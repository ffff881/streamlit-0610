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

# --- 유리함수 모드 (이전과 동일) ---
if function_type == "유리함수 (Rational Function)":
    st.header("유리함수 $y = \\frac{k}{x-p} + q$")
    st.markdown("`k`, `p`, `q` 값을 변경하여 그래프와 점근선을 확인해보세요.")

    # 사용자 입력: k, p, q 값
    st.sidebar.subheader("유리함수 계수")
    k = st.sidebar.number_input("k 값", value=1.0, step=0.1, format="%.1f")
    p = st.sidebar.number_input("p 값 (수직 점근선 관련)", value=0.0, step=0.1, format="%.1f")
    q = st.sidebar.number_input("q 값 (수평 점근선 관련)", value=0.0, step=0.1, format="%.1f")

    # 그래프 데이터 생성
    x = np.linspace(-10, 10, 400)
    
    # 점근선 처리: p 주변에서 그래프가 끊어지도록 nan 값 사용
    graph_x_segment1 = x[x < p - 0.01]
    graph_y_segment1 = k / (graph_x_segment1 - p) + q
    
    graph_x_segment2 = x[x > p + 0.01]
    graph_y_segment2 = k / (graph_x_segment2 - p) + q

    # Plotly 그래프 생성
    fig = go.Figure()

    # 유리함수 그래프 (두 부분으로 나눠서 그립니다)
    fig.add_trace(go.Scatter(
        x=graph_x_segment1,
        y=graph_y_segment1,
        mode='lines',
        name=f'y = {k:.1f}/(x - {p:.1f}) + {q:.1f}',
        line=dict(color='blue', width=2),
        showlegend=True if k!=0 else False
    ))
    fig.add_trace(go.Scatter(
        x=graph_x_segment2,
        y=graph_y_segment2,
        mode='lines',
        line=dict(color='blue', width=2),
        showlegend=False
    ))

    # 수직 점근선
    fig.add_trace(go.Scatter(
        x=[p, p],
        y=[-1000, 1000],
        mode='lines',
        name=f'수직 점근선 x = {p:.1f}',
        line=dict(color='red', width=1, dash='dash')
    ))

    # 수평 점근선
    fig.add_trace(go.Scatter(
        x=[-1000, 1000],
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
        xaxis_range=[-10, 10],
        yaxis_range=[-10, 10]
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 학습 도구 부분: 내 생각은? (유리함수) ---
    st.subheader("💡 내 생각은?")
    st.markdown("이 함수의 **점근선, 정의역, 치역**을 예측하여 입력하고 정답을 확인해보세요.")

    guess_col1, guess_col2 = st.columns(2)

    with guess_col1:
        st.markdown("**수직 점근선**")
        user_p_guess = st.number_input("x 값 예측 (예: 2.0)", key="user_p_guess", value=0.0, step=0.1, format="%.1f")
        st.markdown("**정의역에서 x가 될 수 없는 값**")
        user_domain_guess = st.number_input("x 값 예측 (예: 2.0)", key="user_domain_guess", value=0.0, step=0.1, format="%.1f")

    with guess_col2:
        st.markdown("**수평 점근선**")
        user_q_guess = st.number_input("y 값 예측 (예: 3.0)", key="user_q_guess", value=0.0, step=0.1, format="%.1f")
        st.markdown("**치역에서 y가 될 수 없는 값**")
        user_range_guess = st.number_input("y 값 예측 (예: 3.0)", key="user_range_guess", value=0.0, step=0.1, format="%.1f")

    st.markdown("---")

    if st.button("정답 확인하기", key="check_rational_answer"):
        st.subheader("📝 정답 확인 결과
