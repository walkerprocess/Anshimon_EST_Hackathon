# contact

## Responsibility
예방 전화 작업 생성, 승인, 예약, 발신 요청, 재시도, 전화 결과 콜백 수신과 상태 전이를 담당합니다.

## Structure
```bash
contact/
├── api/          # 전화 작업 생성/승인 API, 전화 결과 콜백 API
├── application/  # 예약, 재시도, 상태 전이, 중복 방지
├── domain/       # ContactJob, ContactStatus, CallObservation 등
├── infra/        # 전화 어댑터 WebClient, Repository
└── dto/          # 전화 계획/결과 DTO
```

## Rules
- 첫 미응답 후 10분 뒤 1회만 재전화합니다.
- 두 번째 미응답은 수동 확인 업무로 넘깁니다.
- `elderlyId + riskSnapshotId + purpose` 조합의 idempotency key로 중복 생성을 막습니다.
- 통화 결과는 enum과 신뢰도를 검증한 뒤 저장합니다.
