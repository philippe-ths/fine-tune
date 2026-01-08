import json
from pathlib import Path

SYSTEM = "You extract structured JSON. Output MUST be valid JSON only."

EXAMPLES = [
    # 1) Billing: duplicate charge (time-sensitive money issue)
    {
        "input": "Billing team: 'Customer got charged twice for December. Invoice shows two transactions. Please refund ASAP.'",
        "output": {"category": "billing", "priority": "p1", "next_action": "verify duplicate charge IDs and initiate refund process"},
    },

    # 2) Bug: reproducible crash with steps (clear engineering handoff)
    {
        "input": "Bug report: 'App crashes when I click Export on iOS 17. Steps: open report > tap Export > crash. Started after last update.'",
        "output": {"category": "bug", "priority": "p1", "next_action": "request device model/app version and reproduce using provided steps"},
    },

    # 3) Account: deletion request (privacy/compliance workflow)
    {
        "input": "Account request: 'Can you delete my account and all data? I no longer want to use the service.'",
        "output": {"category": "account", "priority": "p2", "next_action": "confirm identity and trigger account deletion workflow per policy"},
    },

    # 4) Auth: login failing + business impact (highest urgency)
    {
        "input": "Customer: 'Login keeps failing since yesterday. Urgent — can't access payroll for staff.'",
        "output": {"category": "auth", "priority": "p0", "next_action": "request account email and check auth logs for recent failures"},
    },

    # 5) Security: possible compromise (high severity, different playbook)
    {
        "input": "Customer: 'I think my account was hacked. Password changed and I see logins from Russia.'",
        "output": {"category": "security", "priority": "p0", "next_action": "lock account, verify identity, and review recent login activity for takeover"},
    },

    # 6) Outage/performance: systemic slowness (triage vs single-user)
    {
        "input": "Support: 'Multiple users reporting the dashboard is extremely slow and timing out this morning.'",
        "output": {"category": "outage", "priority": "p0", "next_action": "check service status/metrics and confirm scope (regions, endpoints)"},
    },

    # 7) Data issue: missing records (could be ingestion or permissions)
    {
        "input": "User: 'My sales report is missing yesterday’s transactions. Totals look wrong since Monday.'",
        "output": {"category": "data", "priority": "p1", "next_action": "ask for report name/timezone and check ingestion jobs for missing data"},
    },

    # 8) Feature request: low urgency, needs clarification
    {
        "input": "User: 'Can you add dark mode? Not urgent.'",
        "output": {"category": "feature_request", "priority": "p3", "next_action": "log request and ask for platform (web/iOS/Android) and accessibility needs"},
    },

    # 9) How-to / onboarding: user education, not a bug
    {
        "input": "New user: 'How do I invite my teammate and set their permissions? I'm confused.'",
        "output": {"category": "how_to", "priority": "p3", "next_action": "share invite steps and ask what role/permissions they need"},
    },

    # 10) Payments: card declined (often needs user-side + gateway checks)
    {
        "input": "Customer: 'My card keeps getting declined but it works everywhere else. Please fix now.'",
        "output": {"category": "billing", "priority": "p1", "next_action": "check payment gateway decline code and ask user to confirm billing address/3DS"},
    },

    # 11) Integration/API: webhook failing (technical debugging path)
    {
        "input": "Dev: 'Our webhook endpoint started returning 401s today. We didn't change anything. Requests stopped arriving.'",
        "output": {"category": "integration", "priority": "p1", "next_action": "request webhook URL, timestamps, and verify signing secret/token configuration"},
    },

    # 12) Ambiguous/low info: forces the model to ask for missing details
    {
        "input": "User: 'It doesn't work. Please help.'",
        "output": {"category": "unknown", "priority": "p2", "next_action": "ask what action failed, error message, device/platform, and time it occurred"},
    },

     # 13) Angry auth failure (tone shouldn't change output structure)
    {
        "input": "Customer: 'This is ridiculous — your login is BROKEN. I’ve reset my password 3 times and it still rejects me.'",
        "output": {"category": "auth", "priority": "p1", "next_action": "request account email and exact error message, then check auth logs for repeated failures"},
    },

    # 14) Angry billing dispute (money + urgency)
    {
        "input": "Customer: 'Why the hell did you take £99 from my card?! I never upgraded. Fix it today or I’m cancelling.'",
        "output": {"category": "billing", "priority": "p1", "next_action": "verify subscription change history and charge details, then explain or initiate refund if unauthorized"},
    },

    # 15) Angry + vague (forces clarification instead of guessing)
    {
        "input": "Customer: 'Your app is useless. Nothing works. Sort it out.'",
        "output": {"category": "unknown", "priority": "p2", "next_action": "ask what action failed, any error shown, device/platform, and approximate time of failure"},
    },

    # 16) Multi-issue: billing + login (choose primary and triage)
    {
        "input": "Support: 'User can’t log in and also says they were charged twice this month.'",
        "output": {"category": "auth", "priority": "p1", "next_action": "restore account access first (confirm email/error), then verify billing ledger for duplicate charges"},
    },

    # 17) Multi-issue: outage symptoms + specific feature broken
    {
        "input": "Ops: 'Some customers report timeouts, and Export is failing with 502 errors on web.'",
        "output": {"category": "outage", "priority": "p0", "next_action": "check service metrics for 5xx spikes and confirm affected endpoints/regions, then update status page"},
    },

    # 18) Multi-issue: data missing + permissions question
    {
        "input": "User: 'Yesterday’s numbers are missing AND I can’t see the admin page anymore. Did you change my access?'",
        "output": {"category": "data", "priority": "p1", "next_action": "ask which report/timezone is impacted and check ingestion jobs, then verify the user’s role/permissions"},
    },

    # 19) Contradictory: “charged” but “free trial” claim
    {
        "input": "Customer: 'I’m on a free trial but I was charged yesterday. Also I might have clicked upgrade, not sure.'",
        "output": {"category": "billing", "priority": "p2", "next_action": "confirm account email and plan status, then check trial/upgrade events and charge timestamp"},
    },

    # 20) Contradictory: “can log in” but “locked out”
    {
        "input": "User: 'I can log in on my phone but desktop says I’m locked out. Password is correct.'",
        "output": {"category": "auth", "priority": "p2", "next_action": "ask for desktop browser details and exact error, then check MFA/session policies and account lock events"},
    },

    # 21) Unclear timeline (forces asking for time + scope)
    {
        "input": "Support: 'Reports are sometimes wrong. It’s been happening for a while.'",
        "output": {"category": "data", "priority": "p2", "next_action": "ask which reports/metrics are wrong, date range affected, and timezone, then compare against source events"},
    },

    # 22) Security-ish: suspicious email (not confirmed breach)
    {
        "input": "Customer: 'I received an email asking me to reset my password. Is that from you? It looks sketchy.'",
        "output": {"category": "security", "priority": "p1", "next_action": "ask for email headers/screenshot and verify sending domain, then advise not to click links and use official reset flow"},
    },

    # 23) Security-ish: unusual login alert but user traveling
    {
        "input": "User: 'I got a “new login from Germany” alert but I’m actually in Berlin this week. Should I worry?'",
        "output": {"category": "security", "priority": "p2", "next_action": "confirm recent logins match user activity and recommend MFA if not enabled"},
    },

    # 24) Security-ish: API key leak suspicion
    {
        "input": "Dev: 'I think we accidentally committed an API key to GitHub. What should we do right now?'",
        "output": {"category": "security", "priority": "p0", "next_action": "revoke/rotate the key immediately and audit recent usage for suspicious activity"},
    },

    # 25) Platform-specific: Android notification issue
    {
        "input": "User: 'Android app: I stopped receiving notifications after updating to Android 14.'",
        "output": {"category": "bug", "priority": "p2", "next_action": "ask for device model/app version and check notification permissions and OS battery optimization settings"},
    },

    # 26) Platform-specific: Safari-only bug
    {
        "input": "User: 'On Safari, the dashboard loads but charts are blank. Works fine in Chrome.'",
        "output": {"category": "bug", "priority": "p2", "next_action": "request Safari version/macOS version and console errors, then reproduce in Safari"},
    },

    # 27) Platform-specific: iOS upload failure on cellular
    {
        "input": "User: 'iPhone: file uploads fail on mobile data but work on Wi-Fi.'",
        "output": {"category": "bug", "priority": "p2", "next_action": "ask for iOS/app version and file size, then check network timeouts and cellular data permissions"},
    },

    # 28) Integration: webhook 400 with payload details (debugging checklist)
    {
        "input": "Dev: 'Webhook deliveries started failing with 400. Our endpoint says “invalid signature”. Last good delivery was 09:12 UTC.'",
        "output": {"category": "integration", "priority": "p1", "next_action": "confirm signing secret and compare signature algorithm/logs around 09:12 UTC"},
    },

    # 29) Integration: OAuth token expiry / 401s (common cause)
    {
        "input": "Dev: 'Our API calls are returning 401 Unauthorized since this morning. We use OAuth. No code changes.'",
        "output": {"category": "integration", "priority": "p1", "next_action": "check token expiry/refresh flow and request timestamps/request IDs to correlate with auth logs"},
    },

    # 30) Integration: rate limiting (429) + needs backoff guidance
    {
        "input": "Dev: 'We’re getting 429 Too Many Requests intermittently during peak hours. Any suggestions?'",
        "output": {"category": "integration", "priority": "p2", "next_action": "confirm current request rate and recommend exponential backoff, batching, and checking rate limit headers"},
    },
]

def to_jsonl_line(example: dict) -> str:
    obj = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": json.dumps(example["output"], ensure_ascii=False)},
        ]
    }
    return json.dumps(obj, ensure_ascii=False)

def main() -> None:
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "train.jsonl"

    lines = [to_jsonl_line(ex) for ex in EXAMPLES]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} examples to {out_path}")

if __name__ == "__main__":
    main()
