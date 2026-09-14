# Integrated RAG Module

The `integration/rag` directory is the RAG snapshot wired into the complete ANSIMON care-run flow. It covers document ingestion and chunking, retrieval, prompt construction, output schemas, shelter enrichment, and evidence verification.

## Important Data Notice

`rag/data/heat_illness_manual.pdf` is a team-authored stand-in that mirrors the intended document structure. It is not an official KDCA file. The fixture shelter CSVs are also examples. Replace both with validated current sources before real-world use.

## Run Individually

Install the parent integration requirements, then run commands from the `rag` directory:

```bash
cd components/integration
pip install -r requirements.txt
cd rag

python -X utf8 ingest.py
python -X utf8 retrieval.py
python -X utf8 prompt_builder.py
python -X utf8 evidence_verifier.py
python -X utf8 pipeline.py
python -X utf8 test_integration.py
```

Start the API with:

```bash
python -m uvicorn server:app --port 8000
```

## Main Modules

| File | Responsibility |
| --- | --- |
| `ingest.py` | Parse source metadata and build semantic chunks |
| `retrieval.py` | Audience-aware TF-IDF retrieval |
| `prompt_builder.py` | Build compact evidence-constrained prompts |
| `schemas.py` | Enforce typed request and response contracts |
| `shelter_client.py` | Fetch and rank configured shelter data |
| `shelter_reference.py` | Verify shelter existence against loaded reference data |
| `evidence_verifier.py` | Block unsupported claims, altered emergency text, and unverified shelters |
| `pipeline.py` | Generate a verified intervention plan |
| `server.py` | Expose the plan generator over FastAPI |

If no external LLM credential is configured, the module uses a deterministic evidence-based fallback for local tests. A verification error must stop the call rather than being retried as a transient service failure.

The complete original Korean documentation is preserved in [RAG_README.ko.md](RAG_README.ko.md).
