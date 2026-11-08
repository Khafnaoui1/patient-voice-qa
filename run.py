
import argparse
import subprocess
import sys
import time


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all 10 scenarios",
    )

    parser.add_argument(
        "--scenario",
        type=int,
        default=1,
        help="Scenario number (1-10)",
    )

    args = parser.parse_args()

    agent = None

    try:
        # STEP 1: Start LiveKit agent.
        print("Starting LiveKit agent...")

        agent = subprocess.Popen(
            [sys.executable, "agent.py", "dev"]
        )

        # Give the agent time to register.
        time.sleep(10)

        if agent.poll() is not None:
            raise RuntimeError("LiveKit agent failed to start.")

        # STEP 2: Select scenarios.
        if args.all:
            scenarios = range(1, 11)
        else:
            scenarios = [args.scenario]

        # STEP 3: Run calls one at a time.
        for scenario_id in scenarios:

            print("\n" + "=" * 45)
            print(f"STARTING SCENARIO {scenario_id}")
            print("=" * 45)

            subprocess.run(
                [
                    sys.executable,
                    "call.py",
                    str(scenario_id),
                ],
                check=True,
            )

            print(f"Scenario {scenario_id} finished.")

            # Short pause before the next call.
            if scenario_id != scenarios[-1]:
                time.sleep(5)

        print("\nAll selected scenarios completed.")

    except KeyboardInterrupt:
        print("\nStopped by user.")

    except Exception as e:
        print(f"\nError: {e}")
        print("Remaining scenarios were not started.")

    finally:
        # Stop LiveKit agent.
        if agent and agent.poll() is None:
            print("Stopping LiveKit agent...")
            agent.terminate()
            agent.wait()


if __name__ == "__main__":
    main()
