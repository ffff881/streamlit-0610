import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import math
from io import BytesIO

# --- 설정 및 제목 ---
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
        # 중심이 원점인 정육각형 (나중에 평행이동)
        angle_rad = np.radians(np.arange(0, 360, 60))
        vertices = np.array([
            [size * np.cos(a), size * np.sin(a)]
            for a in angle_rad
        ])
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
    # 원본 꼭짓점 좌표를 기준으로 상대적인 이동 값 슬라이더
    # (x,y) 좌표에 대한 변형 범위는 타일 크기에 따라 조절 필요
    delta_x = st.sidebar.slider(f"꼭짓점 {i+1} X 변형:",
                                min_value=-tile_size / 2, max_value=tile_size / 2,
                                value=0.0, step=1.0, key=f"vx_{i}")
    delta_y = st.sidebar.slider(f"꼭짓점 {i+1} Y 변형:",
                                min_value=-tile_size / 2, max_value=tile_size / 2,
                                value=0.0, step=1.0, key=f"vy_{i}")
    modified_vertices.append(base_vertices[i] + [delta_x, delta_y])

modified_vertices = np.array(modified_vertices)

# --- 테셀레이션 패턴 생성 설정 ---
st.sidebar.header("3. 패턴 생성 설정")
rows = st.sidebar.slider("행 개수:", min_value=1, max_value=15, value=5)
cols = st.sidebar.slider("열 개수:", min_value=1, max_value=15, value=5)

st.sidebar.subheader("색상 설정")
color1 = st.sidebar.color_picker("기본 색상 1:", "#FF6347") # Tomato
color2 = st.sidebar.color_picker("보조 색상 2:", "#4682B4") # SteelBlue

st.sidebar.subheader("패턴 변환")
rotation_angle = st.sidebar.slider("각 타일 회전 (도):", min_value=0, max_value=360, value=0, step=15)
# 추후 뒤집기, 밀기 등 추가 가능

# --- 테셀레이션 생성 및 시각화 함수 ---
def create_tessellation_with_custom_shape(vertices, tile_size, rows, cols, color1, color2, rotation_angle):
    if vertices is None or len(vertices) == 0:
        st.error("유효한 도형 꼭짓점이 없습니다.")
        return None

    # 테셀레이션 크기 계산 (최대/최소 x,y 값으로 경계 상자 계산)
    min_x, min_y = np.min(vertices[:, 0]), np.min(vertices[:, 1])
    max_x, max_y = np.max(vertices[:, 0]), np.max(vertices[:, 1])
    shape_width = max_x - min_x
    shape_height = max_y - min_y

    # 그리드 간격 계산 (기본)
    x_step = shape_width
    y_step = shape_height

    fig, ax = plt.subplots(figsize=(cols * x_step / 70, rows * y_step / 70))
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    for r in range(rows):
        for c in range(cols):
            offset_x = c * x_step
            offset_y = r * y_step

            # --- 선택된 도형 타입에 따른 오프셋 및 특수 처리 ---
            if shape_type == "정육각형":
                x_offset_hex = tile_size * 1.5
                y_offset_hex = tile_size * math.sqrt(3) / 2

                offset_x = c * x_offset_hex
                offset_y = r * y_offset_hex

                # 짝수/홀수 행에 따른 X축 오프셋
                if r % 2 != 0:
                    offset_x += x_offset_hex / 2
                
            elif shape_type == "정삼각형":
                st.warning("정삼각형 테셀레이션은 고급 구현이 필요합니다. 현재는 단순 배치됩니다.")
                pass

            # 각 타일의 변형된 꼭짓점 복사 및 이동
            current_vertices = np.copy(modified_vertices) + [offset_x, offset_y]

            # 선택된 회전 적용 (도형의 중심을 기준으로 회전)
            if rotation_angle != 0:
                # 도형의 중심 계산
                center_x = np.mean(current_vertices[:, 0])
                center_y = np.mean(current_vertices[:, 1])
                
                # 중심을 원점으로 이동 -> 회전 -> 다시 원래 위치로 이동
                temp_vertices = current_vertices - [center_x, center_y]
                theta = np.radians(rotation_angle)
                rotation_matrix = np.array([
                    [np.cos(theta), -np.sin(theta)],
                    [np.sin(theta), np.cos(theta)]
                ])
                rotated_vertices = np.dot(temp_vertices, rotation_matrix.T) + [center_x, center_y]
                current_vertices = rotated_vertices

            face_color = color1 if (r + c) % 2 == 0 else color2
            polygon = Polygon(current_vertices, closed=True, edgecolor='black', facecolor=face_color, lw=1)
            ax.add_patch(polygon)

    # 모든 패치가 추가된 후 x,y 축 범위 조정
    ax.autoscale_view()
    # 여백 추가 (테셀레이션이 너무 꽉 차지 않도록)
    ax.set_xlim(ax.get_xlim()[0] - tile_size/2, ax.get_xlim()[1] + tile_size/2)
    ax.set_ylim(ax.get_ylim()[0] - tile_size/2, ax.get_ylim()[1] + tile_size/2)

    return fig

# --- 메인 화면에 테셀레이션 표시 ---
st.subheader("생성된 테셀레이션 미리보기")

# 실제 테셀레이션 생성 및 표시
fig = create_tessellation_with_custom_shape(modified_vertices, tile_size, rows, cols, color1, color2, rotation_angle)
if fig:
    st.pyplot(fig)
    # 이미지 다운로드 버튼 (Matplotlib 그림을 PNG로 저장)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.1)
    st.download_button(
        label="테셀레이션 이미지 다운로드 (PNG)",
        data=buf.getvalue(),
        file_name="custom_tessellation.png",
        mime="image/png"
    )
else:
    st.info("선택된 도형의 테셀레이션을 그릴 수 없습니다. 다른 도형을 선택하거나 설정을 확인해 보세요.")

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib을 사용하여 만들어졌습니다.")
