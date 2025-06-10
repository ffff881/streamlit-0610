import streamlit as st
import requests
import json # JSON 데이터를 다루기 위해 추가

st.set_page_config(layout="centered") # 앱 레이아웃을 중앙 정렬로 설정
st.title("🤔 심심할 때 뭐 하지? & 💬 오늘의 명언")
st.markdown("버튼을 눌러 새로운 영감을 받아보세요!")

# ------------------ 1. 무작위 활동 추천 기능 ------------------
st.header("✨ 무작위 활동 추천")
st.markdown("심심할 때 할 만한 활동을 무작위로 추천해 드립니다.")

@st.cache_data # 데이터를 캐싱하여 앱 성능 향상
def get_random_activity():
    """Bored API에서 무작위 활동을 가져오는 함수"""
    api_url = "https://www.boredapi.com/api/activity"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킵니다.
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"활동 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

if st.button("새로운 활동 추천받기"):
    activity_data = get_random_activity()
    if activity_data:
        # API 응답에 에러 메시지가 있을 수 있으므로 확인
        if "error" in activity_data:
            st.warning(f"활동을 추천할 수 없습니다: {activity_data['error']}")
        else:
            st.info(f"**활동:** {activity_data.get('activity', '정보 없음')}")
            st.markdown(f"**유형:** `{activity_data.get('type', '정보 없음')}`")
            st.markdown(f"**참가자 수:** `{activity_data.get('participants', '정보 없음')}`")
            if activity_data.get('price') is not None:
                st.markdown(f"**비용:** `{activity_data.get('price', 0) * 100:.0f}%` (0% = 무료, 100% = 비쌈)")


st.markdown("---") # 구분선

# ------------------ 2. 무작위 명언(격언) 생성 기능 ------------------
st.header("💡 오늘의 명언")
st.markdown("마음을 울리는 무작위 명언을 보여드립니다.")

@st.cache_data # 데이터를 캐싱하여 앱 성능 향상
def get_random_advice():
    """Advice Slip API에서 무작위 명언을 가져오는 함수"""
    api_url = "https://api.adviceslip.com/advice"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킵니다.
        # Advice Slip API는 'slip'이라는 키 안에 명언이 들어있습니다.
        return response.json().get('slip', {}).get('advice')
    except requests.exceptions.RequestException as e:
        st.error(f"명언 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

if st.button("새로운 명언 보기", key="advice_button"): # 버튼 키는 유일해야 합니다.
    advice_text = get_random_advice()
    if advice_text:
        st.success(f"**\" {advice_text} \"**")
    else:
        st.warning("명언을 가져올 수 없습니다. 다시 시도해 주세요.")

st.markdown("---")
st.markdown("© 2025 무작위 생성기 앱. Powered by BoredAPI & Advice Slip API.")
