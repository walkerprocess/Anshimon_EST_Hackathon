# -*- coding: utf-8 -*-
"""3) 프롬프트

Spring이 넘기는 구조화 컨텍스트(프로필/위험도/기상/쉼터)와 RAG 근거 청크를
분리된 블록으로 직렬화해 system/messages 형태의 페이로드로 만든다
(llm_client.py가 이걸 그대로 Alan API 호출에 사용한다).

시스템 프롬프트에 강제 규칙을 명시한다:
  1. 근거 청크 밖 사실 생성 금지 (hallucination 차단)
  2. 문장마다 evidenceChunkIds 첨부 의무화
  3. 응급 증상 문구는 승인된 고정 템플릿 그대로 사용
  4. 출력은 JSON 하나만 (자유 텍스트 금지)
"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Optional

from schemas import EMERGENCY_GUIDANCE_TEMPLATE, ROUTE_SOURCE_STRAIGHT_LINE, STRAIGHT_LINE_NOTICE

DEFAULT_MODEL = "alan"
DEFAULT_MAX_TOKENS = 1500

OUTPUT_JSON_SHAPE = """{
  "guidanceSentences": [
    {"text": "<근거에 기반한 안내 문장>", "evidenceChunkIds": ["<chunk_id>", ...]}
  ],
  "emergencyFlag": <true|false>,
  "emergencyMessage": "<emergencyFlag가 true일 때만, 고정 템플릿 그대로>" | null,
  "recommendedShelter": {"name": "...", "address": "...", "distanceM": <number|null>} | null
}"""

SYSTEM_PROMPT_TEMPLATE = f"""너는 폭염 취약계층 대상 자동 안내 문구를 작성하는 '안심온' 시스템의 생성 모듈이다.

[강제 규칙]
1. 아래 [RAG 근거 청크] 블록에 있는 내용만 사실로 사용한다. 근거 청크에 없는 사실(수치, 시설명, 의학적 조언 등)은 절대 새로 만들어내지 않는다.
2. guidanceSentences의 모든 문장은 그 문장의 근거가 된 chunk_id를 evidenceChunkIds 배열에 반드시 채워 넣는다. 비워두지 않는다.
3. 응급 증상(의식저하 등)을 언급해야 하는 경우, emergencyFlag를 true로 하고 emergencyMessage에는 아래 승인된 고정 문구를 토씨 하나 바꾸지 않고 그대로 사용한다.
   고정 문구: "{EMERGENCY_GUIDANCE_TEMPLATE}"
4. [쉼터후보]의 routeSource 가 "{ROUTE_SOURCE_STRAIGHT_LINE}" 이면, 실제 길안내를 받지 못하고 직선거리로 고른 쉼터라는 뜻이다. 이때는 guidanceSentences 마지막에 아래 고지 문구를 토씨 하나 바꾸지 않고 그대로 넣고, evidenceChunkIds 는 빈 배열로 둔다. walkMinutes 대신 estimatedWalkMinutes 가 있다는 점도 유의해 "몇 분 걸린다"고 단정하지 않는다.
   고지 문구: "{STRAIGHT_LINE_NOTICE}"
   반대로 routeSource 가 "TMAP" 이면 이 문구를 절대 넣지 않는다.
5. 출력은 아래 JSON 스키마 하나만 반환한다. JSON 앞뒤로 어떤 설명, 인사말, 코드블록 표시(```)도 붙이지 않는다.

[출력 JSON 스키마]
{OUTPUT_JSON_SHAPE}
"""


def _to_plain(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    return obj


def _format_evidence_block(evidence_chunks: list[Any]) -> str:
    lines = []
    for c in evidence_chunks:
        c = _to_plain(c)
        heading = " > ".join(c.get("heading_path", []))
        lines.append(
            f"- chunk_id={c['chunk_id']} | heading_path=[{heading}] | text=\"{c['text']}\""
        )
    return "\n".join(lines) if lines else "(검색된 근거 청크 없음)"


def build_user_content(
    elderly_profile: dict,
    risk_snapshot: dict,
    shelter: Optional[dict],
    weather: dict,
    evidence_chunks: list[Any],
) -> str:
    blocks = [
        "[프로필]",
        json.dumps(elderly_profile, ensure_ascii=False, indent=2),
        "",
        "[위험도]",
        json.dumps(risk_snapshot, ensure_ascii=False, indent=2, default=str),
        "",
        "[기상]",
        json.dumps(weather, ensure_ascii=False, indent=2),
        "",
        "[쉼터후보]",
        json.dumps(shelter, ensure_ascii=False, indent=2) if shelter else "(추천 후보 없음)",
        "",
        "[RAG 근거 청크]",
        _format_evidence_block(evidence_chunks),
        "",
        "위 컨텍스트와 근거 청크만 사용해 이 대상자에게 보낼 안내 계획을 JSON으로 작성하라.",
    ]
    return "\n".join(blocks)


def build_messages(
    elderly_profile: dict,
    risk_snapshot: dict,
    shelter: Optional[dict],
    weather: dict,
    evidence_chunks: list[Any],
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> dict:
    """llm_client._call_real_api()가 그대로 쓸 system/messages 페이로드를 반환한다."""
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": SYSTEM_PROMPT_TEMPLATE,
        "messages": [
            {
                "role": "user",
                "content": build_user_content(
                    elderly_profile, risk_snapshot, shelter, weather, evidence_chunks
                ),
            }
        ],
    }


if __name__ == "__main__":
    from retrieval import search

    demo_profile = {"elderlyId": 101, "age": 82, "livesAlone": True, "targetAudience": ["ELDERLY"]}
    demo_risk = {"riskSnapshotId": 812, "riskLevel": "HIGH", "riskScore": 0.83}
    demo_weather = {"temperatureC": 36.2, "heatWarning": "폭염경보"}
    demo_shelter = {"name": "종로노인종합복지관 경로당", "address": "서울특별시 종로구 삼봉로 71"}

    chunks = search("노인 폭염 대비 수칙", target_audience=["ELDERLY"], top_k=4)
    payload = build_messages(demo_profile, demo_risk, demo_shelter, demo_weather, chunks)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
