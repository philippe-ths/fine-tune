from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

JOB_ID = os.environ.get("FT_JOB_ID", "ftjob-7RppO6EqSTdp1CVWREreAko0")

def main() -> None:
    client = OpenAI()
    job = client.fine_tuning.jobs.retrieve(JOB_ID)

    print("Job:", job.id)
    print("Status:", job.status)
    # When finished, OpenAI returns the fine-tuned model name here:
    print("Fine-tuned model:", getattr(job, "fine_tuned_model", None))

    # Optional: show recent events if available
    events = client.fine_tuning.jobs.list_events(JOB_ID, limit=10)
    for e in events.data[::-1]:
        print(f"- {e.created_at}: {e.level} {e.message}")

if __name__ == "__main__":
    main()
