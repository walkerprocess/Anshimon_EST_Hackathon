# ansimon-backend

NMDW(너무더워) 팀의 안심온(ansimon) Spring Boot API 서버입니다.

프로젝트 구조와 작업 규칙은 먼저 [AGENTS.md](AGENTS.md)를 확인하세요. 도메인별 작업을 할 때는 해당 패키지의 `AGENTS.md`도 함께 확인합니다.

## Commands

```bash
gradle bootRun
gradle test
gradle build
```

현재 Gradle Wrapper는 포함하지 않았습니다. 로컬 Gradle 설치 후 실행하거나, 나중에 `gradle wrapper`로 Wrapper를 추가하세요.

## Main Dependencies

- Spring Boot Web
- Spring WebFlux WebClient
- Spring Data JPA
- MySQL Connector
- Flyway
- Spring AI OpenAI starter
- Spring AI PGvector starter
- PostgreSQL Driver
- Lombok
- Actuator

## Notes

- MVP에서는 로그인 기능을 만들지 않습니다.
- MySQL은 서비스 도메인 데이터 저장소입니다.
- PostgreSQL + pgvector는 RAG 벡터 저장소입니다.
- 기본 로컬 설정은 `SPRING_AI_VECTORSTORE_TYPE=none`입니다. RAG VectorStore를 실제로 연결할 때 `pgvector`로 변경하세요.
