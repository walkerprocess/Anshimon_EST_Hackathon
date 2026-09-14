# ANSIMON Backend

The Spring Boot API and domain foundation for ANSIMON, Team N.M.D.W's predictive heatwave-care prototype.

## Stack

- Java 21 and Spring Boot
- Spring MVC and WebFlux `WebClient`
- Spring Data JPA, MySQL, and Flyway
- Spring AI with OpenAI and optional PostgreSQL/pgvector
- Actuator, validation, Lombok, JUnit, and H2 for tests

## Run

```bash
# macOS / Linux
./gradlew bootRun

# Windows
gradlew.bat bootRun
```

The default server port is `8080`. Copy values from `.env.example` into your environment before enabling external APIs.

## Test and Build

```bash
./gradlew test
./gradlew build
```

## Domain Layout

The source tree is organized by domain: `elderly`, `risk`, `weather`, `shelter`, `guidance`, `contact`, `dispatch`, `support`, and `dashboard`. Shared configuration and response types live under `global`.

MySQL is intended for operational domain data. PostgreSQL with pgvector is intended for the RAG vector store. Local configuration defaults `SPRING_AI_VECTORSTORE_TYPE` to `none`; switch it to `pgvector` only after the vector database is configured.

The hackathon MVP intentionally omits authentication. Do not expose it as a public production API without adding authentication, authorization, and a deployment-specific security review.

For original project notes, see [README.ko.md](README.ko.md). Repository-specific development guidance is documented in [AGENTS.md](AGENTS.md).
