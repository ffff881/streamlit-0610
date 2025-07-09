import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import colorsys

# --- 설정 및 제목 ---
st.set_page_config(layout="wide")
st.title("🧩 학생들을 위한 테셀레이션 만들기 도구")
st.write("나만의 테셀레이션 패턴을 만들고 탐색해보세요!")

# --- 사이드바 설정 ---
st.sidebar.header("테셀레이션 설정")

# 1. 기본 도형 선택 (초기 버전에서는 정사각형부터 시작)
shape_options = ["정사각형", "정삼각형", "정육각형"] # 나중에 다른 도형 추가 가능
selected_shape = st.sidebar.selectbox("기본 도형 선택:", shape_options)

# 2. 크기 및 반복 횟수
tile_size = st.sidebar.slider("타일 크기:", min_value=10, max_value=100, value=50, step=5)
rows = st.sidebar.slider("행 개수:", min_value=1, max_value=20, value=10)
cols = st.sidebar.slider("열 개수:", min_value=1, max_value=20, value=10)

# 3. 색상 선택
st.sidebar.subheader("색상 설정")
primary_color = st.sidebar.color_picker("기본 색상 1:", "#FF6347") # Tomato
secondary_color = st.sidebar.color_picker("보조 색상 2:", "#4682B4") # SteelBlue

# --- 테셀레이션 생성 함수 ---
def create_square_tessellation(size, rows, cols, color1, color2):
    fig, ax = plt.subplots(figsize=(cols * size / 100, rows * size / 100)) # 비율 유지
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, cols * size)
    ax.set_ylim(0, rows * size)
    ax.axis('off') # 축 숨기기

    for r in range(rows):
        for c in range(cols):
            x = c * size
            y = r * size
            square = plt.Rectangle((x, y), size, size,
                                   edgecolor='black',
                                   facecolor=color1 if (r + c) % 2 == 0 else color2)
            ax.add_patch(square)
    return fig

# 정삼각형 테셀레이션 함수 (추가 필요)
def create_triangle_tessellation(size, rows, cols, color1, color2):
    # 정삼각형 테셀레이션 로직 구현 (복잡할 수 있음)
    # 예: 각 삼각형의 꼭짓점 좌표를 계산하고 Polygon 패치 추가
    # 회전 및 반전 고려 필요
    st.warning("정삼각형 테셀레이션은 구현 예정입니다! (복잡한 기하학 계산 필요)")
    return None # Placeholder

# 정육각형 테셀레이션 함수 (추가 필요)
def create_hexagon_tessellation(size, rows, cols, color1, color2):
    # 정육각형 테셀레이션 로직 구현
    st.warning("정육각형 테셀레이션은 구현 예정입니다! (복잡한 기하학 계산 필요)")
    return None # Placeholder


# --- 메인 화면에 테셀레이션 표시 ---
st.subheader("생성된 테셀레이션")

if selected_shape == "정사각형":
    fig = create_square_tessellation(tile_size, rows, cols, primary_color, secondary_color)
    if fig:
        st.pyplot(fig)
elif selected_shape == "정삼각형":
    fig = create_triangle_tessellation(tile_size, rows, cols, primary_color, secondary_color)
    if fig:
        st.pyplot(fig) # 실제 구현 후 활성화
elif selected_shape == "정육각형":
    fig = create_hexagon_tessellation(tile_size, rows, cols, primary_color, secondary_color)
    if fig:
        st.pyplot(fig) # 실제 구현 후 활성화

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib을 사용하여 만들어졌습니다.")

# --- 추가 기능 아이디어 (향후 확장) ---
st.sidebar.markdown("---")
st.sidebar.header("고급 설정 (향후 추가될 기능)")
st.sidebar.checkbox("타일 회전", disabled=True)
st.sidebar.checkbox("불규칙 변형", disabled=True)
st.sidebar.button("랜덤 테셀레이션 생성", disabled=True)
st.sidebar.download_button("이미지 다운로드 (PNG)", data="...", file_name="tessellation.png", disabled=True)
