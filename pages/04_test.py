import streamlit as st
import matplotlib.pyplot as plt

st.title("도형의 평행이동 학습하기")

st.markdown("""
점 (x, y)을 **x축 방향으로 a만큼, y축 방향으로 b만큼** 옮기면  
새 좌표는 (x+a, y+b)가 됩니다.

도형의 평행이동은 모든 꼭짓점을 똑같이 옮기는 것입니다.
""")

# 평행이동 값 입력
a = st.slider("x축 방향 이동 (a)", -5, 5, 2)
b = st.slider("y축 방향 이동 (b)", -5, 5, 3)

# 원래 도형 (정사각형)
original_shape = [(0,0), (2,0), (2,2), (0,2), (0,0)]

# 이동된 도형
moved_shape = [(x+a, y+b) for (x,y) in original_shape]

# 그래프 그리기
fig, ax = plt.subplots()
ox, oy = zip(*original_shape)
mx, my = zip(*moved_shape)

ax.plot(ox, oy, "bo-", label="원래 도형")
ax.plot(mx, my, "ro-", label="이동된 도형")

ax.set_aspect("equal", "box")
ax.set_xlim(-1, 8)
ax.set_ylim(-1, 8)
ax.grid(True)
ax.legend()

st.pyplot(fig)
