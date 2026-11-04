
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    cli,
)

from livekit.plugins import (
    deepgram,
    openai,
    cartesia,
    silero,
)


# STEP 1: Load API keys from the .env file.
load_dotenv()


# STEP 2: Create our AI patient.
class PatientAgent(Agent):

    def __init__(self):
        super().__init__(
            instructions="""
            You are Sarah Miller, a patient calling a doctor's office.

            Your goal is to schedule a routine appointment
            next week, preferably in the morning.

            Follow these rules:
            - Speak naturally, like a real person.
            - Keep responses short and friendly.
            - Answer the receptionist's questions.
            - Ask for clarification when necessary.
            - Do not invent appointment confirmations.
            - Do not provide real sensitive patient information.
            - Thank the receptionist before ending the call.
            """
        )


# STEP 3: Create our LiveKit server.
server = AgentServer()


# STEP 4: Define what happens when a conversation starts.
@server.rtc_session(agent_name="patient-voice-qa")
async def main(ctx: JobContext):

    # Create our speech → AI → speech pipeline.
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    # Start the conversation session.
    await session.start(
        agent=PatientAgent(),
        room=ctx.room,
    )

    # Connect to the LiveKit room.
    await ctx.connect()


# STEP 5: Run the application.
if __name__ == "__main__":
    cli.run_app(server)
