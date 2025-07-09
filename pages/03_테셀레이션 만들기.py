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
canvas_width = 700
canvas_height = 500

# --- 기본 도형의 꼭짓점 정의 함수 (캔버스 중앙에 오도록 조정) ---
def get_initial_drawable_polygon_vertices(shape_type, size, canvas_width, canvas_height):
    vertices = []
    # 도형의 중심을 (0,0)으로 일단 설정
    if shape_type == "정사각형":
        vertices = np.array([
            [-size / 2, -size / 2],
            [size / 2, -size / 2],
            [size / 2, size / 2],
            [-size / 2, size / 2]
        ])
    elif shape_type == "정삼각형":
        height = size * math.sqrt(3) / 2
        vertices = np.array([
            [-size / 2, -height / 2],
            [size / 2, -height / 2],
            [0, height / 2]
        ])
    elif shape_type == "정육각형":
        angle_rad = np.radians(np.arange(0, 360, 60))
        vertices = np.array([
            [size * np.cos(a), size * np.sin(a)]
            for a in angle_rad
        ])
    
    # 캔버스 중앙으로 이동
    center_x, center_y = canvas_width / 2, canvas_height / 2
    vertices_shifted = vertices + [center_x, center_y]
    
    return vertices_shifted.tolist() # st_canvas는 list of list를 선호

# --- 사이드바 설정 ---
st.sidebar.header("1. 기본 도형 선택")
shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"])
tile_size = st.sidebar.slider("캔버스 타일 기준 크기:", min_value=50, max_value=200, value=100, step=10)

# --- 캔버스에 초기 도형 그리기 위한 세션 상태 관리 ---
# 'initial_drawing_data_for_canvas' 키를 사용하여 캔버스에 전달될 최종 데이터를 저장
# 이 데이터는 Streamlit이 리로드될 때마다 재사용될 수 있도록 합니다.

# 도형 타입이나 크기가 변경되었는지 확인하는 플래그
should_reinitialize_canvas = False
if 'last_shape_type' not in st.session_state or \
   st.session_state.last_shape_type != shape_type or \
   'last_tile_size' not in st.session_state or \
   st.session_state.last_tile_size != tile_size:
    
    should_reinitialize_canvas = True
    st.session_state.last_shape_type = shape_type
    st.session_state.last_tile_size = tile_size
    
    initial_vertices = get_initial_drawable_polygon_vertices(shape_type, tile_size, canvas_width, canvas_height)
    
    # `streamlit-drawable-canvas`는 `initial_drawing`에 {"objects": [...]} 형태를 기대함.
    st.session_state.initial_drawing_data_for_canvas = {
        "objects": [{
            "type": "polygon",
            "strokeWidth": 2,
            "stroke": "black",
            "fill": "rgba(255, 99, 71, 0.5)", # 기본 도형 채우기 색상 (투명도 포함)
            "points": initial_vertices
        }]
    }
# else: 도형 타입이나 크기 변경이 없으면 기존 `st.session_state.initial_drawing_data_for_canvas` 유지

st.subheader("2. 캔버스에서 도형 변형하기 (클릭 & 드래그)")
st.info("캔버스에 도형이 나타납니다. 도형을 클릭한 뒤 점을 드래그하여 변형하거나, 도형 전체를 이동/회전할 수 있습니다.")

# 캔버스 컴포넌트
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # 채우기 색상 (캔버스 배경과 구분)
    stroke_width=2,
    stroke_color="black",
    background_color="#eee", # 캔버스 배경색
    height=canvas_height,
    width=canvas_width,
    drawing_mode="transform", # 'transform' 모드가 객체 변형, 이동, 회전에 적합
    initial_drawing=st.session_state.initial_drawing_data_for_canvas, # 이 부분이 중요!
    key="canvas_tessellation" + shape_type + str(tile_size) # key를 동적으로 변경하여 캔버스 강제 재렌더링
)

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
    # 캔버스의 (0,0)은 좌상단, Matplotlib은 좌하단이 일반적이므로 Y축을 뒤집거나 오프셋을 조절해야 함
    # 여기서는 단순화를 위해 캔버스 좌표를 그대로 사용
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

        # 변형된 도형의 경계 상자 계산 (Matplotlib에 그릴 때 사용할 기준)
        min_x, min_y = np.min(vertices[:, 0]), np.min(vertices[:, 1])
        max_x, max_y = np.max(vertices[:, 0]), np.max(vertices[:, 1])
        # shape_width = max_x - min_x # 실제 변형된 도형의 너비
        # shape_height = max_y - min_y # 실제 변형된 도형의 높이
        
        # 도형의 중심 (회전/대칭 기준)
        shape_center_x = (min_x + max_x) / 2
        shape_center_y = (min_y + max_y) / 2

        # 그리드 간격: 캔버스에서 도형이 변형되었더라도,
        # 테셀레이션은 '원래 어떤 도형을 기반으로 했는지'에 따라 격자 간격이 결정됩니다.
        # 따라서 `ref_tile_size` (슬라이더로 조절하는 기준 크기)와 `shape_type`을 활용합니다.
        
        x_step_grid = ref_tile_size
        y_step_grid = ref_tile_size
        
        if shape_type == "정삼각형":
            x_step_grid = ref_tile_size / 2 # 한 칸 너비 (가로로 겹침)
            y_step_grid = ref_tile_size * math.sqrt(3) / 2 # 높이
        elif shape_type == "정육각형":
            x_step_grid = ref_tile_size * 1.5 # 육각형 가로 간격 (센터 투 센터)
            y_step_grid = ref_tile_size * math.sqrt(3) # 육각형 세로 간격 (두 행에 걸쳐)


        # Matplotlib Figure 및 Axes 설정
        fig, ax = plt.subplots(figsize=(cols * x_step_grid / 70, rows * y_step_grid / 70))
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        for r in range(rows):
            for c in range(cols):
                # 1. 초기 위치 오프셋 계산 (그리드 배치)
                offset_x_grid = c * x_step_grid
                offset_y_grid = r * y_step_grid

                # 정육각형 및 정삼각형 그리드 특수 오프셋
                if shape_type == "정육각형" and r % 2 != 0:
                    offset_x_grid += x_step_grid / 2 # 홀수 행은 반 칸 이동하여 벌집 모양 형성
                elif shape_type == "정삼각형":
                    # 정삼각형은 복잡하여 추후 정교한 구현 필요 (현재는 단순 사각형 격자처럼)
                    pass
                
                # 2. 도형 꼭짓점 복사 (캔버스에서 넘어온 변형된 꼭짓점)
                current_tile_vertices_base = np.copy(vertices)
                
                # 3. 도형의 로컬 중심 (변환의 기준점)
                # 캔버스에서 온 vertices는 캔버스 기준의 절대 좌표이므로,
                # 회전/대칭을 적용하려면 도형의 '현재' 중심을 기준으로 해야 합니다.
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
                    # X좌표만 -1을 곱하여 반전시킵니다.
                    temp_vertices = temp_vertices * np.array([-1, 1])
                    
                # 5. 최종 위치로 이동 (변환된 도형 + 그리드 오프셋)
                # 원점 이동했던 것을 다시 되돌리고, 그리드 오프셋을 더합니다.
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
    fig = create_tessellation_pattern(final_base_vertices, tile_size, rows, cols, color1, color2, transform_type, rotation_angle)
    if fig:
        st.pyplot(fig)
        # 이미지 다운로드 버튼
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
