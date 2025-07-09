import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import math
# from streamlit_drawable_canvas import st_canvas # 만약 이 컴포넌트를 사용한다면

st.set_page_config(layout="wide")
st.title("✂️ 나만의 테셀레이션 만들기")
st.write("기본 도형을 변형하고 복사하여 독특한 패턴을 만들어 보세요!")

# --- 사이드바 설정 ---
st.sidebar.header("1. 기본 도형 선택 및 변형")

# 1.1. 기본 정다각형 선택
shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"])

# 1.2. 기본 타일 크기
tile_size = st.sidebar.slider("타일 기준 크기:", min_value=50, max_value=200, value=100, step=10)

# --- 기본 도형의 꼭짓점 정의 함수 (좌표 계산) ---
def get_base_polygon_vertices(shape_type, size):
    vertices = []
    if shape_type == "정사각형":
        # (0,0)을 기준으로 한 사각형
        vertices = np.array([
            [0, 0],
            [size, 0],
            [size, size],
            [0, size]
        ])
    elif shape_type == "정삼각형":
        # (0,0)을 기준으로 한 정삼각형
        height = size * math.sqrt(3) / 2
        vertices = np.array([
            [0, 0],
            [size, 0],
            [size / 2, height]
        ])
    elif shape_type == "정육각형":
        # (0,0)을 기준으로 한 정육각형 (중심이 아닌, 시작 꼭짓점이 (0,0)에 가깝게)
        angle_rad = np.radians(np.arange(0, 360, 60))
        # 중심을 기준으로 하고 나중에 이동
        center_x, center_y = size, size * math.sqrt(3) / 2
        vertices = np.array([
            [center_x + size * np.cos(a), center_y + size * np.sin(a)]
            for a in angle_rad
        ])
        # 왼쪽 아래 꼭짓점을 (0,0)에 가깝게 이동
        min_x = np.min(vertices[:, 0])
        min_y = np.min(vertices[:, 1])
        vertices = vertices - [min_x, min_y]

    return vertices

# --- 사용자 정의 변형 섹션 ---
st.sidebar.subheader("2. 도형 변형 (슬라이더로 조절)")
st.sidebar.write("각 꼭짓점의 좌표를 조절하여 기본 도형을 변형합니다.")

# 현재 선택된 도형의 기본 꼭짓점 가져오기
base_vertices = get_base_polygon_vertices(shape_type, tile_size)
num_vertices = len(base_vertices)

# 변형된 꼭짓점을 저장할 리스트 (초기값은 기본 꼭짓점)
modified_vertices = []

# 각 꼭짓점별로 슬라이더 생성
st.sidebar.markdown("---")
st.sidebar.write("**각 꼭짓점의 상대적 위치 변형**")
for i in range(num_vertices):
    st.sidebar.markdown(f"**꼭짓점 {i+1}**")
    # 원본 꼭
