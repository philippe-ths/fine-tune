from dotenv import load_dotenv
load_dotenv()

import json
import os
from openai import OpenAI

SYSTEM = (
    "You extract structured JSON. Output MUST be valid JSON only.\n"
    "Return exactly these keys: category, priority, next_action.\n"
    "category must be one of: billing, bug, account, auth, security, outage, data, feature_request, how_to, integration, unknown.\n"
    "priority must be one of: p0, p1, p2, p3.\n"
    "No extra keys. No prose."
)

BASE_MODEL = os.environ.get("BASE_MODEL", "gpt-4.1-nano-2025-04-14")
FT_MODEL = os.environ.get("FT_MODEL", "ft:gpt-4.1-nano-2025-04-14:personal::CxZyZXib")

TEST_INPUTS = [
    "Customer: 'Login keeps failing. Says invalid password but it is correct. Urgent: payroll run today.'",
    "User: 'On Safari the charts are blank but Chrome works.'",
    "Dev: 'We are getting 401s on webhook deliveries since 09:00 UTC. No code changes.'",
    "Customer: 'I’m on a free trial but I was charged yesterday. Not sure if I clicked upgrade.'",
]

ALLOWED_PRIORITIES = {"p0", "p1", "p2", "p3"}
ALLOWED_CATEGORIES = {
    "billing","bug","account","auth","security","outage","data",
    "feature_request","how_to","integration","unknown"
}
REQUIRED_KEYS = {"category", "priority", "next_action"}

def schema_check(text: str) -> str:
    try:
        obj = json.loads(text)
    except Exception as e:
        return f"FAIL (not JSON: {e.__class__.__name__})"
    if not isinstance(obj, dict):
        return "FAIL (JSON is not an object)"
    missing = REQUIRED_KEYS - obj.keys()
    if missing:
        return f"FAIL (missing keys: {sorted(missing)})"
    if obj.get("category") not in ALLOWED_CATEGORIES:
        return f"FAIL (bad category: {obj.get('category')})"
    if obj.get("priority") not in ALLOWED_PRIORITIES:
        return f"FAIL (bad priority: {obj.get('priority')})"
    if not isinstance(obj.get("next_action"), str) or not obj["next_action"].strip():
        return "FAIL (next_action empty/not string)"
    extra = set(obj.keys()) - REQUIRED_KEYS
    if extra:
        return f"PASS (extra keys ignored: {sorted(extra)})"
    return "PASS"

def call_model(client: OpenAI, model: str, user_text: str) -> str:
    resp = client.responses.create(
        model=model,
        temperature=0,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_text},
        ],
    )
    return resp.output_text.strip()

def try_parse_json(text: str) -> str:
    try:
        obj = json.loads(text)
        return f"✅ valid JSON ({type(obj).__name__})"
    except Exception as e:
        return f"❌ invalid JSON ({e.__class__.__name__})"

def main() -> None:
    client = OpenAI()

    for i, t in enumerate(TEST_INPUTS, start=1):
        print("=" * 80)
        print(f"TEST {i}: {t}\n")

        base_out = call_model(client, BASE_MODEL, t)
        ft_out = call_model(client, FT_MODEL, t)

        print("[BASE OUTPUT]")
        print(base_out)
        print("Parse:", try_parse_json(base_out))
        print("Schema:", schema_check(base_out), "\n")

        print("[FINE-TUNED OUTPUT]")
        print(ft_out)
        print("Parse:", try_parse_json(ft_out))
        print("Schema:", schema_check(ft_out))

if __name__ == "__main__":
    main()
