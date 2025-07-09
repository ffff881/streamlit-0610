import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math
from io import BytesIO

# 필요한 경우, `streamlit-drawable-canvas` 임포트
# pip install streamlit-drawable-canvas 가 되어 있어야 합니다!
from streamlit_drawable_canvas import st_canvas

# --- 설정 및 제목 ---
st.set_page_config(layout="wide")
st.title("✂️ 나만의 테셀레이션 만들기")
st.write("캔버스에서 도형을 직접 변형하고, 테셀레이션을 만들어 보세요!")

# --- 캔버스 설정 ---
# 캔버스 크기를 좀 더 명확히 설정 (픽셀 단위)
canvas_width = 700
canvas_height = 500

# --- 기본 도형의 꼭짓점 정의 함수 (캔버스 중앙에 오도록 조정) ---
# 이 함수는 이제 항상 list of lists를 반환합니다.
def get_initial_drawable_polygon_vertices(shape_type, size, canvas_width, canvas_height):
    vertices = []
    # 도형의 중심을 (0,0)으로 일단 설정
    if shape_type == "정사각형":
        vertices = [
            [-size / 2, -size / 2],
            [size / 2, -size / 2],
            [size / 2, size / 2],
            [-size / 2, size / 2]
        ]
    elif shape_type == "정삼각형":
        height = size * math.sqrt(3) / 2
        vertices = [
            [-size / 2, -height / 2],
            [size / 2, -height / 2],
            [0, height / 2]
        ]
    elif shape_type == "정육각형":
        angle_rad = np.radians(np.arange(0, 360, 60))
        vertices_np = np.array([
            [size * np.cos(a), size * np.sin(a)]
            for a in angle_rad
        ])
        vertices = vertices_np.tolist() # numpy array를 list로 변환
    
    # 캔버스 중앙으로 이동
    center_x, center_y = canvas_width / 2, canvas_height / 2
    vertices_shifted = [[v[0] + center_x, v[1] + center_y] for v in vertices]
    
    return vertices_shifted

# --- 사이드바 설정 ---
st.sidebar.header("1. 기본 도형 선택")
shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"])
tile_size = st.sidebar.slider("캔버스 타일 기준 크기:", min_value=50, max_value=200, value=100, step=10)

# --- 캔버스에 초기 도형 그리기 위한 세션 상태 관리 (단순화) ---
# 매번 새로운 initial_drawing 데이터를 생성하여 명확성을 높입니다.
initial_vertices = get_initial_drawable_polygon_vertices(shape_type, tile_size, canvas_width, canvas_height)

# `streamlit-drawable-canvas`는 `initial_drawing`에 {"objects": [...]} 형태를 기대함.
# 여기에 도형 객체 리스트를 직접 구성하여 전달합니다.
initial_canvas_drawing_data = {
    "objects": [{
        "type": "polygon",
        "strokeWidth": 2,
        "stroke": "black",
        "fill": "rgba(255, 99, 71, 0.5)", # 기본 도형 채우기 색상 (투명도 포함)
        "points": initial_vertices
    }]
}

st.subheader("2. 캔버스에서 도형 변형하기 (클릭 & 드래그)")
st.info("캔버스에 도형이 나타납니다. 도형을 클릭한 뒤 점을 드래그하여 변형하거나, 도형 전체를 이동/회전할 수 있습니다.")

# 캔버스 컴포넌트
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # 캔버스에서 사용자가 그릴 때의 기본 채우기 색상
    stroke_width=2,
    stroke_color="black",
    background_color="#eee", # 캔버스 배경색
    height=canvas_height,
    width=canvas_width,
    drawing_mode="transform", # 'transform' 모드가 객체 변형, 이동, 회전에 적합
    initial_drawing=initial_canvas_drawing_data, # 수정된 초기 도형 데이터 전달
    key=f"canvas_tessellation_{shape_type}_{tile_size}_{st.session_state.get('rerun_counter', 0)}"
    # key에 `rerun_counter`를 추가하여 도형 선택 및 크기 변경 시 강제 리렌더링 유도
)

# `rerun_counter`를 증가시켜 캔버스 `key`가 변경되도록 합니다.
# 이렇게 하면 매번 앱이 실행될 때마다 캔버스가 '새롭게' 그려지면서 초기 도형을 불러오려 시도합니다.
if 'rerun_counter' not in st.session_state:
    st.session_state.rerun_counter = 0
st.session_state.rerun_counter += 1


# --- 변형된 도형 확정 ---
modified_vertices_from_canvas = None

# 캔버스에서 JSON 데이터가 넘어왔을 때만 처리
if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    if objects:
        # 캔버스에는 여러 객체가 있을 수 있으므로, polygon 타입의 마지막 객체를 찾습니다.
        polygon_object = None
        for obj in reversed(objects): # 가장 최근에 상호작용한 객체를 찾기 위해 역순으로 검색
            if obj.get("type") == "polygon":
                polygon_object = obj
                break
        
        if polygon_object and "points" in polygon_object:
            # 캔버스에서 받아온 꼭짓점 데이터를 Matplotlib용 numpy 배열로 변환
            modified_vertices_from_canvas = np.array(polygon_object["points"])
            
            # 변형된 도형을 사이드바에 미리보기
            st.sidebar.subheader("변형된 도형 미리보기 (캔버스 결과)")
            fig_preview, ax_preview = plt.subplots(figsize=(3,3))
            ax_preview.set_aspect('equal')
            ax_preview.axis('off')
            ax_preview.add_patch(Polygon(modified_vertices_from_canvas, closed=True,
                                        edgecolor='blue', facecolor='lightblue', lw=1))
            ax_preview.autoscale_view()
            st.sidebar.pyplot(fig_preview)
        else:
            st.sidebar.warning("캔버스에서 유효한 도형 데이터를 찾을 수 없습니다. 다시 시도해주세요.")
    else:
        st.sidebar.info("캔버스에 도형이 그려지지 않았습니다. 기본 도형을 선택하거나 도형을 그려주세요.")
else:
    st.sidebar.info("캔버스 데이터를 기다리는 중...")


# --- 테셀레이션 패턴 생성 설정 ---
st.sidebar.header("3. 테셀레이션 구성")

# 변형된 도형이 있어야만 테셀레이션 설정을 할 수 있도록
# 만약 캔버스에서 아무것도 받아오지 못했다면, 기본 정사각형으로라도 테셀레이션 시도 (안전장치)
final_base_vertices = modified_vertices_from_canvas
if final_base_vertices is None or len(final_base_vertices) == 0:
    st.warning("캔버스에서 변형된 도형을 가져오지 못했습니다. 기본 정사각형으로 테셀레이션을 시도합니다.")
    # 캔버스 크기를 고려하여 기본 도형 생성 (Matplotlib용)
    temp_vertices = get_initial_drawable_polygon_vertices("정사각형", tile_size, canvas_width, canvas_height)
    final_base_vertices = np.array(temp_vertices)


# 이제 항상 유효한 final_base_vertices를 가지고 진행
if final_base_vertices is not None and len(final_base_vertices) > 0:
    st.sidebar.write("이제 변형된 도형으로 테셀레이션 패턴을 만들어보세요.")
    rows = st.sidebar.slider("행 개수:", min_value=1, max_value=15, value=5, key="t_rows")
    cols = st.sidebar.slider("열 개수:", min_value=1, max_value=15, value=5, key="t_cols")

    st.sidebar.subheader("색상 설정")
    color1 = st.sidebar.color_picker("기본 색상 1:", "#FF6347", key="t_color1")
    color2 = st.sidebar.color_picker("보조 색상 2:", "#4682B4", key="t_color2")

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
    def create_tessellation_pattern(vertices, ref_tile_size, rows, cols, color1, color2, transform_type, rotation_angle):
        if vertices is None or len(vertices) == 0:
            return None

        min_x, min_y = np.min(vertices[:, 0]), np.min(vertices[:, 1])
        max_x, max_y = np.max(vertices[:, 0]), np.max(vertices[:, 1])
        
        shape_center_x = (min_x + max_x) / 2
        shape_center_y = (min_y + max_y) / 2

        x_step_grid = ref_tile_size
        y_step_grid = ref_tile_size
        
        if shape_type == "정삼각형":
            x_step_grid = ref_tile_size / 2
            y_step_grid = ref_tile_size * math.sqrt(3) / 2
        elif shape_type == "정육각형":
            x_step_grid = ref_tile_size * 1.5
            y_step_grid = ref_tile_size * math.sqrt(3)

        fig, ax = plt.subplots(figsize=(cols * x_step_grid / 70, rows * y_step_grid / 70))
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        for r in range(rows):
            for c in range(cols):
                offset_x_grid = c * x_step_grid
                offset_y_grid = r * y_step_grid

                if shape_type == "정육각형" and r % 2 != 0:
                    offset_x_grid += x_step_grid / 2
                elif shape_type == "정삼각형":
                    pass
                
                current_tile_vertices_base = np.copy(vertices)
                
                current_shape_center_x = np.mean(current_tile_vertices_base[:, 0])
                current_shape_center_y = np.mean(current_tile_vertices_base[:, 1])

                temp_vertices = current_tile_vertices_base - [current_shape_center_x, current_shape_center_y]

                if transform_type == "회전":
                    theta = np.radians(rotation_angle)
                    rotation_matrix = np.array([
                        [np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]
                    ])
                    temp_vertices = np.dot(temp_vertices, rotation_matrix.T)
                    
                elif transform_type == "대칭":
                    temp_vertices = temp_vertices * np.array([-1, 1])
                    
                final_vertices = temp_vertices + [current_shape_center_x, current_shape_center_y] + [offset_x_grid, offset_y_grid]

                face_color = color1 if (r + c) % 2 == 0 else color2
                polygon = Polygon(final_vertices, closed=True, edgecolor='black', facecolor=face_color, lw=1)
                ax.add_patch(polygon)

        ax.autoscale_view()
        ax.set_xlim(ax.get_xlim()[0] - x_step_grid/2, ax.get_xlim()[1] + x_step_grid/2)
        ax.set_ylim(ax.get_ylim()[0] - y_step_grid/2, ax.get_ylim()[1] + y_step_grid/2)

        return fig

    # --- 메인 화면에 테셀레이션 패턴 표시 ---
    st.subheader("생성된 테셀레이션 패턴")
    fig = create_tessellation_pattern(final_base_vertices, tile_size, rows, cols, color1, color2, transform_type, rotation_angle)
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
        st.warning("테셀레이션 패턴을 생성할 수 없습니다. 캔버스에서 도형을 제대로 변형했는지 확인해 보세요.")
else:
    st.info("캔버스 데이터를 기다리는 중이거나, 유효한 도형이 없습니다. 캔버스에 도형이 나타나지 않으면, 기본 도형 선택을 다시 하거나 앱을 새로고침 해보세요.")

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib, 그리고 streamlit-drawable-canvas를 사용하여 만들어졌습니다.")
