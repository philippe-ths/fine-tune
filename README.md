# Fine-tune

Fine-tuning OpenAI’s GPT-4.1-nano for support ticket classification. Generates training data, runs fine-tuning jobs, and evaluates the fine-tuned model against baseline using golden test cases.

Tickets are classified by **category** (billing, bug, outage, auth, etc.), **priority** (P0–P3), and **next action**.

## Prerequisites

- Python 3.11+
- OpenAI API key with fine-tuning permissions

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/make_dataset.py` | Generate JSONL training data (31 examples) |
| `scripts/eval_json.py` | Validate training data against schema rules |
| `scripts/run_finetune.py` | Upload training file and launch fine-tuning job |
| `scripts/check_finetune.py` | Check fine-tuning job status and events |
| `scripts/compare_models.py` | Compare base vs fine-tuned model outputs |
| `scripts/run_golden_eval.py` | Score both models against golden test cases |

## Workflow

1. `make_dataset.py` — generate `data/train.jsonl`
2. `eval_json.py` — validate the training data
3. `run_finetune.py` — upload and start fine-tuning
4. `check_finetune.py` — poll until training completes
5. `compare_models.py` / `run_golden_eval.py` — evaluate results