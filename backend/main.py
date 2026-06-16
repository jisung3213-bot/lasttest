from pathlib import Path
from typing import Dict, List

import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# =========================
# 기본 설정
# =========================

app = FastAPI(
    title="COC HO Recommendation API",
    description="COC 은닉 시나리오별 핸드아웃 추천 백엔드",
    version="1.0.0"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

HO_LIST = ["HO1", "HO2", "HO3", "HO4"]


# =========================
# 요청 / 응답 모델
# =========================

class AnswerItem(BaseModel):
    question_id: int = Field(..., description="문제 번호")
    option_id: int = Field(..., description="선택지 번호")


class RecommendRequest(BaseModel):
    scenario: str = Field(..., description="시나리오 이름")
    answers: List[AnswerItem] = Field(..., description="사용자가 선택한 답변 목록")


class RecommendResponse(BaseModel):
    scenario: str
    recommended_ho: str
    scores: Dict[str, int]
    reason: str


# =========================
# 점수 파일 매핑
# =========================

SCORING_FILES = {
    "VOID": DATA_DIR / "void_scoring_backend.json",
    "고스트 레코드": DATA_DIR / "ghost_record_scoring_backend.json",
    "청춘계시론": DATA_DIR / "youth_apocalypse_scoring_backend.json",
}


# =========================
# 유틸 함수
# =========================

def load_json(path: Path) -> dict:
    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"점수 데이터 파일을 찾을 수 없습니다: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scoring_data(scenario: str) -> dict:
    if scenario not in SCORING_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 시나리오입니다: {scenario}"
        )

    file_path = SCORING_FILES[scenario]
    all_data = load_json(file_path)

    if scenario not in all_data:
        raise HTTPException(
            status_code=500,
            detail=f"점수 파일 안에 시나리오 키가 없습니다: {scenario}"
        )

    return all_data[scenario]


def calculate_scores(scenario: str, answers: List[AnswerItem]) -> Dict[str, int]:
    scoring_data = load_scoring_data(scenario)

    total_scores = {
        "HO1": 0,
        "HO2": 0,
        "HO3": 0,
        "HO4": 0,
    }

    for answer in answers:
        question_key = str(answer.question_id)
        option_key = str(answer.option_id)

        if question_key not in scoring_data:
            raise HTTPException(
                status_code=400,
                detail=f"존재하지 않는 문제 번호입니다: {answer.question_id}"
            )

        if option_key not in scoring_data[question_key]:
            raise HTTPException(
                status_code=400,
                detail=f"{answer.question_id}번 문제에 존재하지 않는 선택지입니다: {answer.option_id}"
            )

        option_scores = scoring_data[question_key][option_key]

        for ho in HO_LIST:
            total_scores[ho] += option_scores.get(ho, 0)

    return total_scores


def decide_recommended_ho(scores: Dict[str, int]) -> str:
    # 동점일 경우 HO1 → HO2 → HO3 → HO4 순서로 먼저 나온 HO를 선택
    return max(HO_LIST, key=lambda ho: scores[ho])


def make_reason(scenario: str, recommended_ho: str, scores: Dict[str, int]) -> str:
    score_text = ", ".join([f"{ho}: {scores[ho]}점" for ho in HO_LIST])

    return (
        f"{scenario} 답변을 기준으로 점수를 합산한 결과 "
        f"{recommended_ho}의 점수가 가장 높게 나왔습니다. "
        f"점수 합계는 {score_text}입니다."
    )


# =========================
# API 엔드포인트
# =========================

@app.get("/")
def root():
    return {
        "message": "COC HO 추천 FastAPI 서버가 실행 중입니다.",
        "available_scenarios": list(SCORING_FILES.keys())
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    if len(request.answers) == 0:
        raise HTTPException(
            status_code=400,
            detail="답변 목록이 비어 있습니다."
        )

    scores = calculate_scores(
        scenario=request.scenario,
        answers=request.answers
    )

    recommended_ho = decide_recommended_ho(scores)

    reason = make_reason(
        scenario=request.scenario,
        recommended_ho=recommended_ho,
        scores=scores
    )

    return RecommendResponse(
        scenario=request.scenario,
        recommended_ho=recommended_ho,
        scores=scores,
        reason=reason
    )