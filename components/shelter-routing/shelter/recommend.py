#!/usr/bin/env python3
"""어르신 위치에서 도보로 가장 가까운 무더위쉼터를 고른다.

    python shelter/recommend.py                          # 예시 좌표(서울시청), OpenAPI
    python shelter/recommend.py 37.5013 127.0396
    python shelter/recommend.py --file=무더위쉼터.csv      # 포털에서 내려받은 파일로
    python shelter/recommend.py --demo                   # 네트워크 없이 로직만 검증

쉼터 목록은 두 곳 중 하나에서 온다.
  1) 서울열린데이터광장 OpenAPI  — .env 의 SHELTER_API_BASE_URL(인증키), SHELTER_SERVICE(서비스명)
  2) 포털에서 내려받은 CSV/JSON — --file= 또는 .env 의 SHELTER_FILE
컬럼명은 두 경로가 서로 다르지만(한글/영문) 코드가 알아서 맞춘다.

흐름: 쉼터 목록(서울열린데이터광장) → 직선거리로 후보 압축 → TMAP 보행경로로 확정.
직선거리는 후보를 줄이는 용도일 뿐이다. 추천 근거는 항상 TMAP 도보 시간이다
(ANSIMON_WORKFLOW §11: TMAP 실패 시 직선거리만으로 이동을 확정하지 않는다).

출력은 voice/job.py 의 job["shelter"] 모양 그대로다.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from math import asin, cos, radians, sin, sqrt

import aiohttp
from dotenv import load_dotenv

# DB 연결 전까지 쓰는 예시 좌표. 나중에 elderly_profile.latitude/longitude 로 대체된다.
DEMO_LATLON = (37.5301 127.1236)   # 서울시청

SEOUL = "http://openapi.seoul.go.kr:8088"
SERVICE = os.getenv("SHELTER_SERVICE", "TbGtnHwcwP")   # 서울시 무더위쉼터 표준데이터
TMAP = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"

PAGE = 1000         # 서울 오픈API 는 1회 최대 1000건. 전체를 받으려면 나눠 받아야 한다.
CANDIDATES = 5      # TMAP 은 1건당 1콜이라 직선거리 상위 N개만 확인한다
WALK_LIMIT_MIN = 20 # 폭염에 고령자가 걸을 만한 상한. 넘으면 이동 권고하지 않는다

# 쉼터명·주소 후보 키. 위경도는 이름으로 찾지 않는다 (아래 latlon 참고).
# 한글 키는 포털 CSV/JSON 내려받기용, 영문 키는 OpenAPI 용이다.
NAME_KEYS = ("쉼터명칭", "시설명", "명칭", "R_AREA_NM", "RSTR_NM", "FCLTY_NM", "AREA_NM", "NM")
ADDR_KEYS = ("도로명주소", "지번주소", "소재지도로명주소",
             "RN_DETAIL_ADRES", "RDNMADR", "ADRES", "DTL_ADRES", "LNMADR")
_WARNED: set[str] = set()

# 한반도 위경도 범위. 두 구간이 겹치지 않아서 값만 보고 위도/경도를 구분할 수 있다.
LAT_RANGE, LON_RANGE = (33.0, 39.0), (124.0, 132.0)


def pick(row: dict, keys: tuple[str, ...]):
    for k in keys:
        if (v := row.get(k)) not in (None, ""):
            return v
    return None


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """직선거리(m). 후보를 줄이는 용도로만 쓴다."""
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371000 * asin(sqrt(a))


def latlon(row: dict) -> tuple[float, float] | None:
    """필드명이 아니라 값의 범위로 위도·경도를 찾는다.

    포털·데이터셋마다 컬럼명이 LA/LAT/YCORD/위도 등으로 제각각인데, 한국 위도(33~39)와
    경도(124~132)는 범위가 겹치지 않는다. 이름 목록을 관리하는 것보다 이쪽이 안 깨진다.
    TM 좌표(21만, 54만 같은 값)는 범위 밖이라 자동으로 걸러진다.
    """
    lat = lon = None
    for v in row.values():
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if lat is None and LAT_RANGE[0] < f < LAT_RANGE[1]:
            lat = f
        elif lon is None and LON_RANGE[0] < f < LON_RANGE[1]:
            lon = f
    return (lat, lon) if lat and lon else None


def to_shelter(row: dict) -> dict | None:
    """원본 행 -> 우리 모양. 좌표를 못 찾은 행은 버린다."""
    if not (c := latlon(row)):
        return None
    if (name := pick(row, NAME_KEYS)) is None and "name" not in _WARNED:
        _WARNED.add("name")   # 이름 컬럼만 못 찾은 건 치명적이지 않다. 딱 한 번만 알린다.
        print(f"  ! 쉼터명 컬럼을 못 찾았습니다. 실제 컬럼: {', '.join(row)}\n"
              f"    -> recommend.py 의 NAME_KEYS 에 추가하세요.", file=sys.stderr)
    return {"name": name or "이름 미상",
            "address": pick(row, ADDR_KEYS), "lat": c[0], "lon": c[1]}


def from_file(path: str) -> list[dict]:
    """포털에서 직접 내려받은 CSV/JSON. 시연 때 API 장애에 걸리지 않는 길."""
    import csv

    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    body = json.loads(open(path, encoding="utf-8-sig").read())
    if isinstance(body, list):
        return body
    for v in body.values():                      # {"DATA":[...]} / {"서비스명":{"row":[...]}}
        if isinstance(v, list):
            return v
        if isinstance(v, dict) and isinstance(v.get("row"), list):
            return v["row"]
    sys.exit(f"{path} 에서 행 목록을 못 찾았습니다. 최상위 키: {list(body)}")


async def fetch_shelters(s: aiohttp.ClientSession) -> list[dict]:
    """서울열린데이터광장 무더위쉼터 목록. 1000건씩 끝까지 받는다."""
    key = os.getenv("SHELTER_API_BASE_URL") or os.getenv("SHELTER_API_KEY")
    if not key:
        sys.exit("SHELTER_API_BASE_URL(인증키)가 .env 에 없습니다.")

    rows: list[dict] = []
    while True:
        start = len(rows) + 1
        url = f"{SEOUL}/{key}/json/{SERVICE}/{start}/{start + PAGE - 1}/"
        try:
            async with s.get(url, timeout=20) as r:
                body = await r.json(content_type=None)
        except Exception as e:   # 워크플로우 §11: 쉼터 API 실패는 예상된 상황이다
            sys.exit(f"쉼터 API 연결 실패 ({type(e).__name__}) — {SEOUL}\n"
                     f"  망 차단·오타·포털 점검을 확인하세요.")

        block = body.get(SERVICE) if isinstance(body.get(SERVICE), dict) else {}
        result = block.get("RESULT") or body.get("RESULT") or {}
        code = result.get("CODE", "")
        if code and code != "INFO-000":
            sys.exit(f"쉼터 API 오류 {code}: {result.get('MESSAGE')}\n"
                     f"  현재 서비스명 SERVICE={SERVICE}\n"
                     f"  포털 > 해당 데이터셋 > Open API 탭의 '서비스명'을 확인해\n"
                     f"  .env 에 SHELTER_SERVICE=<서비스명> 으로 넣으세요.")

        page = block.get("row") or []
        if not page:
            if not rows:   # 첫 페이지부터 비었다 = 추측이 틀렸다. 원본을 그대로 보여준다.
                sys.exit("쉼터 목록이 비었습니다. 서버 원본 응답:\n"
                         + json.dumps(body, ensure_ascii=False)[:800]
                         + f"\n\n  요청 URL(키 가림): {SEOUL}/***/json/{SERVICE}/{start}/…"
                         + "\n  → 서비스명이 틀렸을 가능성이 큽니다. .env 에 SHELTER_SERVICE=... 로 지정하거나,"
                         + "\n    포털에서 CSV/JSON 을 내려받아 --file 로 넘기세요.")
            break
        rows += page
        total = block.get("list_total_count")
        if len(page) < PAGE or (total and len(rows) >= int(total)):
            break
    return rows


async def walk_time(s: aiohttp.ClientSession, lat: float, lon: float,
                    dest: dict) -> dict | None:
    """TMAP 보행자 경로. 실패하면 None — 직선거리로 대체하지 않는다."""
    key = os.getenv("TMAP_APP_KEY")
    body = {"startX": lon, "startY": lat, "endX": dest["lon"], "endY": dest["lat"],
            "reqCoordType": "WGS84GEO", "resCoordType": "WGS84GEO",
            "startName": "출발지", "endName": "쉼터"}
    try:
        async with s.post(TMAP, json=body, timeout=15,
                          headers={"appKey": key, "Content-Type": "application/json"}) as r:
            if r.status != 200:
                print(f"  · TMAP {r.status} — {dest['name']} 건너뜀", file=sys.stderr)
                return None
            p = (await r.json())["features"][0]["properties"]
    except Exception as e:
        print(f"  · TMAP 실패 ({type(e).__name__}) — {dest['name']} 건너뜀", file=sys.stderr)
        return None
    return dest | {"walk_meters": int(p["totalDistance"]),
                   "walk_minutes": round(p["totalTime"] / 60)}


async def recommend(lat: float, lon: float, path: str | None = None) -> dict:
    """도보 시간이 가장 짧은 쉼터 1곳. job["shelter"] 에 그대로 넣을 수 있다."""
    async with aiohttp.ClientSession() as s:
        rows = from_file(path) if path else await fetch_shelters(s)
        all_ = [x for r in rows if (x := to_shelter(r))]
        if not all_:
            sys.exit(f"{len(rows)}행을 받았지만 위경도를 가진 행이 하나도 없습니다.\n"
                     f"  첫 행: {json.dumps(rows[0], ensure_ascii=False)[:400] if rows else '(없음)'}")
        print(f"쉼터 {len(all_)}곳 확보 (원본 {len(rows)}행)", file=sys.stderr)

        # 직선거리 상위 N개만 TMAP 에 물어본다
        near = sorted(all_, key=lambda x: haversine(lat, lon, x["lat"], x["lon"]))[:CANDIDATES]
        routed = [x for x in await asyncio.gather(
            *(walk_time(s, lat, lon, d) for d in near)) if x]

    if not routed:
        # 워크플로우 §11: TMAP 실패 시 직선거리만으로 이동을 확정 권고하지 않는다
        return {"needs_review": True, "reason": "TMAP 경로 계산 실패",
                "nearest_by_line": near[0]["name"] if near else None}

    best = min(routed, key=lambda x: x["walk_minutes"])
    return best | {
        "open_status": "UNKNOWN",       # 운영시간은 쉼터 API 원본에서 별도 확인 필요
        "candidates": len(routed),
        # 폭염에 20분 넘게 걷게 하지 않는다. 사회복지사가 판단하도록 넘긴다.
        "needs_review": best["walk_minutes"] > WALK_LIMIT_MIN,
    }


def demo() -> None:
    """API 없이 도는 자체검사 — 후보 압축과 최단 도보 선택 로직만 확인한다."""
    me = (37.5665, 126.9780)
    assert 885 < haversine(37.5665, 126.9780, 37.5745, 126.9780) < 895   # 위도 0.008° ≈ 890m
    assert haversine(*me, *me) == 0

    # 실제 데이터 모양 그대로: 컬럼명을 몰라도, 경도가 위도보다 앞에 와도 잡아야 한다.
    rows = [{"R_AREA_NM": "먼쉼터", "LAT": "37.60", "LOT": "126.98"},
            {"쉼터명칭": "가까운쉼터", "경도": "126.9785", "위도": "37.5670",
             "X좌표": "211184.80", "Y좌표": "547780.40", "년도": "2026"},
            {"R_AREA_NM": "좌표없음", "LAT": "", "LOT": ""},
            {"R_AREA_NM": "해외", "LAT": "48.85", "LOT": "2.35"}]
    ok = [x for r in rows if (x := to_shelter(r))]
    assert len(ok) == 2, ok
    assert (ok[1]["lat"], ok[1]["lon"]) == (37.5670, 126.9785), ok[1]   # TM 좌표에 안 속음
    ok[1]["name"] = "가까운쉼터"        # 한글 컬럼명은 NAME_KEYS 밖 -> "이름 미상"

    near = sorted(ok, key=lambda x: haversine(*me, x["lat"], x["lon"]))
    assert near[0]["name"] == "가까운쉼터"

    # 직선거리가 가까워도 도보가 더 걸리면 뒤집힌다 — 이게 이 파일의 존재 이유다
    routed = [near[0] | {"walk_minutes": 18}, near[1] | {"walk_minutes": 6}]
    assert min(routed, key=lambda x: x["walk_minutes"])["name"] == "먼쉼터"
    print("자체검사 통과 — 직선거리 압축 + 도보시간 우선 선택")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
        raise SystemExit
    load_dotenv()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--file=")),
                os.getenv("SHELTER_FILE"))
    lat, lon = (float(args[0]), float(args[1])) if len(args) > 1 else DEMO_LATLON
    print(f"기준 위치 {lat}, {lon}" + ("  (예시 좌표)" if (lat, lon) == DEMO_LATLON else ""))
    print(json.dumps(asyncio.run(recommend(lat, lon, path)), ensure_ascii=False, indent=2))
