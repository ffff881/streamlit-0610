import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 유리함수 & 무리함수 그래프 탐색기")
st.markdown("계수를 조절하여 함수의 그래프와 특징을 실시간으로 확인해보세요!")

# --- 함수 선택 라디오 버튼 ---
function_type = st.sidebar.radio(
    "어떤 함수를 탐색하시겠어요?",
    ("유리함수 (Rational Function)", "무리함수 (Irrational Function)")
)

# --- 유리함수 모드 ---
if function_type == "유리함수 (Rational Function)":
    st.header("유리함수 $y = \\frac{k}{x-p} + q$")
    st.markdown("`k`, `p`, `q` 값을 변경하여 그래프와 점근선을 확인해보세요.")

    # 사용자 입력: st.slider 대신 st.number_input 사용
    st.sidebar.subheader("유리함수 계수")
    k = st.sidebar.number_input("k 값", value=1.0, step=0.1, format="%.1f")
    p = st.sidebar.number_input("p 값 (수직 점근선)", value=0.0, step=0.1, format="%.1f")
    q = st.sidebar.number_input("q 값 (수평 점근선)", value=0.0, step=0.1, format="%.1f")

    # 그래프 데이터 생성
    x = np.linspace(-10, 10, 400)
    
    # 점근선 처리: p 주변에서 그래프가 끊어지도록 nan 값 사용
    # p 근처의 작은 구간을 제외하고 그래프를 그립니다.
    graph_x = np.concatenate((x[x < p - 0.01], x[x > p + 0.01]))
    graph_y = k / (graph_x - p) + q

    # Plotly 그래프 생성
    fig = go.Figure()

    # 유리함수 그래프
    fig.add_trace(go.Scatter(
        x=graph_x,
        y=graph_y,
        mode='lines',
        name=f'y = {k:.1f}/(x - {p:.1f}) + {q:.1f}',
        line=dict(color='blue', width=2)
    ))

    # 수직 점근선
    fig.add_trace(go.Scatter(
        x=[p, p],
        y=[min(graph_y) if len(graph_y) > 0 and not np.isnan(min(graph_y)) else -10, max(graph_y) if len(graph_y) > 0 and not np.isnan(max(graph_y)) else 10], # y축 범위에 맞춤
        mode='lines',
        name=f'수직 점근선 x = {p:.1f}',
        line=dict(color='red', width=1, dash='dash')
    ))

    # 수평 점근선
    fig.add_trace(go.Scatter(
        x=[min(x), max(x)],
        y=[q, q],
        mode='lines',
        name=f'수평 점근선 y = {q:.1f}',
        line=dict(color='green', width=1, dash='dash')
    ))

    # 레이아웃 설정
    fig.update_layout(
        title=f'유리함수: y = {k:.1f}/(x - {p:.1f}) + {q:.1f}',
        xaxis_title="x",
        yaxis_title="y",
        hovermode="x unified",
        height=600,
        showlegend=True,
        xaxis_range=[-10, 10], # x축 범위 고정
        yaxis_range=[-10, 10]  # y축 범위 고정
    )
    
    # 정의역/치역 정보
    st.subheader("함수 정보")
    st.write(f"**수직 점근선:** `x = {p:.1f}`")
    st.write(f"**수평 점근선:** `y = {q:.1f}`")
    st.write(f"**정의역:** $x \\neq {p:.1f}$ 인 모든 실수")
    st.write(f"**치역:** $y \\neq {q:.1f}$ 인 모든 실수")


# --- 무리함수 모드 (이전과 동일) ---
else: # function_type == "무리함수 (Irrational Function)"
    st.header("무리함수 $y = \\pm \\sqrt{ax+b} + c$")
    st.markdown("`a`, `b`, `c` 값과 부호를 변경하여 그래프와 시작점을 확인해보세요.")

    # 사용자 입력
    st.sidebar.subheader("무리함수 계수")
    sqrt_sign = st.sidebar.radio("루트 앞 부호", ("+", "-"))
    a = st.sidebar.number_input("a 값", value=1.0, step=0.1, format="%.1f")
    b = st.sidebar.number_input("b 값", value=0.0, step=0.1, format="%.1f")
    c = st.sidebar.number_input("c 값", value=0.0, step=0.1, format="%.1f")

    # 시작점 계산
    # ax + b >= 0 이므로 x >= -b/a (a>0) 또는 x <= -b/a (a<0)
    try:
        start_x = -b / a
    except ZeroDivisionError:
        st.warning("a 값이 0이면 무리함수가 아닙니다 (일차함수 형태). a를 0이 아닌 값으로 설정해주세요.")
        st.stop() # a가 0이면 앱 실행 중지

    start_y = c

    # 그래프 데이터 생성
    # 정의역 설정
    if a > 0:
        x_range = np.linspace(start_x, start_x + 10, 400) # 시작점부터 오른쪽으로
    else: # a < 0
        x_range = np.linspace(start_x - 10, start_x, 400) # 시작점부터 왼쪽으로

    # 음수 루트 방지 (정의역 밖의 값은 nan 처리)
    inner_sqrt = a * x_range + b
    y_range = np.where(inner_sqrt >= 0, np.sqrt(inner_sqrt), np.nan)
    
    if sqrt_sign == "-":
        y_range = -y_range
    
    y_range += c

    # Plotly 그래프 생성
    fig = go.Figure()

    # 무리함수 그래프
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_range,
