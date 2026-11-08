
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from livekit import api

load_dotenv(override=True)


# Assessment phone number.
TEST_NUMBER = "+18054398008"

# Your existing Twilio caller ID.
CALLER_NUMBER = "+14842763146"


# Ten patient scenarios.
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


# Wait until the phone conversation ends.
async def wait_for_call_end(lkapi, room_name):

    while True:
        await asyncio.sleep(2)

        try:
            result = await lkapi.room.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )

            # The receptionist is the SIP participant.
            connected = any(
                p.identity == "receptionist"
                for p in result.participants
            )

            if not connected:
                print("Receptionist disconnected.")
                return

        except Exception as e:
            # The room may already be closed.
            print(f"Room status unavailable: {e}")
            raise


# Wait for agent.py to finish saving the files.
async def wait_for_report(room_name):

    folder = Path("reports")

    json_file = folder / f"{room_name}.json"
    txt_file = folder / f"{room_name}.txt"
    mp3_file = folder / f"{room_name}.mp3"

    for _ in range(60):
        if (
            json_file.is_file()
            and txt_file.is_file()
            and mp3_file.is_file()
            and txt_file.stat().st_size > 0
            and mp3_file.stat().st_size > 1000
        ):
            print("JSON, transcript, and MP3 saved.")
            return

        await asyncio.sleep(1)

    raise RuntimeError(
        f"Report files are missing or incomplete for {room_name}"
    )


# Place one patient phone call.
async def make_call(scenario_id=1):

    if scenario_id not in SCENARIOS:
        raise ValueError("Invalid scenario ID")

    trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID")

    if not trunk_id:
        raise ValueError("LIVEKIT_SIP_TRUNK_ID is missing")

    room_name = f"patient-test-{uuid.uuid4().hex[:8]}"

    lkapi = api.LiveKitAPI()

    try:
        print(f"\nScenario {scenario_id}: {SCENARIOS[scenario_id]}")
        print(f"Calling {TEST_NUMBER}...")

        # Start the patient agent with the scenario.
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

        # Make the phone call.
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

        print("Call answered. Conversation started.")

        # Allow up to 4 minutes for the conversation.
        try:
            await asyncio.wait_for(
                wait_for_call_end(lkapi, room_name),
                timeout=240,
            )

        except asyncio.TimeoutError:
            print("Call exceeded 4 minutes. Ending call.")

            await lkapi.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )

            raise RuntimeError("Call timed out")

        # Wait for transcript and recording.
        await wait_for_report(room_name)

        print(f"Scenario {scenario_id} completed.")
        print(f"Room: {room_name}")

    finally:
        await lkapi.aclose()


# Run a single scenario from the command line.
if __name__ == "__main__":

    scenario_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    asyncio.run(make_call(scenario_id))
