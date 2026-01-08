import json
from pathlib import Path


def is_valid_json(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def main() -> None:
    path = Path("data/train.jsonl")
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}. Run scripts/make_dataset.py first.")

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("train.jsonl is empty")

    errors: list[str] = []
    for i, line in enumerate(lines, start=1):
        # 1) Each line must be valid JSON
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"Line {i}: invalid JSONL outer object: {e}")
            continue

        # 2) Must contain messages list
        messages = obj.get("messages")
        if not isinstance(messages, list) or len(messages) < 3:
            errors.append(f"Line {i}: 'messages' must be a list with at least 3 items")
            continue

        # 3) Check roles order (simple expectation)
        roles = [m.get("role") for m in messages[:3]]
        if roles != ["system", "user", "assistant"]:
            errors.append(f"Line {i}: expected roles [system,user,assistant], got {roles}")

        # 4) Assistant content should be JSON text (for our project)
        assistant_content = messages[2].get("content", "")
        if not isinstance(assistant_content, str) or not assistant_content.strip():
            errors.append(f"Line {i}: assistant content missing/empty")
        elif not is_valid_json(assistant_content):
            errors.append(f"Line {i}: assistant content is not valid JSON: {assistant_content}")

    if errors:
        print("FAIL ❌ Dataset has issues:")
        for e in errors:
            print("-", e)
        raise SystemExit(1)

    print(f"PASS ✅ {len(lines)} examples validated in {path}")


if __name__ == "__main__":
    main()
