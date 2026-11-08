
import asyncio
import json
import os
import uuid

from dotenv import load_dotenv
from livekit import api

load_dotenv(override=True)

# Only allowed assessment phone number.
TEST_NUMBER = "+18054398008"

# Your Twilio caller ID.
CALLER_NUMBER = "+14842763146"

SCENARIOS = {
    1: "Schedule a routine appointment next week, preferably in the morning.",
    2: "Ask to reschedule an appointment to another weekday.",
    3: "Ask to cancel an upcoming appointment.",
    4: "Request a refill of a routine medication.",
    5: "Ask about the office's opening and closing hours.",
    6: "Ask where the office is located and how to get there.",
    7: "Ask whether the office accepts your insurance.",
    8: "Ask for an appointment but initially give an unclear date.",
    9: "Ask about two different appointment times and compare them.",
    10: "Ask a question, politely interrupt, and clarify your request.",
}


async def make_call(scenario_id=1):

    if scenario_id not in SCENARIOS:
        raise ValueError("Invalid scenario ID")

    # Read LiveKit SIP trunk ID from .env.
    trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID")

    if not trunk_id:
        raise ValueError("LIVEKIT_SIP_TRUNK_ID is missing")

    room_name = f"patient-test-{uuid.uuid4().hex[:8]}"

    lkapi = api.LiveKitAPI()

    try:
        # Start the patient agent.
        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="patient-voice-qa",
                room=room_name,
                metadata=json.dumps({
                    "scenario": SCENARIOS[scenario_id],
                    "scenario_id": scenario_id,
                }),
            )
        )

        print(f"Calling {TEST_NUMBER}...")
        print(f"Scenario: {SCENARIOS[scenario_id]}")

        # Make the actual phone call.
        await lkapi.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=room_name,
                sip_trunk_id=trunk_id,
                sip_call_to=TEST_NUMBER,
                sip_number=CALLER_NUMBER,
                participant_identity="receptionist",
                wait_until_answered=True,
            )
        )

        print("Call answered successfully!")
        print(f"Room: {room_name}")

    except Exception as e:
        print(f"Call failed: {e}")
        raise

    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(make_call(1))
