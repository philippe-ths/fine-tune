from dotenv import load_dotenv
load_dotenv()

import json
from pathlib import Path
from openai import OpenAI

SYSTEM = (
    "You extract structured JSON. Output MUST be valid JSON only.\n"
    "Return exactly these keys: category, priority, next_action.\n"
    "category must be one of: billing, bug, account, auth, security, outage, data, feature_request, how_to, integration, unknown.\n"
    "priority must be one of: p0, p1, p2, p3.\n"
    "No extra keys. No prose."
)

BASE_MODEL = "gpt-4.1-nano-2025-04-14"
FT_MODEL = "ft:gpt-4.1-nano-2025-04-14:personal::CxauVJbP"

TEST_PATH = Path("data/test_cases.json")

def call(client: OpenAI, model: str, text: str) -> dict:
    r = client.responses.create(
        model=model,
        temperature=0,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
    )
    return json.loads(r.output_text)

def score_case(pred: dict, expected: dict) -> tuple[bool, list[str]]:
    problems = []
    for k, v in expected.items():
        if pred.get(k) != v:
            problems.append(f"{k}: expected {v!r}, got {pred.get(k)!r}")
    return (len(problems) == 0), problems

def main() -> None:
    cases = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    client = OpenAI()

    for model in [BASE_MODEL, FT_MODEL]:
        print("=" * 80)
        print("MODEL:", model)
        passed = 0

        for c in cases:
            pred = call(client, model, c["input"])
            ok, problems = score_case(pred, c["expected"])
            status = "PASS" if ok else "FAIL"
            print(f"{status} - {c['name']}")
            if not ok:
                for p in problems:
                    print("  -", p)
            else:
                passed += 1

        print(f"Score: {passed}/{len(cases)}")

if __name__ == "__main__":
    main()
