# guidance

## Responsibility
Spring AI 기반 LLM/RAG로 공식 근거를 검색하고 개인별 행동지침, 추천 쉼터 안내문, 전화 질문 순서를 생성/검증합니다.

## Structure
```bash
guidance/
├── api/           # 안내 계획 생성/조회 API
├── application/   # 컨텍스트 조립, RAG 검색, LLM 호출, 결과 검증
├── domain/        # InterventionPlan, GuidanceStatus, EvidenceChunkRef 등
├── infra/
│   ├── ai/        # Spring AI ChatClient 어댑터, structured output DTO
│   ├── rag/       # 문서 수집, 청킹, VectorStore 검색
│   └── prompt/    # 시스템/유저 프롬프트 템플릿
└── dto/           # 안내 계획 요청/응답 DTO
```

## Rules
- 정부/공공기관 공식 문서만 운영 지침의 RAG 근거로 사용합니다.
- LLM 응답은 JSON/DTO로 구조화하고 enum, 필수 필드, 근거 ID를 검증합니다.
- 숫자, 주소, 운영시간, 전화번호는 LLM 결과를 신뢰하지 말고 원천 데이터와 대조합니다.
- 응급 증상 관련 문구는 자유 생성보다 승인된 고정 템플릿을 우선 사용합니다.
