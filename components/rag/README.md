# ANSIMON Evidence-Grounded Guidance

This standalone component implements document ingestion, retrieval, prompt construction, typed output schemas, shelter validation, and evidence verification for ANSIMON's preventive heatwave guidance.

## Data Notice

`data/heat_illness_manual.pdf` is a team-authored stand-in that mirrors the structure of the intended Korean heat-illness prevention manual. It is not a downloaded copy of the official KDCA publication. Replace it with a validated source document and rerun `ingest.py` before any real-world use. The shelter CSVs under `fixtures/` are also examples rather than production data.

## Pipeline

1. `ingest.py` extracts metadata and creates semantic chunks.
2. `retrieval.py` ranks audience-filtered chunks with character n-gram TF-IDF and cosine similarity.
3. `prompt_builder.py` separates structured care context from retrieved evidence and requires JSON-only output.
4. `schemas.py` enforces typed risk, plan, shelter, and call-result contracts with Pydantic.
5. `evidence_verifier.py` rejects missing or fabricated chunk references, altered emergency wording, and unverified shelters.
6. `pipeline.py` exposes the complete guidance-generation entry point.

## Install and Run

Keep all Python files and the `data`, `fixtures`, and `out` directories together.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -X utf8 ingest.py
python -X utf8 retrieval.py
python -X utf8 prompt_builder.py
python -X utf8 evidence_verifier.py
python -X utf8 pipeline.py
```

Without LLM credentials, the pipeline uses a deterministic generator built from retrieved evidence, so the complete retrieval-to-verification path remains testable offline.

## API

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

- `GET /health` reports service health.
- `POST /v1/intervention-plans` accepts `elderlyId`, `riskSnapshotId`, `elderlyProfile`, `riskSnapshot`, `shelter`, and `weather`.
- `200` returns the intervention plan.
- `422 GUIDANCE_GENERATION_BLOCKED` means evidence verification failed and calling must stop.
- `503` means the RAG store has not been prepared, usually because `out/chunks.jsonl` is missing.

## Test

```bash
python -X utf8 test_integration.py
```

The original detailed Korean documentation is preserved in [README.ko.md](README.ko.md). The integrated, newer snapshot used by the complete care flow is under [`../integration/rag`](../integration/rag).
