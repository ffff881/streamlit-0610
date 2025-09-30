# streamlit_translation_app.py
# 나만의 수학교과서: 도형의 평행이동 (Translation)
# 벡터 대신 x축, y축 방향 이동 설명 버전

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
def translate_point(pt, a, b):
    return np.array(pt) + np.array([a, b])


def plot_points(ax, pts, style='o', label=None, color=None):
    pts = np.array(pts)
    ax.plot(pts[:,0], pts[:,1], style, label=label)
    if len(pts) == 1:
        ax.annotate(f"{tuple(pts[0].round(2))}", (pts[0,0], pts[0,1]))


def plot_polygon(ax, poly, label=None, alpha=0.4, edgecolor='k'):
    poly = np.array(poly)
    patch = Polygon(poly, closed=True, alpha=alpha, edgecolor=edgecolor)
    ax.add_patch(patch)
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
    st.markdown("1. 점의 평행이동 시뮬레이션 → 2. 도형 평행이동 시뮬레이션 → 3. 수식 유도와 예제 → 4. 응용문제")

elif mode == "점의 평행이동":
    st.header("점의 평행이동")
    st.write("점 (x, y)를 x축으로 a만큼, y축으로 b만큼 옮기면 (x+a, y+b)가 됩니다.")

    col1, col2 = st.columns([1,1])
    with col1:
        x = st.number_input("x 좌표", value=1.0, format="%.3f")
        y = st.number_input("y 좌표", value=2.0, format="%.3f")
        a = st.slider("x축으로 이동할 거리 a", -5.0, 5.0, 1.0, step=0.1)
        b = st.slider("y축으로 이동할 거리 b", -5.0, 5.0, 0.5, step=0.1)
        st.write(f"이동 후 좌표는 ({x+a:.3f}, {y+b:.3f}) 입니다.")

    with col2:
        fig, ax = plt.subplots(figsize=(5,5))
        ax.set_aspect('equal')
        ax.axhline(0,
