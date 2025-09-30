# streamlit_translation_app.py
# 나만의 수학교과서: 도형의 평행이동 (Translation)
# 사용법:
# 1) 가상환경 활성화 후: pip install streamlit matplotlib numpy
# 2) 실행: streamlit run streamlit_translation_app.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

st.set_page_config(page_title="도형의 평행이동 교과서", layout="wide")

# 헤더
st.title("도형의 평행이동 — 인터랙티브 교과서")
st.markdown("간단한 인터랙션으로 **점의 평행이동**과 **도형의 평행이동** 개념을 배우고, 방정식 유도 과정을 단계별로 확인합니다.")

# 사이드바: 선택
st.sidebar.header("설정")
mode = st.sidebar.radio("보여줄 내용 선택", ("개요", "점의 평행이동", "도형의 평행이동", "비교 및 유도", "예제 따라하기"))

# 유틸 함수

def translate_point(pt, t):
    """pt: (x,y) or array shape (n,2); t: (tx,ty)"""
    return np.array(pt) + np.array(t)


def plot_points(ax, pts, style='o', label=None, color=None):
    pts = np.array(pts)
    ax.plot(pts[:,0], pts[:,1], style, label=label)
    if len(pts) == 1:
        ax.annotate(f"{tuple(pts[0].round(2))}", (pts[0,0], pts[0,1]))


def plot_polygon(ax, poly, label=None, alpha=0.4, edgecolor='k'):
    poly = np.array(poly)
    patch = Polygon(poly, closed=True, alpha=alpha, edgecolor=edgecolor)
    ax.add_patch(patch)
    # annotate vertices
    for i,(x,y) in enumerate(poly):
        ax.text(x, y, f"({x:.1f},{y:.1f})", fontsize=9)

# 콘텐츠
if mode == "개요":
    st.header("학습 목표")
    st.write("""
- 점의 평행이동 개념을 이해한다.
- 점의 평행이동과 도형의 평행이동의 공통점과 차이점을 설명할 수 있다.
- 간단한 예제로 직접 확인한다.
- 평행이동의 방정식을 유도하고 해석할 수 있다.
    """)
    st.subheader("학습 흐름")
    st.markdown("1. 점의 평행이동 시뮬레이션 → 2. 도형(다각형) 평행이동 시뮬레이션 → 3. 수식 유도와 예제 → 4. 응용문제")

elif mode == "점의 평행이동":
    st.header("점의 평행이동 (Point Translation)")
    st.write("점 (x, y)를 벡터 (t_x, t_y)만큼 이동시키면 새로운 점은 (x + t_x, y + t_y)입니다.")

    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("원래 점 설정")
        x = st.number_input("x 좌표", value=1.0, format="%.3f")
        y = st.number_input("y 좌표", value=2.0, format="%.3f")
        st.subheader("이동 벡터")
        tx = st.slider("t_x", -5.0, 5.0, 1.0, step=0.1)
        ty = st.slider("t_y", -5.0, 5.0, 0.5, step=0.1)
        st.write(f"이동 후 좌표는 ({x+tx:.3f}, {y+ty:.3f}) 입니다.")

    with col2:
        fig, ax = plt.subplots(figsize=(5,5))
        ax.set_aspect('equal')
        ax.axhline(0, linewidth=0.5); ax.axvline(0, linewidth=0.5)
        ax.set_xlim(min(x, x+tx)-2, max(x, x+tx)+2)
        ax.set_ylim(min(y, y+ty)-2, max(y, y+ty)+2)
        plot_points(ax, [(x,y)], style='o', label='원래 점')
        plot_points(ax, [(x+tx,y+ty)], style='o', label='이동된 점')
        # 화살표
        ax.arrow(x, y, tx, ty, head_width=0.12, length_includes_head=True)
        ax.legend()
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("수식적 표현")
    st.latex(r"(x,y)\mapsto (x+t_x,\; y+t_y)")
    st.write("행렬/벡터로 표현하면:")
    st.latex(r"\begin{pmatrix}x'\\y'\end{pmatrix}=\begin{pmatrix}x\\y\end{pmatrix}+\begin{pmatrix}t_x\\t_y\end{pmatrix}")

elif mode == "도형의 평행이동":
    st.header("도형의 평행이동 (Polygon Translation)")
    st.write("도형의 각 꼭짓점에 같은 이동 벡터를 더하면 도형 전체가 평행이동합니다.")

    # 프리셋 폴리곤
    preset = st.selectbox("다각형 선택", ("삼각형", "정사각형", "오각형", "사용자 입력"))
    if preset == "삼각형":
        poly = np.array([[0,0],[2,0],[1,1.5]])
    elif preset == "정사각형":
        poly = np.array([[0,0],[2,0],[2,2],[0,2]])
    elif preset == "오각형":
        theta = np.linspace(0,2*np.pi,6)[:-1]
        poly = np.column_stack((np.cos(theta), np.sin(theta))) * 1.5
    else:
        st.write("쉼표로 구분하여 좌표 입력 (예: 0,0; 2,0; 1,1.5)")
        user_in = st.text_area("좌표 입력", value="0,0; 2,0; 1,1.5")
        try:
            poly = np.array([[float(c) for c in pair.split(',')] for pair in user_in.split(';')])
        except:
            st.error("입력 형식 오류 — 기본 삼각형 사용")
            poly = np.array([[0,0],[2,0],[1,1.5]])

    tx = st.slider("t_x", -5.0, 5.0, 1.0, step=0.1, key='poly_tx')
    ty = st.slider("t_y", -5.0, 5.0, 0.5, step=0.1, key='poly_ty')
    t = (tx, ty)
    poly_t = translate_point(poly, t)

    col1, col2 = st.columns([1,1])
    with col1:
        fig, ax = plt.subplots(figsize=(5,5))
        ax.set_aspect('equal')
        allx = np.concatenate([poly[:,0], poly_t[:,0]])
        ally = np.concatenate([poly[:,1], poly_t[:,1]])
        ax.set_xlim(allx.min()-1, allx.max()+1)
        ax.set_ylim(ally.min()-1, ally.max()+1)
        plot_polygon(ax, poly, label='원래 도형', alpha=0.3, edgecolor='blue')
        plot_polygon(ax, poly_t, label='이동된 도형', alpha=0.3, edgecolor='red')
        # 선으로 대응점 연결
        for p,q in zip(poly, poly_t):
            ax.plot([p[0],q[0]],[p[1],q[1]], linestyle='--', linewidth=0.7)
        ax.legend(["원래 도형","이동된 도형"]) 
        st.pyplot(fig)
    with col2:
        st.subheader("정점 목록")
        st.write("원래:")
        st.write(poly.round(3).tolist())
        st.write("이동 후:")
        st.write(poly_t.round(3).tolist())

    st.markdown("---")
    st.subheader("성질 요약")
    st.write("""
- 길이와 각은 변하지 않습니다 (등거리 유지).
- 두 도형은 서로 대응하는 점들 사이의 벡터가 모두 동일합니다.
- 회전·성장(스케일)과 달리, 평행이동은 원점을 기준으로 하지 않고 모든 점에 같은 벡터를 더합니다.
    """)

elif mode == "비교 및 유도":
    st.header("점 ↔ 도형의 평행이동: 공통점과 차이점")
    st.write("""
**공통점**
- 변환이 모든 점에 대해 같은 벡터 (t_x, t_y)를 더하는 연산이다.
- 거리·각·도형의 형태를 보존한다 (이것은 등거리 변환, isometry의 하나이다).

**차이점**
- 점은 단일 좌표의 변화로 끝나지만, 도형은 각 꼭짓점마다 같은 연산을 적용해야 한다.
- 도형의 평행이동은 꼭짓점들의 리스트(배열)를 다루므로 구현 측면에서는 벡터화가 유리하다.
    """)

    st.subheader("도형 평행이동 방정식 유도")
    st.write("점 (x,y)를 이동시키는 단순 유도:")
    st.latex(r"x'=x+t_x,\quad y'=y+t_y")
    st.write("도형의 모든 정점 (x_i,y_i)에 대해 동일하게 적용하면:")
    st.latex(r"x_i'=x_i+t_x,\quad y_i'=y_i+t_y\quad(\forall i)")
    st.write("행렬/벡터 관점:")
    st.latex(r"\mathbf{x}'=\mathbf{x}+\mathbf{t},\quad \mathbf{t}=\begin{pmatrix}t_x\\t_y\end{pmatrix}")

    st.markdown("---")
    st.subheader("참고: 동차좌표(Homogeneous coordinates)로 표현하면")
    st.write("동차좌표를 쓰면 평행이동을 3x3 행렬로 표현할 수 있어 다른 변환(회전·스케일·전단)과 합성하기 편합니다.")
    st.latex(r"\begin{pmatrix}x'\\y'\\1\end{pmatrix} = \begin{pmatrix}1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1\end{pmatrix} \begin{pmatrix}x\\y\\1\end{pmatrix}")

elif mode == "예제 따라하기":
    st.header("간단 예제: 정삼각형을 (2,1)만큼 옮기기")
    st.write("원래 정삼각형 좌표와 이동 후 좌표를 직접 계산하고 시각화합니다.")
    tri = np.array([[0,0],[2,0],[1,1.732]])
    t = (2.0, 1.0)
    tri_t = translate_point(tri, t)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("계산")
        st.write("원래 정점:")
        st.write(tri.tolist())
        st.write("이동 벡터: (2,1)")
        st.write("이동 후 정점:")
        st.write(tri_t.tolist())
    with col2:
        fig, ax = plt.subplots(figsize=(5,5))
        ax.set_aspect('equal')
        plot_polygon(ax, tri, label='원래')
        plot_polygon(ax, tri_t, label='이동')
        for p,q in zip(tri, tri_t):
            ax.plot([p[0],q[0]],[p[1],q[1]], linestyle='--')
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("따라하기 문제")
    st.write("도형을 (t_x, t_y) = (-1.5, 0.7)만큼 이동했을 때 새로운 꼭짓점 좌표를 계산하세요. 직접 입력해보고 맞는지 확인해보세요.")
    user_answer = st.text_input("새로운 좌표(세 점): 예: x1,y1; x2,y2; x3,y3", value="")
    if user_answer:
        try:
            ans = np.array([[float(c) for c in pair.split(',')] for pair in user_answer.split(';')])
            if ans.shape == tri_t.shape and np.allclose(ans, tri_t, atol=1e-3):
                st.success("정답입니다! 🎉")
            else:
                st.error("정답과 다릅니다. 이동 후 좌표는 아래를 확인하세요.")
                st.write(tri_t.tolist())
        except Exception as e:
            st.error("입력 형식을 확인하세요. 예: 2.0,1.0; 3.0,1.0; 2.5,2.732")

# 하단: 배포 및 깃허브 안내 (항상 표시)
st.markdown("---")
st.subheader("배포 & 깃허브 안내")
st.markdown("""
- 로컬 실행: `pip install streamlit matplotlib numpy` 후 `streamlit run streamlit_translation_app.py`
- 깃허브 업로드: 새 리포지토리를 만들고 이 파일을 커밋하세요.
- Streamlit Cloud에 배포하려면 깃허브 리포지토리를 연결하면 자동으로 배포됩니다.

원하시면 깃허브용 README와 Streamlit Cloud에 올리는 방법까지 같이 만들어 드릴게요.
""")

# End of file
