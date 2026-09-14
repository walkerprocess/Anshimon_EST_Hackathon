# Source Repositories

This monorepo was assembled on September 13, 2026 from the public repositories owned by the [N-M-D-W GitHub organization](https://github.com/N-M-D-W). Files were copied from the exact revisions below without importing nested Git metadata. All remote branches were audited in addition to each repository's default branch.

| Original repository | Consolidated path | Source revision | Original commits |
| --- | --- | --- | ---: |
| [`ansimon_backend`](https://github.com/N-M-D-W/ansimon_backend) | [`components/backend`](../components/backend) | [`5b26f62`](https://github.com/N-M-D-W/ansimon_backend/commit/5b26f620db02867bd416cf5394e31096228f5aef) on `feat/risk-ml-and-connection-integration` | 62 |
| [`ansimon_front_end`](https://github.com/N-M-D-W/ansimon_front_end) | [`components/dashboard`](../components/dashboard) | [`4c61dda`](https://github.com/N-M-D-W/ansimon_front_end/commit/4c61dda304c7364719b6bee9c619aec79d2a7360) | 4 |
| [`ansimon-connection`](https://github.com/N-M-D-W/ansimon-connection) | [`components/integration`](../components/integration) | [`a280117`](https://github.com/N-M-D-W/ansimon-connection/commit/a28011720151377338719f1330d5e22d7f4c201d) | 2 |
| [`heatwave_ml_model`](https://github.com/N-M-D-W/heatwave_ml_model) | [`components/heatwave-ml`](../components/heatwave-ml) | [`d652eaa`](https://github.com/N-M-D-W/heatwave_ml_model/commit/d652eaa1f32bac0fdd760ed36939b655d66fc853) | 4 |
| [`rag-llm`](https://github.com/N-M-D-W/rag-llm) | [`components/rag`](../components/rag) | [`5edce09`](https://github.com/N-M-D-W/rag-llm/commit/5edce09e1d10130e10589dcdbed35b8860c69910) | 12 |
| [`t-map_location_connection_ansimon`](https://github.com/N-M-D-W/t-map_location_connection_ansimon) | [`components/shelter-routing`](../components/shelter-routing) | [`b242261`](https://github.com/N-M-D-W/t-map_location_connection_ansimon/commit/b242261b1bb97269ad91818944d1453b44efd181) | 1 |
| [`ansimon-phone_calling`](https://github.com/N-M-D-W/ansimon-phone_calling) | [`components/voice-calling`](../components/voice-calling) | [`05509df`](https://github.com/N-M-D-W/ansimon-phone_calling/commit/05509df1e0b9e6bf2c06b20d9963ed244a74e3d4) | 7 |
| [`ansimon-total`](https://github.com/N-M-D-W/ansimon-total) | Not applicable | Empty repository | 0 |

## Consolidation Notes

- The latest `ansimon-connection` snapshot includes integrated copies of the RAG and voice modules. It is kept intact under `components/integration` as the recommended end-to-end Python implementation.
- The standalone `rag-llm` and `ansimon-phone_calling` snapshots are also retained in full because they contain independent documentation and earlier component-level work.
- The backend's default `main` branch was not its most complete state. `feat/risk-ml-and-connection-integration` contains all 62 commits reachable across `main`, `develop`, `feat/global-foundation`, and `feat/elderly-crud`, so that superset branch is used for `components/backend`.
- Two `rag-llm` branches diverged before the current `main` snapshot and consisted primarily of early uploaded notes and ZIP bundles. Their unique Git blobs are preserved byte-for-byte in [`archive/source-branches/rag-llm`](../archive/source-branches/rag-llm); duplicate blobs are stored once.
- Original Korean READMEs are preserved as `README.ko.md`; the active `README.md` files are English editions prepared for this consolidated repository.
- The award certificate was supplied separately by the repository owner and is stored under `docs/award` in both original PDF and GitHub-renderable PNG form.
- No high-confidence API keys or access tokens were detected in the copied working trees. Populated `.env` files remain excluded by `.gitignore`.
- Post-import verification corrected one syntax error in `components/shelter-routing/shelter/recommend.py` (a missing comma in `DEMO_LATLON`) and changed JSON file loading to close the input deterministically. The regression suite and RED/GREEN evidence are recorded in [`docs/testing/shelter-demo-coordinate.tdd.md`](testing/shelter-demo-coordinate.tdd.md).
