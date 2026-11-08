
import json
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, AgentServer, JobContext, cli

from livekit.plugins import deepgram, openai, cartesia, silero

load_dotenv(override=True)


# STEP 1: Define the patient.
class PatientAgent(Agent):
    def __init__(self, scenario):
        super().__init__(
            instructions=f"""
            You are Sarah Miller, a patient calling a doctor's office.

            Your goal: {scenario}

            Follow these rules:
            - Speak naturally, like a real patient.
            - Keep responses short and friendly.
            - Listen carefully before answering.
            - Answer the receptionist's questions.
            - Ask for clarification when necessary.
            - Do not invent appointment confirmations.
            - Use only fictional patient information.
            - Stay focused on your goal.
            - Thank the receptionist before ending the call.
            """
        )


# STEP 2: Create the LiveKit server.
server = AgentServer()


# STEP 3: Save the session report after each call.
async def save_report(ctx: JobContext):
    Path("reports").mkdir(exist_ok=True)

    report = ctx.make_session_report()
    filename = Path("reports") / f"{ctx.room.name}.json"

    filename.write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )

    print(f"Session report saved: {filename}")


# STEP 4: Run the patient agent.
@server.rtc_session(
    agent_name="patient-voice-qa",
    on_session_end=save_report,
)
async def main(ctx: JobContext):

    # Read the scenario passed from call.py.
    data = json.loads(ctx.job.metadata or "{}")

    scenario = data.get(
        "scenario",
        "Schedule a routine appointment next week in the morning.",
    )

    # Connect to the room.
    await ctx.connect()

    # Wait for the receptionist's phone connection.
    await ctx.wait_for_participant(identity="receptionist")

    # Create our speech → AI → speech pipeline.
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    # Start the patient conversation and enable recording.
    await session.start(
        agent=PatientAgent(scenario),
        room=ctx.room,
        record=True,
    )


# STEP 5: Run the application.
if __name__ == "__main__":
    cli.run_app(server)
