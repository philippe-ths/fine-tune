import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

TRAIN_PATH = "data/train.jsonl"
MODEL = "gpt-4.1-nano-2025-04-14"  # small + cheap for practice


def main() -> None:
    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError(f"Missing {TRAIN_PATH}. Run scripts/make_dataset.py first.")

    client = OpenAI()

    # Upload training file
    with open(TRAIN_PATH, "rb") as f:
        train_file = client.files.create(file=f, purpose="fine-tune")

    # Create fine-tuning job
    job = client.fine_tuning.jobs.create(
        training_file=train_file.id,
        model=MODEL,
    )

    print("Fine-tuning job created.")
    print("Job ID:", job.id)
    print("Model:", MODEL)


if __name__ == "__main__":
    main()
