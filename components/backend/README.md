# ANSIMON Backend

The Spring Boot API and operational domain layer for ANSIMON, Team N.M.D.W's predictive heatwave-care prototype.

This snapshot comes from `feat/risk-ml-and-connection-integration` at commit [`5b26f62`](https://github.com/N-M-D-W/ansimon_backend/commit/5b26f620db02867bd416cf5394e31096228f5aef). That branch contains every commit reachable from the source repository's `main`, `develop`, `feat/global-foundation`, and `feat/elderly-crud` branches, so it is the most complete backend state.

## Stack

- Java 21, Spring Boot 4.1.0, and Gradle Wrapper
- Spring MVC and WebFlux `WebClient`
- Spring Data JPA, MySQL, and Flyway
- Spring AI 2.0 with OpenAI and optional PostgreSQL/pgvector
- Springdoc OpenAPI, Actuator, validation, Lombok, JUnit, and H2 for tests

## Responsibilities

The source tree is organized by domain:

| Domain | Responsibility |
| --- | --- |
| `elderly` | Older-adult profiles, consent, addresses, and geocoding |
| `risk` | ML forecasts, policy adjustment, and risk snapshots |
| `weather` | Forecast and heat-alert ingestion |
| `shelter` | Cooling-shelter persistence and route data |
| `guidance` | Care-run requests and intervention plans |
| `contact` | Preventive-call jobs, observations, and result callbacks |
| `support` / `dispatch` | Follow-up work, assignment, and workload planning |
| `dashboard` | Aggregated data for the social-worker dashboard |
| `global` | Shared configuration, errors, responses, and HTTP clients |

## API Surface

| Scope | Endpoint family | Purpose |
| --- | --- | --- |
| Public | `/api/v1/elderly` | Create, list, read, update, and delete profiles |
| Public | `/api/v1/risk/current` | Read the current risk view |
| Public | `/api/v1/contact/observations` | Review and manage call observations |
| Internal | `/internal/v1/risk/forecast` | Request an ML-backed risk forecast |
| Internal | `/internal/v1/guidance/care-runs/{elderlyId}` | Trigger the integrated care workflow |
| Internal | `/internal/v1/contact/results` | Receive structured call outcomes |

When the application is running, health information is available at `/actuator/health`; Springdoc exposes the generated API UI at `/swagger-ui/index.html`.

## Run Locally

Prerequisites: JDK 21 and MySQL 8 or newer. The application does not automatically load `.env` files, so copy the values from `.env.example` into your IDE run configuration or shell environment.

```powershell
$env:SPRING_PROFILES_ACTIVE = "local"
$env:MYSQL_URL = "jdbc:mysql://localhost:3306/ansimon?serverTimezone=Asia/Seoul&characterEncoding=UTF-8"
$env:MYSQL_USERNAME = "ansimon"
$env:MYSQL_PASSWORD = "replace-with-your-local-password"

.\gradlew.bat bootRun
```

On macOS or Linux, export the same variables and run `./gradlew bootRun`. The default port is `8080`. Flyway applies the schema under `src/main/resources/db/migration/mysql`; JPA validates that schema rather than creating it.

External services are optional until their related endpoints are called. Keep `SPRING_AI_VECTORSTORE_TYPE=none` unless PostgreSQL with pgvector is configured. ML defaults to `http://localhost:8100`, while the integrated care service defaults to `http://localhost:7000`.

## Test and Build

```powershell
.\gradlew.bat test
.\gradlew.bat build
```

The preserved source workflow at `.github/workflows/ci-cd.yml` tested the standalone backend and optionally deployed it to Railway. Because this backend now lives below `components/backend`, that nested workflow is archival and does not run as a monorepo-level GitHub Actions workflow.

## Prototype Boundaries

The hackathon MVP intentionally omits authentication. Do not expose it as a public production API without authentication, authorization, secrets management, and a deployment-specific security review. Do not commit populated environment files or real participant data.

For the original Korean project notes, see [README.ko.md](README.ko.md). Repository-specific development notes are preserved in [AGENTS.md](AGENTS.md).
