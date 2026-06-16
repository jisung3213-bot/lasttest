import json
from pathlib import Path

import os
import requests
import streamlit as st


# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="COC 은닉 시나리오별 핸드아웃 추천 애플리케이션",
    layout="wide"
)

# Docker Compose 기준
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/recommend"
)

# 로컬 테스트용
# API_URL = "http://localhost:8000/recommend"


# =========================
# 경로 설정
# =========================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = BASE_DIR / "images"


SCENARIOS = {
    "void": {
        "name": "VOID",
        "color": "#f2c94c",
        "question_file": DATA_DIR / "void_questions_frontend.json",
        "image_file": IMAGE_DIR / "void.png",
    },
    "ghost": {
        "name": "고스트 레코드",
        "color": "#6b0000",
        "question_file": DATA_DIR / "ghost_record_questions_frontend.json",
        "image_file": IMAGE_DIR / "ghost_record.png",
    },
    "youth": {
        "name": "청춘계시론",
        "color": "#2f80ed",
        "question_file": DATA_DIR / "youth_apocalypse_questions_frontend.json",
        "image_file": IMAGE_DIR / "youth_apocalypse.png",
    },
}


# =========================
# HO 결과 설명
# =========================

HO_RESULT_TEXT = {
    "VOID": {
        "HO1": {
            "title": "신입 경찰관",
            "description": "당신은 올해 막 형사가 된 신입이다. 이 젊은 나이에 발탁된 것은 이례적인 일이다."
        },
        "HO2": {
            "title": "신형 파트너 안드로이드",
            "description": "당신은 HO1의 파트너 로봇이다. 최신형 기능이 모두 탑재되어 있다."
        },
        "HO3": {
            "title": "베테랑 경찰관",
            "description": "당신은 다른 과에서 이동해 온 형사다. 지금까지 수많은 사건을 해결해 왔을 것이다."
        },
        "HO4": {
            "title": "정체불명의 안드로이드",
            "description": "당신은 HO3의 파트너 로봇이다. HO3를 신뢰하며, 안드로이드로서 그를 지원해 왔다."
        },
    },
    "고스트 레코드": {
        "HO1": {
            "title": "미래",
            "description": "당신은 미래를 볼 수 있다."
        },
        "HO2": {
            "title": "시선",
            "description": "당신은 시선을 끌 수 있다."
        },
        "HO3": {
            "title": "기억",
            "description": "당신은 기억해 둘 수 있다."
        },
        "HO4": {
            "title": "운명",
            "description": "당신은 운을 좋게 만들 수 있다."
        },
    },
    "청춘계시론": {
        "HO1": {
            "title": "미술부의 부장",
            "description": "이 예술제를 위해 모든 것을 쏟아부었다고 해도 과언이 아닐 것이다.\n졸업을 위한 마지막 발걸음, 그 끝은 과연 어디로 향할까."
        },
        "HO2": {
            "title": "미술부의 부부장",
            "description": "부장을 도와 예술제를 열심히 준비하고 있다.\n내년이 된다면 자신이 부장이 될 테니, 그에 대한 예행 연습이라고 할 수도 있겠다."
        },
        "HO3": {
            "title": "미술부의 부원",
            "description": "이번 예술제의 공동 작품 제작에 참여하게 된 것을 내심 자랑스럽게 생각하고 있다.\n특히나 이번 주제, 푸른 하늘은 당신에게 특별하다."
        },
        "HO4": {
            "title": "미술부의 신입부원",
            "description": "당신이 이 학교에 온 이유는 단순하다. 작년 예술제에서 전시 그림을 보고 마음을 사로잡혀버렸기에."
        },
    },
}


# =========================
# 세션 상태 초기화
# =========================

if "page" not in st.session_state:
    st.session_state.page = "main"

if "selected_scenario_key" not in st.session_state:
    st.session_state.selected_scenario_key = None

if "result" not in st.session_state:
    st.session_state.result = None


# =========================
# 유틸 함수
# =========================

def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def go_to_quiz(scenario_key: str):
    st.session_state.selected_scenario_key = scenario_key
    st.session_state.page = "quiz"
    st.session_state.result = None


def go_to_main():
    st.session_state.page = "main"
    st.session_state.selected_scenario_key = None
    st.session_state.result = None


def set_result_background_color():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #111111;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================
# 메인 화면
# =========================

def show_main_page():
    st.markdown(
        """
        <h1 style="
            text-align: center;
            font-size: 42px;
            margin-top: 20px;
            margin-bottom: 50px;
        ">
            COC 은닉 시나리오별 핸드아웃 추천 애플리케이션
        </h1>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    for col, scenario_key in zip(cols, SCENARIOS.keys()):
        scenario_info = SCENARIOS[scenario_key]

        with col:
            scenario_name = scenario_info["name"]
            color = scenario_info["color"]
            image_path = scenario_info["image_file"]

            st.markdown(
                f"""
                <h2 style="
                    text-align: center;
                    color: {color};
                    margin-bottom: 20px;
                ">
                    {scenario_name}
                </h2>
                """,
                unsafe_allow_html=True
            )

            # 이미지는 링크가 아니라 단순 표시
            if image_path.exists():
                st.image(str(image_path), use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path}")

            # 이동은 이미지 아래의 별도 버튼으로 처리
            if st.button(
                f"{scenario_name} 문제 풀기",
                key=f"start_{scenario_key}",
                use_container_width=True
            ):
                go_to_quiz(scenario_key)
                st.rerun()


# =========================
# 문제 풀이 화면
# =========================

def show_quiz_page():
    scenario_key = st.session_state.selected_scenario_key
    scenario_info = SCENARIOS[scenario_key]

    question_data = load_json(scenario_info["question_file"])
    scenario_name = question_data["scenario"]
    questions = question_data["questions"]

    st.markdown(
        f"""
        <h1 style="text-align: center;">
            {scenario_name} 핸드아웃 추천 질문
        </h1>
        """,
        unsafe_allow_html=True
    )

    if st.button("처음 화면으로 돌아가기"):
        go_to_main()
        st.rerun()

    st.divider()

    with st.form(key=f"{scenario_key}_quiz_form"):
        st.markdown("### 사용자 정보")

        user_name = st.text_input(
            "이름을 입력하세요.",
            key=f"{scenario_key}_user_name"
        )

        student_id = st.text_input(
            "학번을 입력하세요.",
            key=f"{scenario_key}_student_id"
        )

        st.divider()

        answers = []

        for question in questions:
            question_id = question["id"]
            question_text = question["question"]
            options = question["options"]

            option_id_to_text = {
                option["id"]: option["text"]
                for option in options
            }

            st.markdown(f"### Q{question_id}. {question_text}")

            selected_option_id = st.radio(
                label="답변을 선택하세요.",
                options=list(option_id_to_text.keys()),
                format_func=lambda option_id, mapping=option_id_to_text: mapping[option_id],
                key=f"{scenario_key}_q_{question_id}"
            )

            answers.append(
                {
                    "question_id": question_id,
                    "option_id": selected_option_id
                }
            )

            st.markdown("")

        submitted = st.form_submit_button("결과 보기")

    if submitted:
        request_data = {
            "scenario": scenario_name,
            "answers": answers
        }

        try:
            response = requests.post(
                API_URL,
                json=request_data,
                timeout=10
            )

            if response.status_code != 200:
                st.error("백엔드 서버에서 오류 응답을 받았습니다.")
                st.write(f"상태 코드: {response.status_code}")
                st.code(response.text)
                return

            st.session_state.result = response.json()
            st.session_state.page = "result"
            st.rerun()

        except requests.exceptions.ConnectionError:
            st.error("FastAPI 백엔드 서버에 연결할 수 없습니다.")

        except requests.exceptions.Timeout:
            st.error("FastAPI 백엔드 서버 응답 시간이 초과되었습니다.")

        except Exception as e:
            st.error("알 수 없는 오류가 발생했습니다.")
            st.write(str(e))


# =========================
# 결과 화면
# =========================

def show_result_page():
    scenario_key = st.session_state.selected_scenario_key
    scenario_info = SCENARIOS[scenario_key]
    scenario_name = scenario_info["name"]
    image_path = scenario_info["image_file"]

    result = st.session_state.result
    recommended_ho = result.get("recommended_ho")

    ho_info = HO_RESULT_TEXT.get(scenario_name, {}).get(recommended_ho)

    if ho_info is None:
        st.error("추천 결과 설명을 찾을 수 없습니다.")
        st.json(result)
        return

    ho_title = ho_info["title"]
    ho_description = ho_info["description"].replace("\n", "<br>")

    # 결과 제목 가운데 정렬
    st.markdown(
        f"""
        <h1 style="
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            margin-top: 20px;
            margin-bottom: 30px;
        ">
            {scenario_name} 추천 결과
        </h1>
        """,
        unsafe_allow_html=True
    )

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)

    st.divider()

    # 추천 핸드아웃 문구 가운데 정렬
    st.markdown(
        """
        <h3 style="
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 20px;
        ">
            추천 핸드아웃
        </h3>
        """,
        unsafe_allow_html=True
    )

    # HO 번호 가운데 정렬
    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 72px;
            font-weight: 900;
            margin-bottom: 20px;
        ">
            {recommended_ho}
        </div>
        """,
        unsafe_allow_html=True
    )

    # HO 명칭 가운데 정렬
    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 28px;
        ">
            {ho_title}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 설명 가운데 정렬
    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 22px;
            line-height: 1.9;
            max-width: 850px;
            margin: 0 auto;
        ">
            {ho_description}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if "scores" in result:
        with st.expander("점수 상세 보기"):
            st.json(result["scores"])

    # 버튼 가운데 정렬
    left, center, right = st.columns([1, 2, 1])

    with center:
        if st.button("처음 화면으로 돌아가기", use_container_width=True):
            go_to_main()
            st.rerun()


# =========================
# 실행부
# =========================

if st.session_state.page == "main":
    show_main_page()

elif st.session_state.page == "quiz":
    show_quiz_page()

elif st.session_state.page == "result":
    show_result_page()