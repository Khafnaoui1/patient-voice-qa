
import json
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, AgentServer, JobContext, cli
from livekit.plugins import deepgram, openai, cartesia, silero


# Load environment variables.
load_dotenv(override=True)


# STEP 1: Define the patient.
class PatientAgent(Agent):

    def __init__(self, scenario):
        super().__init__(
            instructions=f"""
            You are Khaled Hafnaoui, a fictional patient
            calling a doctor's office.

            Your goal: {scenario}

            Rules:
            - Speak naturally and keep answers short.
            - Let the receptionist greet you first.
            - Explain why you are calling.
            - Answer questions one at a time.
            - Ask follow-up questions when useful.
            - Do not interrupt unless testing interruptions.
            - Do not invent appointment confirmations.
            - Use only fictional patient information.
            - Stay focused on your scenario.
            - Finish the conversation naturally.
            - Thank the receptionist before ending.
            """
        )


# STEP 2: Create the LiveKit server.
server = AgentServer()


# STEP 3: Save the session report, transcript, and MP3.
async def save_report(ctx: JobContext):

    folder = Path("reports")
    folder.mkdir(exist_ok=True)

    report = ctx.make_session_report()
    data = report.to_dict()
    name = ctx.room.name

    # 1. Save JSON report.
    json_file = folder / f"{name}.json"

    json_file.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    print(f"JSON report saved: {json_file}")

    # 2. Save readable transcript.
    lines = []

    for item in data.get("chat_history", {}).get("items", []):

        if item.get("type") != "message":
            continue

        role = item.get("role")

        if role == "assistant":
            speaker = "Patient"
        elif role == "user":
            speaker = "Receptionist"
        else:
            continue

        content = item.get("content", [])

        message = " ".join(
            part for part in content
            if isinstance(part, str)
        )

        if message.strip():
            lines.append(f"{speaker}: {message}")

    transcript_file = folder / f"{name}.txt"

    transcript_file.write_text(
        "\n\n".join(lines),
        encoding="utf-8",
    )

    print(f"Transcript saved: {transcript_file}")

    # 3. Convert the recording to MP3.
    audio_path = data.get("audio_recording_path")

    if audio_path and Path(audio_path).is_file():

        mp3_file = folder / f"{name}.mp3"

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", str(audio_path),
                    "-codec:a", "libmp3lame",
                    "-qscale:a", "2",
                    str(mp3_file),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            print(f"MP3 recording saved: {mp3_file}")

        except (subprocess.CalledProcessError, FileNotFoundError) as e:

            # Preserve the original audio if conversion fails.
            source = Path(audio_path)
            backup_file = folder / f"{name}{source.suffix}"

            shutil.copy2(source, backup_file)

            print(f"MP3 conversion failed: {e}")
            print(f"Original recording saved: {backup_file}")

    else:
        print("Audio recording not found. Check LiveKit Agent insights.")

    print(f"Session completed: {name}")


# STEP 4: Run the patient agent.
@server.rtc_session(
    agent_name="patient-voice-qa",
    on_session_end=save_report,
)
async def main(ctx: JobContext):

    # Read the scenario from call.py.
    data = json.loads(ctx.job.metadata or "{}")

    scenario = data.get(
        "scenario",
        "Schedule a routine appointment next week in the morning.",
    )

    # Connect to the LiveKit room.
    await ctx.connect()

    # Wait for the receptionist to join.
    await ctx.wait_for_participant(identity="receptionist")

    # Create the speech -> LLM -> speech pipeline.
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    # Start the patient conversation and record audio.
    await session.start(
        agent=PatientAgent(scenario),
        room=ctx.room,
        record=True,
    )


# STEP 5: Run the application.
if __name__ == "__main__":
    cli.run_app(server)
