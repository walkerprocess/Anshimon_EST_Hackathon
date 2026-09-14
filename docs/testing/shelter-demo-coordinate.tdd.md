# Shelter Demo Coordinate - TDD Evidence

## Source

The user requested a clean consolidation of the ANSIMON repositories. During verification, the documented offline shelter demo failed to parse because `DEMO_LATLON` was missing the comma between latitude and longitude.

## User Journey

As a reviewer or teammate, I want the shelter router's offline demo to run without credentials, so that I can verify candidate reduction and pedestrian-time ranking before connecting external APIs.

## RED

Command:

```text
python -m unittest -v test_recommend.py
```

Observed result before the production change:

```text
FAILED (failures=1, errors=1)
SyntaxError: invalid syntax. Perhaps you forgot a comma?
DEMO_LATLON = (37.5301 127.1236)
```

Checkpoint: `460b69f test(shelter): reproduce invalid demo coordinates`

## GREEN

The coordinate constant was corrected to the two-value tuple `(37.5301, 127.1236)`. The file parser was also changed to close JSON input files deterministically after the expanded tests exposed a `ResourceWarning`.

Command:

```text
python -m coverage run --branch -m unittest -v test_recommend.py
python -m coverage report -m --include='*\shelter\recommend.py'
```

Observed result:

```text
Ran 15 tests in 0.127s
OK
recommend.py: 92% branch-aware coverage
```

## Guarantees

| # | Guarantee | Test type | Result |
| ---: | --- | --- | --- |
| 1 | The shelter module compiles and the default coordinate is a latitude/longitude tuple | Regression unit test | PASS |
| 2 | The credential-free CLI demo completes cleanly | CLI integration test | PASS |
| 3 | CSV and supported JSON shelter shapes are parsed correctly and files are closed | Unit test | PASS |
| 4 | Missing keys, provider failures, empty responses, and route failures remain explicit | Async unit test with fakes | PASS |
| 5 | Route metrics are normalized and the shortest successful walk is selected | Async unit test with fakes | PASS |
| 6 | Failed routes are marked for human review instead of treated as valid recommendations | Async integration test with fakes | PASS |

## Coverage and Known Gaps

Branch-aware production coverage for `recommend.py` is 92%. The untested lines are the name-warning branch and the real network-backed CLI path. Seoul Open Data and TMAP calls are replaced by deterministic fakes; no paid API or live phone action was performed.
