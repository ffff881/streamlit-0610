import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math
from io import BytesIO

# --- 설정 및 제목 ---
st.set_page_config(layout="wide")
st.title("✂️ 나만의 테셀레이션 만들기")
st.write("슬라이더를 조작하여 기본 도형을 변형하고, 테셀레이션을 만들어 보세요!")

# --- 사이드바 설정 ---
st.sidebar.header("1. 기본 도형 선택 및 변형")

# 1.1. 기본 정다각형 선택
shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"])

# 1.2. 타일 기준 크기
tile_size = st.sidebar.slider("타일 기준 크기:", min_value=50, max_value=200, value=100, step=10)

# --- 기본 도형의 꼭짓점 정의 함수 (좌표 계산) ---
# 이 함수는 (0,0)을 기준으로 한 정다각형의 꼭짓점을 반환합니다.
def get_base_polygon_vertices(shape_type, size):
    vertices = []
    if shape_type == "정사각형":
        vertices = np.array([
            [0, 0],
            [size, 0],
            [size, size],
            [0, size]
        ])
    elif shape_type == "정삼각형":
        height = size * math.sqrt(3) / 2
        vertices = np.array([
            [0, 0],
            [size, 0],
            [size / 2, height]
        ])
    elif shape_type == "정육각형":
        # 중심이 원점인 정육각형
        angle_rad = np.radians(np.arange(0, 360, 60))
        vertices = np.array([
            [size * np.cos(a), size * np.sin(a)]
            for a in angle_rad
        ])
        # 왼쪽 아래 꼭짓점을 (0,0) 근처로 이동 (보기 좋게)
        min_x = np.min(vertices[:, 0])
        min_y = np.min(vertices[:, 1])
        vertices = vertices - [min_x, min_y]
    return vertices

# --- 사용자 정의 변형 섹션 (슬라이더 사용) ---
st.sidebar.subheader("2. 도형 변형 (슬라이더로 조절)")
st.sidebar.write("각 꼭짓점의 X, Y 좌표를 조절하여 기본 도형을 변형합니다.")

# 현재 선택된 도형의 기본 꼭짓점 가져오기
base_vertices = get_base_polygon_vertices(shape_type, tile_size)
num_vertices = len(base_vertices)

# 변형된 꼭짓점을 저장할 리스트 (초기값은 기본 꼭짓점)
modified_vertices = []

st.sidebar.markdown("---")
for i in range(num_vertices):
    st.sidebar.markdown(f"**꼭짓점 {i+1} (`{base_vertices[i][0]:.0f},{base_vertices[i][1]:.0f}`)**")
    
    # 원본 꼭짓점 좌표를 기준으로 상대적인 이동 값 슬라이더
    # 변형 범위는 tile_size에 비례하게 설정하여 과도한 변형 방지 및 유연성 확보
    range_limit = tile_size / 2
    delta_x = st.sidebar.slider(f"X 변형 (꼭짓점 {i+1}):",
                                min_value=-range_limit, max_value=range_limit,
                                value=0.0, step=1.0, key=f"vx_{i}")
    delta_y = st.sidebar.slider(f"Y 변형 (꼭짓점 {i+1}):",
                                min_value=-range_limit, max_value=range_limit,
                                value=0.0, step=1.0, key=f"vy_{i}")
    
    modified_vertices.append(base_vertices[i] + [delta_x, delta_y])

modified_vertices = np.array(modified_vertices)

# 변형된 도형 미리보기
st.sidebar.subheader("변형된 도형 미리보기")
fig_preview, ax_preview = plt.subplots(figsize=(3,3))
ax_preview.set_aspect('equal')
ax_preview.axis('off')
ax_preview.add_patch(Polygon(modified_vertices, closed=True,
                            edgecolor='blue', facecolor='lightblue', lw=1))
ax_preview.autoscale_view()
st.sidebar.pyplot(fig_preview)


# --- 테셀레이션 패턴 생성 설정 ---
st.sidebar.header("3. 테셀레이션 구성")

st.sidebar.write("이제 변형된 도형으로 테셀레이션 패턴을 만들어보세요.")
rows = st.sidebar.slider("행 개수:", min_value=1, max_value=15, value=5, key="t_rows")
cols = st.sidebar.slider("열 개수:", min_value=1, max_value=15, value=5, key="t_cols")

st.sidebar.subheader("색상 설정")
color1 = st.sidebar.color_picker("기본 색상 1:", "#FF6347", key="t_color1") # Tomato
color2 = st.sidebar.color_picker("보조 색상 2:", "#4682B4", key="t_color2") # SteelBlue

st.sidebar.subheader("패턴 변환 옵션")
transform_type = st.sidebar.radio(
    "테셀레이션 변환 방식:",
    ("평행이동", "회전", "대칭", "미끄럼 반사 (미구현)")
)
rotation_angle = 0
if transform_type == "회전":
    rotation_angle = st.sidebar.slider("회전 각도 (도):", min_value=0, max_value=360, value=90, step=15, key="t_rot_angle")
    st.info("회전은 기본 도형이 '회전 대칭'이 될 때 평면을 완벽히 채울 수 있습니다.")
elif transform_type == "대칭":
    st.info("대칭 변환은 현재 단순 복제 후 X축 반전 처리됩니다.")
elif transform_type == "미끄럼 반사 (미구현)":
    st.warning("미끄럼 반사 기능은 아직 구현되지 않았습니다.")

# --- 테셀레이션 생성 및 시각화 함수 ---
def create_tessellation_pattern(vertices, ref_tile_size, rows, cols, color1, color2, transform_type, rotation_angle, current_shape_type):
    if vertices is None or len(vertices) == 0:
        st.error("유효한 도형 꼭짓점이 없습니다.")
        return None

    # 변형된 도형의 경계 상자 계산
    min_x, min_y = np.min(vertices[:, 0]), np.min(vertices[:, 1])
    max_x, max_y = np.max(vertices[:, 0]), np.max(vertices[:, 1])
    
    # 도형의 중심 (회전/대칭 기준)
    shape_center_x = (min_x + max_x) / 2
    shape_center_y = (min_y + max_y) / 2

    # 그리드 간격 (기본 정다각형 타입에 따라 결정)
    x_step_grid = ref_tile_size
    y_step_grid = ref_tile_size
    
    if current_shape_type == "정삼각형":
        x_step_grid = ref_tile_size / 2 # 한 칸 너비 (가로로 겹침)
        y_step_grid = ref_tile_size * math.sqrt(3) / 2 # 높이
    elif current_shape_type == "정육각형":
        x_step_grid = ref_tile_size * 1.5 # 육각형 가로 간격 (센터 투 센터)
        y_step_grid = ref_tile_size * math.sqrt(3) # 육각형 세로 간격 (두 행에 걸쳐)


    # Matplotlib Figure 및 Axes 설정
    # figsize는 실제 테셀레이션 크기에 맞춰 조정 (종횡비 유지)
    fig, ax = plt.subplots(figsize=(cols * x_step_grid / 70, rows * y_step_grid / 70))
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    for r in range(rows):
        for c in range(cols):
            # 1. 초기 위치 오프셋 계산 (그리드 배치)
            offset_x_grid = c * x_step_grid
            offset_y_grid = r * y_step_grid

            # 정육각형 및 정삼각형 그리드 특수 오프셋
            if current_shape_type == "정육각형" and r % 2 != 0:
                offset_x_grid += x_step_grid / 2 # 홀수 행은 반 칸 이동하여 벌집 모양 형성
            elif current_shape_type == "정삼각형":
                # 정삼각형은 복잡하여 추후 정교한 구현 필요 (현재는 단순 사각형 격자처럼 배치)
                # 이 부분에 정삼각형의 회전/반전/오프셋 로직을 추가해야 완벽한 테셀레이션이 됨
                pass
            
            # 2. 도형 꼭짓점 복사 (슬라이더로 변형된 꼭짓점)
            current_tile_vertices_base = np.copy(vertices)
            
            # 3. 도형의 로컬 중심 (변환의 기준점)
            current_shape_center_x = np.mean(current_tile_vertices_base[:, 0])
            current_shape_center_y = np.mean(current_tile_vertices_base[:, 1])

            # 도형의 중심을 원점으로 임시 이동 (변환 적용을 위해)
            temp_vertices = current_tile_vertices_base - [current_shape_center_x, current_shape_center_y]

            # 4. 선택된 변환 방식 적용
            if transform_type == "회전":
                theta = np.radians(rotation_angle)
                rotation_matrix = np.array([
                    [np.cos(theta), -np.sin(theta)],
                    [np.sin(theta), np.cos(theta)]
                ])
                temp_vertices = np.dot(temp_vertices, rotation_matrix.T) # 회전 적용
                
            elif transform_type == "대칭":
                # Y축 기준 대칭 (좌우 반전)
                temp_vertices = temp_vertices * np.array([-1, 1])
                
            # 5. 최종 위치로 이동 (변환된 도형 + 그리드 오프셋)
            final_vertices = temp_vertices + [current_shape_center_x, current_shape_center_y] + [offset_x_grid, offset_y_grid]


            # 6. Matplotlib에 도형 추가
            face_color = color1 if (r + c) % 2 == 0 else color2
            polygon = Polygon(final_vertices, closed=True, edgecolor='black', facecolor=face_color, lw=1)
            ax.add_patch(polygon)

    # Matplotlib 축 범위 자동 조정 및 여백 추가
    ax.autoscale_view()
    ax.set_xlim(ax.get_xlim()[0] - x_step_grid/2, ax.get_xlim()[1] + x_step_grid/2)
    ax.set_ylim(ax.get_ylim()[0] - y_step_grid/2, ax.get_ylim()[1] + y_step_grid/2)

    return fig

# --- 메인 화면에 테셀레이션 패턴 표시 ---
st.subheader("생성된 테셀레이션 패턴")
fig = create_tessellation_pattern(modified_vertices, tile_size, rows, cols, color1, color2, transform_type, rotation_angle, shape_type)
if fig:
    st.pyplot(fig)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.1)
    st.download_button(
        label="테셀레이션 이미지 다운로드 (PNG)",
        data=buf.getvalue(),
        file_name="custom_tessellation.png",
        mime="image/png"
    )
else:
    st.warning("테셀레이션 패턴을 생성할 수 없습니다. 설정을 확인해 보세요.")

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib을 사용하여 만들어졌습니다.")
