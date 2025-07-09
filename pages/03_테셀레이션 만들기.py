import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math
from io import BytesIO

# 필요한 경우, `streamlit_drawable_canvas` 임포트
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.title("✂️ 나만의 테셀레이션 만들기")
st.write("캔버스에서 도형을 직접 변형하고, 테셀레이션을 만들어 보세요!")

# --- 사이드바 설정 ---
st.sidebar.header("1. 기본 도형 선택")
shape_type = st.sidebar.selectbox("기본 정다각형 선택:", ["정사각형", "정삼각형", "정육각형"])
tile_size = st.sidebar.slider("캔버스 타일 기준 크기:", min_value=50, max_value=200, value=100, step=10)

# --- 기본 도형의 꼭짓점 정의 함수 (캔버스 중앙에 오도록 조정) ---
def get_initial_drawable_polygon_vertices(shape_type, size, canvas_width, canvas_height):
    vertices = []
    if shape_type == "정사각형":
        vertices = np.array([
            [-size/2, -size/2],
            [size/2, -size/2],
            [size/2, size/2],
            [-size/2, size/2]
        ])
    elif shape_type == "정삼각형":
        height = size * math.sqrt(3) / 2
        vertices = np.array([
            [-size/2, -height/2],
            [size/2, -height/2],
            [0, height/2]
        ])
    elif shape_type == "정육각형":
        angle_rad = np.radians(np.arange(0, 360, 60))
        vertices = np.array([
            [size * np.cos(a), size * np.sin(a)]
            for a in angle_rad
        ])

    # 캔버스 중앙으로 이동
    center_x, center_y = canvas_width / 2, canvas_height / 2
    vertices += [center_x, center_y]
    return vertices.tolist() # st_canvas는 list of list를 선호

# --- 캔버스 설정 ---
canvas_width = 600
canvas_height = 400

st.subheader("2. 캔버스에서 도형 변형하기 (클릭 & 드래그)")
st.info("시작하려면 캔버스에 도형이 나타납니다. 마우스로 꼭짓점을 드래그하여 변형해보세요.")

# 초기 도형 꼭짓점 설정 (세션 상태에 저장하여 도형 변경 시 초기화)
if 'initial_shape_drawn' not in st.session_state or st.session_state.initial_shape_drawn != shape_type:
    initial_vertices = get_initial_drawable_polygon_vertices(shape_type, tile_size, canvas_width, canvas_height)
    st.session_state.drawing = {
        "type": "polygon",
        "strokeWidth": 2,
        "stroke": "black",
        "fill": "rgba(255, 99, 71, 0.5)", # 기본 도형 채우기 색상
        "points": initial_vertices
    }
    st.session_state.initial_shape_drawn = shape_type
else:
    # 도형 타입이 바뀌지 않았다면 기존 상태 유지 (재로드 시 초기화 방지)
    if "drawing" not in st.session_state: # 첫 로드 시 예외처리
        initial_vertices = get_initial_drawable_polygon_vertices(shape_type, tile_size, canvas_width, canvas_height)
        st.session_state.drawing = {
            "type": "polygon",
            "strokeWidth": 2,
            "stroke": "black",
            "fill": "rgba(255, 99, 71, 0.5)",
            "points": initial_vertices
        }

# 캔버스 컴포넌트
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # 채우기 색상
    stroke_width=2,
    stroke_color="black",
    background_color="#eee",
    height=canvas_height,
    width=canvas_width,
    drawing_mode="transform", # 'transform' 모드가 객체 변형에 적합
    initial_drawing=st.session_state.drawing,
    key="canvas_tessellation"
)

# --- 변형된 도형 확정 ---
modified_vertices_from_canvas = None
if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    if objects:
        # 마지막으로 그려지거나 변형된 객체 (가장 최근에 상호작용한 객체)
        # 여러 객체가 있을 수 있으므로 실제 사용 시 더 정교한 로직 필요
        polygon_object = None
        for obj in reversed(objects): # 가장 최근 객체부터 확인
            if obj.get("type") == "polygon":
                polygon_object = obj
                break
        
        if polygon_object:
            # 캔버스 좌표를 Matplotlib 좌표계로 변환 (필요시)
            # st_canvas의 polygon points는 로컬 좌표가 아님
            # 캔버스의 scaleX, scaleY, left, top 등을 고려해야 하지만,
            # 간단한 드래그 변형이라면 points만으로도 가능성 있음.
            # 이 부분은 `streamlit-drawable-canvas`의 docs를 더 참고해야 합니다.
            # 지금은 임시로 points를 그대로 사용
            modified_vertices_from_canvas = np.array(polygon_object["points"])
            
            st.sidebar.subheader("변형된 도형 미리보기 (캔버스 결과)")
            # 캔버스에서 받아온 꼭짓점으로 Matplotlib에 그리기
            fig_preview, ax_preview = plt.subplots(figsize=(3,3))
            ax_preview.set_aspect('equal')
            ax_preview.axis('off')
            ax_preview.add_patch(Polygon(modified_vertices_from_canvas, closed=True,
                                        edgecolor='blue', facecolor='lightblue', lw=1))
            ax_preview.autoscale_view()
            st.sidebar.pyplot(fig_preview)

# --- 테셀레이션 생성 설정 ---
st.sidebar.header("3. 테셀레이션 구성")

# 변형된 도형이 있어야만 테셀레이션 설정을 할 수 있도록
if modified_vertices_from_canvas is not None and len(modified_vertices_from_canvas) > 0:
    st.sidebar.write("이제 변형된 도형으로 테셀레이션 패턴을 만들어보세요.")
    rows = st.sidebar.slider("행 개수:", min_value=1, max_value=15, value=5, key="t_rows")
    cols = st.sidebar.slider("열 개수:", min_value=1, max_value=15, value=5, key="t_cols")

    st.sidebar.subheader("색상 설정")
    color1 = st.sidebar.color_picker("기본 색상 1:", "#FF6347", key="t_color1")
    color2 = st.sidebar.color_picker("보조 색상 2:", "#4682B4", key="t_color2")

    st.sidebar.subheader("패턴 변환 옵션")
    # 사용자가 선택할 변환 유형
    transform_type = st.sidebar.radio(
        "테셀레이션 변환 방식:",
        ("평행이동", "회전", "대칭", "미끄럼 반사 (미구현)")
    )
    rotation_angle = 0
    if transform_type == "회전":
        rotation_angle = st.sidebar.slider("회전 각도 (도):", min_value=0, max_value=360, value=90, step=15, key="t_rot_angle")
        st.info("회전은 기본 도형이 '회전 대칭'이 될 때 평면을 완벽히 채울 수 있습니다.")
    elif transform_type == "대칭":
        st.info("대칭 변환은 현재 단순 복제 후 반전 처리됩니다.")
        # 대칭 축 선택 등을 추가할 수 있음
    elif transform_type == "미끄럼 반사 (미구현)":
        st.warning("미끄럼 반사 기능은 아직 구현되지 않았습니다.")


    # --- 테셀레이션 생성 및 시각화 함수 (이전 코드와 거의 동일, `vertices`만 변경) ---
    def create_tessellation_with_custom_shape(vertices, tile_size_ref, rows, cols, color1, color2, transform_type, rotation_angle):
        if vertices is None or len(vertices) == 0:
            st.error("유효한 도형 꼭짓점이 없습니다.")
            return None

        # 변형된 도형의 최소/최대 x,y 값을 사용하여 경계 상자 계산
        min_x, min_y = np.min(vertices[:, 0]), np.min(vertices[:, 1])
        max_x, max_y = np.max(vertices[:, 0]), np.max(vertices[:, 1])
        shape_width = max_x - min_x
        shape_height = max_y - min_y

        # 이 부분은 테셀레이션의 종류(정사각형, 삼각형, 육각형 기반)에 따라
        # 실제 평면을 채우는 간격과 오프셋을 정교하게 계산해야 합니다.
        # 여기서는 단순화를 위해 기본 사각형 간격을 사용하거나, 특정 도형에 대한 가정을 사용합니다.
        # 실제 테셀레이션 알고리즘은 변형된 도형의 '패턴 매칭'을 고려해야 합니다.

        # 임시 그리드 스텝 (가장 단순한 평행이동 가정)
        # 실제로는 변형된 도형의 너비/높이가 아니라, 테셀레이션에 필요한 "유효 공간"을 계산해야 합니다.
        # 예를 들어, 에셔처럼 한 변을 변형하면 반대편 변도 같아지는 경우
        # 이 부분은 가장 복잡하고, 어떤 테셀레이션 원리를 따르냐에 따라 크게 달라집니다.
        # 일단은 기본 타일 크기를 참고하여 대략적인 간격 설정
        
        # 기본 스텝:
        x_base_step = shape_width
        y_base_step = shape_height

        # 육각형의 경우, 특정 그리드 스텝 적용
        if shape_type == "정육각형":
            x_base_step = tile_size_ref * 1.5
            y_base_step = tile_size_ref * math.sqrt(3) / 2
        elif shape_type == "정삼각형":
            x_base_step = tile_size_ref / 2
            y_base_step = tile_size_ref * math.sqrt(3) / 2


        fig, ax = plt.subplots(figsize=(cols * x_base_step / 70, rows * y_base_step / 70))
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        for r in range(rows):
            for c in range(cols):
                current_tile_vertices = np.copy(vertices) # 캔버스에서 변형된 꼭짓점 사용
                
                # --- 평행이동 오프셋 계산 ---
                offset_x = c * x_base_step
                offset_y = r * y_base_step

                # 육각형 그리드 특수 처리
                if shape_type == "정육각형" and r % 2 != 0:
                    offset_x += x_base_step / 2
                # 정삼각형 그리드 특수 처리 (미구현)
                elif shape_type == "정삼각형":
                    # 정삼각형 그리드는 이보다 훨씬 복잡한 오프셋과 회전/반전 조합이 필요
                    # 여기서는 일단 간단한 직사각형 그리드처럼 배치 (완전한 테셀레이션 아님)
                    # st.warning("정삼각형 테셀레이션의 배치는 아직 완벽하지 않습니다.")
                    pass


                # 도형의 중심을 기준으로 모든 변환 적용
                # 캔버스 도형이 Matplotlib의 (0,0) 근처가 아닐 수 있으므로 min_x, min_y를 빼서 상대적인 위치로 변환
                # Matplotlib polygon은 절대 좌표를 사용.
                # 따라서 current_vertices는 캔버스에서 온 좌표 그대로를 사용하고,
                # 회전/대칭 등을 적용할 때 상대적 위치를 고려해야 함.

                # 현재 도형의 중심 (변환된 도형 자체의 중심)
                center_x = np.mean(current_tile_vertices[:, 0])
                center_y = np.mean(current_tile_vertices[:, 1])

                # 변형에 따라 도형의 '시작점'을 (0,0)으로 정규화
                # 캔버스에서 얻은 좌표는 절대 좌표이므로, 이를 Matplotlib에 맞게 변환해야 합니다.
                # 단순 평행이동은 캔버스 좌표 그대로 사용 가능.
                # 회전, 대칭 등은 도형의 상대적 중심을 기준으로 해야 정확함.
                
                # 모든 꼭짓점을 원점으로 임시 이동
                temp_vertices = current_tile_vertices - [center_x, center_y]

                # --- 선택된 변환 방식 적용 ---
                if transform_type == "회전":
                    theta = np.radians(rotation_angle)
                    rotation_matrix = np.array([
                        [np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]
                    ])
                    temp_vertices = np.dot(temp_vertices, rotation_matrix.T)
                    
                elif transform_type == "대칭":
                    # 간단한 Y축 대칭 (수직 축 대칭)
                    temp_vertices = temp_vertices * np.array([-1, 1]) # X축 뒤집기
                    
                # 다시 원래 위치로 (테셀레이션 그리드 위치 + 도형 중심)
                final_vertices = temp_vertices + [center_x, center_y] + [offset_x, offset_y]


                face_color = color1 if (r + c) % 2 == 0 else color2
                polygon = Polygon(final_vertices, closed=True, edgecolor='black', facecolor=face_color, lw=1)
                ax.add_patch(polygon)

        ax.autoscale_view()
        # 여백 추가
        ax.set_xlim(ax.get_xlim()[0] - x_base_step/2, ax.get_xlim()[1] + x_base_step/2)
        ax.set_ylim(ax.get_ylim()[0] - y_base_step/2, ax.get_ylim()[1] + y_base_step/2)

        return fig

    # --- 메인 화면에 테셀레이션 표시 ---
    st.subheader("생성된 테셀레이션 패턴")
    fig = create_tessellation_with_custom_shape(modified_vertices_from_canvas, tile_size, rows, cols, color1, color2, transform_type, rotation_angle)
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
    st.info("먼저 캔버스에서 도형을 변형하여 확정해 주세요.")

st.markdown("---")
st.info("이 도구는 Python의 Streamlit과 Matplotlib, 그리고 streamlit-drawable-canvas를 사용하여 만들어졌습니다.")
