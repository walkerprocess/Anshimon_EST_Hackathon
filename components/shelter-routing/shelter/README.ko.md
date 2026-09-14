# t-map_location_connection_ansimon

안심온 — 어르신 위치(위도·경도)에서 **도보로 가장 가깝고 편한 무더위쉼터**를 찾는다.

## 하는 일

```
쉼터 전체 (서울 ~3천 곳)
      ↓ 직선거리 정렬
   후보 5곳
      ↓ TMAP 보행자 경로 5건 동시 호출
도보시간 → 횡단보도 수 순 정렬
      ↓
최적 쉼터 1곳 + 경로 안내 + 대안 4곳
```

직선거리는 **후보를 줄이는 용도로만** 쓴다. 추천 근거는 항상 TMAP 도보 시간이다.
강 건너편처럼 직선으로 가까워도 실제 도보는 먼 경우가 있다.

TMAP `searchOption=30`(최단거리+계단제외)을 기본으로 쓴다. 고령자를 육교·지하보도
계단으로 안내하지 않는 것이 "편한 경로"의 핵심이다.

## 실행

```bash
pip install aiohttp python-dotenv
cp .env.example .env        # 키 채우기

python recommend.py                              # 예시 좌표(서울시청)
python recommend.py 37.5301 127.1236             # 특정 위경도
python recommend.py 37.5301 127.1236 --file=무더위쉼터.csv
python recommend.py --demo                       # 네트워크 없이 로직만 검증
```

쉼터 목록은 **OpenAPI** 또는 **포털에서 내려받은 CSV/JSON**(`--file=`) 중 하나에서 온다.
시연에는 `--file` 을 권장한다 — 포털 장애나 키 만료에 걸리지 않는다.

컬럼명은 데이터셋마다 다르지만(`LAT`/`위도`/`YCORD`…) 코드가 **값의 범위**로
위경도를 찾으므로(한국 위도 33~39, 경도 124~132) 이름이 뭐든 동작한다.
TM 좌표(21만·54만 같은 값)는 범위 밖이라 자동으로 걸러진다.

## 출력

```json
{
  "name": "성내1동주민센터",
  "address": "서울특별시 강동구 성내로 13",
  "lat": 37.5304794, "lon": 127.122458,
  "walk_minutes": 3, "walk_meters": 162, "crossings": 1,
  "open_status": "UNKNOWN",
  "needs_review": false,
  "route": ["80m 이동", "횡단보도 건너기", "도착"],
  "alternatives": [{"name": "...", "walk_minutes": 4, "crossings": 0}]
}
```

- `route` — 전화 안내 문구로 그대로 쓸 수 있다
- `crossings` — 횡단보도 횟수. 사회복지사가 "혼자 이동 가능한가"를 판단하는 근거
- `alternatives` — 어르신이 다른 곳을 원하실 때 바로 답할 수 있게
- `needs_review` — 도보 20분 초과이거나 TMAP 실패. **사람이 확인해야 한다는 뜻**

## 다른 모듈과의 연결

| 방향 | 내용 |
| --- | --- |
| 입력 | `elderly_profile.latitude` / `longitude` (지금은 예시 좌표 하드코딩) |
| 출력 | `ansimon_backend` 의 `shelter` 테이블 + `intervention_plan.shelter_id` |
| 소비 | `ansimon-phone_calling` 의 `job["shelter"]` — 반환값을 그대로 넣을 수 있다 |

백엔드 구조상 쉼터 선정은 Spring `shelter` 패키지 담당이다. 이 저장소는 **참조 구현**이며,
운영에서는 TMAP 결과를 `shelter_route_cache` 에 저장해 중복 호출을 줄여야 한다.

## 실패 처리 (ANSIMON_WORKFLOW §11)

| 상황 | 동작 |
| --- | --- |
| TMAP 실패 | 직선거리로 **대체하지 않고** `needs_review: true` 로 사람에게 넘긴다 |
| TMAP 일부 실패(401 등) | 해당 쉼터만 후보에서 빼고 나머지로 계속 진행 |
| 도보 20분 초과 | 추천은 하되 `needs_review: true` |
| 쉼터 API 실패 | 원본 응답을 그대로 출력해 원인을 바로 알 수 있게 한다 |
