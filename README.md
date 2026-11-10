# Patient Voice QA Bot

A Python voice-testing project that places outbound calls to an authorized medical-office AI test line. A LiveKit agent plays a fictional patient, holds a natural conversation with the receptionist, and captures evidence to review conversational quality, workflow issues, and edge cases.

> **Test-only project.** Calls are restricted to the assessment's authorized number, **+1-805-439-8008**. Use fictional patient details; do not enter real medical or identity information. API and telephone usage may incur charges.

## Features

- Python + LiveKit Agents with a **pipeline architecture** (independent speech-to-text, language model, and text-to-speech services; not a realtime speech-to-speech model).
- Outbound calls through a LiveKit SIP trunk and configured Twilio caller ID.
- Ten patient scenarios, including appointment scheduling, rescheduling, cancellation, refills, office information, insurance, and conversational edge cases.
- Session evidence for each call, with JSON session reports and (in the **updated** `agent.py`) readable transcripts and MP3 recordings created through FFmpeg.
- A one-terminal launcher (`run.py`). The **updated** `run.py`/`call.py` versions support sequential scenario execution.

## Architecture

`run.py` starts the LiveKit agent worker, then invokes `call.py` to place a call using the configured outbound SIP trunk. `call.py` creates a unique LiveKit room and dispatches `patient-voice-qa` with scenario metadata. Once the called receptionist joins the room, `agent.py` starts a fictional patient agent. Speech is transcribed by **Deepgram**, processed by **OpenAI `gpt-4o-mini`**, and spoken using **Cartesia**, with **Silero VAD** assisting turn detection. This separate-component pipeline follows the challenge's technical requirements.

The LiveKit session report preserves the conversation history and usage information. The updated session-end handler writes a JSON report, generates a human-readable transcript identifying Patient and Receptionist, and converts the recorded audio to MP3 via FFmpeg (retaining the original recording on conversion failure when possible). Session recordings and transcripts can be reviewed for booking accuracy, identity-verification friction, latency, interruptions, and unexpected transfer behavior. A transcript alone is not proof of a backend booking or a confirmed product bug.

## Project structure

```text
patient-voice-qa/
├── agent.py               # Patient agent, voice pipeline, session evidence
├── call.py                # SIP calling and 10 patient scenarios
├── run.py                 # Single-terminal launcher
├── .env                   # Local secrets (do not commit)
├── .env.example           # Environment variable names (recommended)
├── README.md
└── reports/               # Per-call evidence (created at runtime)
    ├── patient-test-<id>.json
    ├── patient-test-<id>.txt
    └── patient-test-<id>.mp3
```

The `*.txt` and `*.mp3` outputs require the revised `save_report()` implementation; the original uploaded `agent.py` saves **JSON only**.

## Prerequisites

- Python 3.11+ in a virtual environment compatible with your installed LiveKit SDK
- A configured LiveKit Cloud project and an **outbound** SIP trunk capable of calling the authorized test number
- A configured Twilio telephone number used consistently as the caller ID
- API credentials for Deepgram, OpenAI, and Cartesia
- **FFmpeg** available on `PATH` for MP3 conversion
- Windows PowerShell (commands below); other shells can be used with adjusted activation commands

## Setup (Windows PowerShell)

From the project folder, create and activate a virtual environment if one does not already exist:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required dependencies:

```powershell
python -m pip install "livekit-agents[deepgram,openai,cartesia,silero]" livekit-api python-dotenv
```

If your project already has a working pinned dependency/lock file, install from that instead to avoid unintentional upgrades.

Install FFmpeg if needed:

```powershell
winget install --id Gyan.FFmpeg -e
```

Close and reopen PowerShell after installation, then verify:

```powershell
ffmpeg -version
python -c "from livekit.agents import Agent, AgentSession, AgentServer; print('LiveKit import OK')"
```

Create a local `.env` file with **your own secrets**, following this example:

```dotenv
LIVEKIT_URL=wss://YOUR_PROJECT.livekit.cloud
LIVEKIT_API_KEY=YOUR_LIVEKIT_API_KEY
LIVEKIT_API_SECRET=YOUR_LIVEKIT_API_SECRET
LIVEKIT_SIP_TRUNK_ID=ST_YOUR_OUTBOUND_TRUNK_ID
DEEPGRAM_API_KEY=YOUR_DEEPGRAM_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
CARTESIA_API_KEY=YOUR_CARTESIA_API_KEY
```

The caller ID and assessment number are configured in `call.py`. Keep the assessment destination restricted to `+18054398008` and use **one consistent authorized caller ID** across all assessment calls. Never commit `.env`, API keys, or real patient information.

## Run

### One-terminal run

With the virtual environment activated:

```powershell
python run.py
```

In the **original uploaded** launcher, this starts the worker and places **Scenario 1 only**; press `Ctrl+C` after the conversation ends to stop the worker.

If you have applied the **updated** sequential `call.py` and `run.py` from the project walkthrough, you can also use:

```powershell
python run.py --scenario 5
python run.py --all
```

The first runs Scenario 5; the second makes ten outbound calls **one at a time**, waiting for each call's files before proceeding. **Those options do not exist in the original uploaded `run.py`.** Test one scenario before running all ten. Do not assume a call counts toward the submission until its audio, transcript, and conversational quality are checked.

### Run the agent manually (diagnostics)

```powershell
python agent.py dev
```

This starts the worker without initiating a phone call. Stop it with `Ctrl+C` when finished.

## Test scenarios

| ID | Patient goal |
|---:|---|
| 1 | Schedule a routine appointment next week, preferably in the morning |
| 2 | Reschedule an appointment to another weekday |
| 3 | Cancel an upcoming appointment |
| 4 | Request a routine medication refill |
| 5 | Ask about opening and closing hours |
| 6 | Ask for the office location and directions |
| 7 | Ask whether the clinic accepts an insurance provider |
| 8 | Request an appointment with an initially unclear date |
| 9 | Compare two appointment times |
| 10 | Clarify a request and test polite interruptions |

## Reports and quality review

Each run uses a unique `patient-test-<id>` room identifier. In the revised evidence-saving implementation, the matching files in `reports/` are:

- **`.json`** — full LiveKit session report and conversation events
- **`.txt`** — readable conversation, labeled Patient and Receptionist
- **`.mp3`** — call recording converted from the session's recorded audio using FFmpeg

After each call, play the recording and check that **both voices** can be heard and the conversation is reasonably complete. Verify timestamps against the recording when filing a bug. Distinguish actual receptionist behavior from speech-to-text errors, caller-agent errors, and intentional restrictions of the assessment test line. A statement that an appointment was scheduled or canceled is not independent verification of a backend state change.

A useful issue report includes: **scenario, severity, observation, expected behavior, actual behavior, transcript line or audio timestamp, impact, and validation status**. Report confirmed defects separately from suspected or environment-dependent issues.

## Troubleshooting

| Problem | What to check |
|---|---|
| `ModuleNotFoundError: No module named 'livekit'` | Activate `.venv` and install dependencies into the same Python interpreter used by `run.py`. |
| `LIVEKIT_SIP_TRUNK_ID is missing` | Confirm `.env` contains the outbound SIP trunk ID and is being loaded from the project directory. |
| Agent fails to start | Check LiveKit URL/API credentials, installed SDK version, and terminal error messages. |
| Outbound call fails | Verify SIP trunk configuration, Twilio caller ID, account permissions, and the authorized destination number. |
| No MP3 produced | Verify the updated `save_report()` is installed, `record=True` is enabled, `ffmpeg -version` works, and an audio recording path exists in the JSON report. |
| Audio won't preview inside VS Code | Open the file in a media player; editor text preview does not indicate an invalid audio file. |
| Transcript and audio disagree | Listen to the original audio before calling the difference a receptionist defect. |

## Submission checklist

The challenge requires a **private GitHub repository** containing the working code, a setup README, a short architecture explanation, at least **10 complete call transcripts plus OGG/MP3 recordings**, and a clearly evidenced bug report. It also requires **two Loom videos**: a webcam-enabled project walkthrough (maximum 3 minutes) and a screen recording showing AI-assisted debugging and iteration. Keep the repository private, invite the reviewer using the address provided in the challenge instructions, and submit the form with the repository/video links and the single caller number used for all tests. Do not put the assessment organization's name or abbreviation in the repository name, description, or README title, and do not mention it in the Loom walkthrough.

## Security and limitations

This project is a **test caller**, not a clinical service. It must not provide medical advice, invent confirmed appointments, expose credentials, or send calls to numbers other than the assessment-authorized destination. The example configuration contains placeholders; access to external telephony, LiveKit, and model services must be configured separately. Logs and recordings may contain personal information if supplied during testing, so keep sensitive artifacts private.
