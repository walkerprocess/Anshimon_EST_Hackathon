# ANSIMON Integrated Care Flow

This is the recommended end-to-end Python snapshot. It validates a care request, creates evidence-grounded guidance, dispatches a Korean AI call, waits for a structured outcome, and forwards the result to the Spring backend.

## Services

| Port | Module | Responsibility |
| ---: | --- | --- |
| `7000` | `server.py` | Care-run API and end-to-end orchestration |
| `8000` | `rag/server.py` | Guidance generation, shelter lookup, and evidence verification |
| `9000` | `voice/server.py` | Call dispatch and outcome reporting |

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python run_all.py
```

In another terminal:

```bash
python run_demo.py --check
python run_demo.py --list
python run_demo.py --file samples/01_high_shelter.json --dry-run
```

Five date-independent scenarios are included under `samples/`: a high-risk Seoul resident with a shelter, a critical case, a non-Seoul case, a minimal-input case, and a no-consent case.

## Test

```bash
python test_connection.py
cd rag
python test_integration.py
```

The tests do not require external APIs. Missing LLM credentials activate a deterministic mock path for the evidence pipeline.

## Care-Run Contract

The backend calls `POST /v1/care-runs` with four structured blocks: `elderly`, `location`, `risk`, and `weather`. The integration layer then:

1. Rejects missing consent or invalid risk, time, or location data.
2. Requests a shelter-aware, evidence-grounded intervention plan from the RAG service.
3. Selects the question categories in code while allowing the LLM to phrase the Korean questions.
4. Dispatches one approved call and waits for its callback.
5. Builds a structured result and posts it to `/internal/v1/contact/results` with an idempotency key.

Call answers use `YES`, `NO`, or `UNKNOWN`. Unknown values are never guessed. Transcript text is not copied into the result payload; only a reference is returned.

## Important Failure Semantics

| Status | Meaning |
| --- | --- |
| `403 CONSENT_REQUIRED` | Consent is absent; no call is placed |
| `400 CONTRACT_VIOLATION` | A required value, range, or time order is invalid |
| `422 GUIDANCE_GENERATION_BLOCKED` | Evidence verification failed; no call is placed |
| `502 RAG_UNAVAILABLE` | The guidance service is unavailable |
| `502 PHONE_UNAVAILABLE` | The voice service is unavailable |

Shelter lookups are limited to configured region prefixes, currently Seoul (`11`). A TMAP failure or a route that requires review is not silently replaced with a confident walking estimate. `risk.score` accepts either a 0-1 value or a percentage and records a warning when normalization is required.

## Key Files

| Path | Role |
| --- | --- |
| `contracts.py` | Input validation, regional rules, and final payload construction |
| `orchestrator.py` | End-to-end care-run flow and callback wait |
| `questions.py` | Deterministic question categories with LLM phrasing |
| `backend_client.py` | Idempotent backend result delivery |
| `rag/` | Integrated RAG and shelter implementation |
| `voice/` | Integrated ClawOps/OpenAI calling implementation |
| `samples/` | Demonstration care-run inputs |

## Safety and Configuration

Use `.env.example` as the complete configuration reference. Keep `.env` untracked. A real call requires ClawOps and OpenAI credentials; the shelter and route path may require Seoul Open Data and TMAP credentials. Use fictional care profiles and consenting team-member phone numbers for demos only.

This English README summarizes the final integrated behavior. The detailed original Korean documentation, including full request and response examples, is preserved in [README.ko.md](README.ko.md).
