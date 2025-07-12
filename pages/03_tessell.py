import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math
from io import BytesIO

# 필요한 라이브러리: pip install streamlit numpy matplotlib streamlit-drawable-canvas
from streamlit_drawable_canvas import st_canvas

# --- Streamlit 앱 기본 설정 ---
st.set_page_config(layout="wide")
st.title("✂️ 나만의 테셀레이션 만들기 (캔버스 버전)")
st.write("캔버스에서 도형을 직접 변형하고 꾸민 후, 테셀레이션 패턴을 만들어 보세요!")

# --- 캔버스 설정 ---
canvas_width = 700
canvas_height = 500
stroke_width = 2
stroke_color = "black"
background_color = "#eee" # 캔버스 배경색

# --- 기본 도형의 꼭짓점 정의 함수 (캔버스 중앙에 오도록 조정) ---
# 이 함수는 항상 list of lists를 반환합니다.
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
        vertices = vertices_np.tolist()
    
    # 캔버스 중앙으로 이동
    center_x, center_y = canvas_width / 2, canvas_height / 2
    vertices_shifted = [[v[0] + center_x, v[1] + center_y] for v in vertices]
    
    return vertices_shifted

# --- 사이드바: 1. 기본 도형 선택 ---
st.sidebar.header("1. 기본 도형 선택")
selected_shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"], key="shape_select")
selected_tile_size = st.sidebar.slider("캔버스 타일 기준 크기:", min_value=50, max_value=250, value=150, step=10, key="tile_size_select")

# --- 캔버스에 초기 도형 그리기 위한 데이터 생성 및 캐싱 ---
# `st.cache_data`를 사용하여 매번 재계산하지 않도록 최적화 (성능 향상)
@st.cache_data(show_spinner=False)
def get_cached_initial_drawing_data(current_shape_type, current_tile_size, c_width, c_height):
    verts = get_initial_drawable_polygon_vertices(current_shape_type, current_tile_size, c_width, c_height)
    
    # 초기 도형의 채우기/테두리 색상과 두께를 명확하게 설정
    return {
        "objects": [{
            "type": "polygon",
            "strokeWidth": 5, # 테두리 두께 강조
            "stroke": "blue", # 테두리 색상 강조
            "fill": "yellow", # 채우기 색상 강조 (불투명)
            "points": verts
        }]
    }

# --- 캔버스 초기화 로직 (사이드바 선택 변경 시 캔버스 초기화) ---
# 세션 상태를 사용하여 마지막으로 선택된 도형과 크기를 추적합니다.
if 'last_selected_shape' not in st.session_state:
    st.session_state.last_selected_shape = selected_shape_type
    st.session_state.last_selected_size = selected_tile_size
    st.session_state.initial_canvas_data = get_cached_initial_drawing_data(selected_shape_type, selected_tile_size, canvas_width, canvas_height)
elif (st.session_state.last_selected_shape != selected_shape_type or
      st.session_state.last_selected_size != selected_tile_size):
    st.session_state.initial_canvas_data = get_cached_initial_drawing_data(selected_shape_type, selected_tile_size, canvas_width, canvas_height)
    st.session_state.last_selected_shape = selected_shape_type
    st.session_state.last_selected_size = selected_tile_size
    # 선택이 바뀌면 "도형 확정" 상태도 리셋
    if 'confirmed_polygon_vertices' in st.session_state:
        del st.session_state['confirmed_polygon_vertices']
    if 'canvas_drawn_objects' in st.session_state:
        del st.session_state['canvas_drawn_objects']


# --- 메인 섹션: 2. 캔버스에서 도형 변형 및 꾸미기 ---
st.subheader("2. 캔버스에서 도형 변형 및 꾸미기")
st.info("캔버스에 노란색 도형이 나타납니다. 도형을 클릭하여 점을 드래그해 변형하거나, 도형 전체를 이동/회전할 수 있습니다.")

# 그리기 모드 선택 (변형 vs. 자유 그리기)
drawing_mode_select = st.radio(
    "그리기 모드 선택:",
    ("도형 변형 (Transform)", "자유 그리기 (Freedraw)"),
    key="drawing_mode_radio"
)
current_drawing_mode = "transform" if drawing_mode_select == "도형 변형 (Transform)" else "freedraw"

# 캔버스 컴포넌트 렌더링
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)" if current_drawing_mode == "freedraw" else "rgba(0,0,0,0)", # 그리기 모드일 때 채우기 색상
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=background_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=current_drawing_mode, # 선택된 그리기 모드 적용
    initial_drawing=st.session_state.initial_canvas_data, # 세션 상태에서 초기 데이터 로드
    key=f"drawable_canvas_{selected_shape_type}_{selected_tile_size}_{current_drawing_mode}" # key를 동적으로 변경하여 강제 리렌더링
)

# --- 도형 확정 버튼 ---
if st.button("캔버스 도형 확정 (테셀레이션 시작)", key="confirm_shape_button"):
    if canvas_result.json_data is not None and "objects" in canvas_result.json_data:
        # 마지막으로 그려지거나 변형된 객체 (가장 최근에 상호작용한 객체)
        # 여러 객체가 있을 수 있으므로 polygon 타입의 객체를 찾습니다.
        polygon_object = None
        for obj in reversed(canvas_result.json_data["objects"]):
            if obj.get("type") == "polygon":
                polygon_object = obj
                break
        
        # 자유 그리기로 그린 선들도 함께 저장 (꾸미기 정보)
        drawn_lines = [obj for obj in canvas_result.json_data["objects"] if obj.get("type") == "path" or obj.get("type") == "line"]

        if polygon_object and "points" in polygon_object:
            st.session_state.confirmed_polygon_vertices = np.array(polygon_object["points"])
            st.session_state.canvas_drawn_objects = drawn_lines # 꾸민 선들 저장
            st.success("도형이 성공적으로 확정되었습니다! 사이드바에서 테셀레이션 설정을 진행하세요.")
        else:
            st.error("캔버스에서 유효한 도형을 찾을 수 없습니다. 도형을 변형하거나 그려주세요.")
    else:
        st.error("캔버스 데이터가 비어 있습니다. 도형을 변형하거나 그려주세요.")
else:
    st.info("캔버스에서 도형을 변형하거나 그린 후 '캔버스 도형 확정' 버튼을 눌러주세요.")

# --- 사이드바: 3. 테셀레이션 구성 ---
st.sidebar.header("3. 테셀레이션 구성")

# '확정된 도형'이 있을 때만 테셀레이션 구성 옵션을 보여줍니다.
if 'confirmed_polygon_vertices' in st.session_state and st.session_state.confirmed_polygon_vertices is not None:
    final_base_vertices = st.session_state.confirmed_polygon_vertices
    canvas_drawn_objects = st.session_state.canvas_drawn_objects # 저장된 꾸미기 선들

    st.sidebar.write("확정된 도형으로 테셀레이션 패턴을 만들어보세요.")
    rows = st.sidebar.slider("행 개수:", min_value=1, max_value=10, value=5, key="t_rows")
    cols = st.sidebar.slider("열 개수:", min_value=1, max_value=10, value=5, key="t_cols")

    st.sidebar.subheader("색상 설정")
    color1 = st.sidebar.color_picker("기본 색상 1:", "#FF6347", key="t_color1") # Tomato
    color2 = st.sidebar.color_picker("보조 색상 2:", "#4682B4", key="t_color2") # SteelBlue

    st.sidebar.subheader("패턴 변환 옵션")
    transform_type = st.sidebar.radio(
        "테셀레이션 변환 방식:",
        ("평행이동", "회전", "대칭", "미끄럼 반사 (미구현)"),
        key="transform_select"
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
    def create_tessellation_pattern(vertices, ref_tile_size, rows, cols, color1, color2, transform_type, rotation_angle, current_shape_type, drawn_objects_data):
        if vertices is None or len(vertices) == 0:
            return None

        # 변형된 도형의 경계 상자 계산 (Matplotlib에 그릴 때 사용할 기준)
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
                
                # 2. 도형 꼭짓점 복사 (캔버스에서 넘어온 변형된 꼭짓점)
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

                # 7. 꾸민 선들 복제 및 추가
                # 꾸민 선들은 도형의 변형 및 위치에 맞춰 변환되어야 합니다.
                # 이는 캔버스 좌표와 Matplotlib 좌표, 그리고 변환 행렬을 정확히 이해해야 합니다.
                # 여기서는 기본적인 스케일과 오프셋만 적용하며, 회전/대칭은 복잡하므로 고려하지 않습니다.
                for drawn_obj in drawn_objects_data:
                    if drawn_obj["type"] == "path" and "path" in drawn_obj: # 자유 드로잉 패스
                        # 캔버스상의 drawn_obj의 (left, top, scaleX, scaleY, angle 등) 속성을
                        # Matplotlib 좌표계로 변환해야 하지만 매우 복잡합니다.
                        # 여기서는 단순 평행이동만 적용합니다.
                        
                        # 캔버스상의 도형 위치를 Matplotlib의 원점 (0,0)으로 이동시킨 기준점
                        # 그리고 이를 다시 최종 위치로 옮기는 방식이 필요합니다.
                        
                        # drawn_obj의 path 데이터를 직접 Matplotlib Path로 변환하는 것은 복잡합니다.
                        # 일단은 꾸미는 기능이 단순 선 추가라는 가정 하에 생략합니다.
                        pass # 현재는 꾸미기 선 그리는 부분은 구현 복잡성으로 인해 생략.
                             # Matplotlib에서 `Line2D`나 `Path`를 사용해야 함.


        # Matplotlib 축 범위 자동 조정 및 여백 추가
        ax.autoscale_view()
        ax.set_xlim(ax.get_xlim()[0] - x_step_grid/2, ax.get_xlim()[1] + x_step_grid/2)
        ax.set_ylim(ax.get_ylim()[0] - y_step_grid/2, ax.get_ylim()[1] + y_step_grid/2)

        return fig

    # --- 메인 화면에 테셀레이션 패턴 표시 ---
    st.subheader("생성된 테셀레이션 패턴")
    fig = create_tessellation_pattern(final_base_vertices, selected_tile_size, rows, cols, color1, color2, transform_type, rotation_angle, selected_shape_type, canvas_drawn_objects)
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
        st.warning("테셀레이션 패턴을 생성할 수 없습니다. 도형 확정을 눌렀는지 확인해 보세요.")
else:
    st.info("캔버스에서 도형을 변형하거나 그린 후 '캔버스 도형 확정' 버튼을 눌러 테셀레이션을 시작하세요.")

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib, 그리고 streamlit-drawable-canvas를 사용하여 만들어졌습니다.")
