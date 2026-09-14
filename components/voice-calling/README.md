# ANSIMON Voice Calling

Places a Korean AI preventive-care call when ANSIMON has an approved heat-risk intervention plan.

This component owns the communication channel only. The Spring backend decides who may be called, when a call is allowed, which guidance is approved, and what follow-up work is created.

## Providers

- **ClawOps** supplies the registered Korean 070 calling number.
- **OpenAI Realtime** supplies speech-to-speech Korean conversation.

A real call requires `CLAWOPS_API_KEY`, `CLAWOPS_ACCOUNT_ID`, and `OPENAI_API_KEY`. Optional values include `CLAWOPS_FROM_NUMBER`, `ANSIMON_BACKEND_BASE_URL`, and `SOCIAL_WORKER_PHONE`. Copy these names from the integrated component's `.env.example` and never commit populated credentials.

## Install and Run

```bash
pip install "clawops[agent,openai]"
python scripts/provision_number.py --create
python voice/call.py 01012345678
```

Use a consenting team member's number for demos. Never test with an older adult's real personal information.

## Responsibility Boundary

The backend verifies consent and calling hours, chooses the target, calculates risk and shelter information, creates the contact job, enforces idempotency, stores results, and schedules any business retry. This module reads one approved plan, places one call, asks the supplied questions in order, and returns a structured outcome.

Outcome fields use explicit enums:

- `contactStatus`: `ANSWERED`, `NO_ANSWER`, or `FAILED`
- `shelterIntent`, `canMoveAlone`, `helpNeeded`, and `symptomMentioned`: `YES`, `NO`, or `UNKNOWN`

Unclear or unanswered questions remain `UNKNOWN`. The calling module does not diagnose, choose a different shelter, decide whom to call, or independently schedule a second attempt.

## Safety

- Identify the caller as AI and explain the call purpose in the opening sentence.
- Keep call recording disabled for the prototype.
- Mask phone numbers in logs except for the last four digits.
- Escalate symptoms for human review; do not claim medical authority or automatically contact emergency services.
- Use only a registered outbound number that the operator is authorized to use.

For original project notes, see [README.ko.md](README.ko.md). The newer integrated voice snapshot is under [`../integration/voice`](../integration/voice).
