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

    # 레이아웃 설정 (dtick=1 추가)
    fig.update_layout(
        title=f'유리함수: y = {k:.1f}/(x - {p:.1f}) + {q:.1f}',
        xaxis_title="x",
        yaxis_title="y",
        hovermode="x unified",
        height=600,
        showlegend=True,
        xaxis=dict(
            range=[-10, 10], # x축 범위 고정
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            dtick=1 # 정수 단위 그리드 라인 추가
        ),
        yaxis=dict(
            range=[-10, 10],  # y축 범위 고정
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            dtick=1 # 정수 단위 그리드 라인 추가
        )
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
        st.subheader("📝 정답 확인 결과")

        epsilon = 0.001

        if abs(user_p_guess - p) < epsilon:
            st.success(f"**수직 점근선 (x = {p:.1f}):** ✅ 정답입니다!")
        else:
            st.error(f"**수직 점근선 (x = {p:.1f}):** ❌ 오답입니다. 다시 시도해보세요.")

        if abs(user_q_guess - q) < epsilon:
            st.success(f"**수평 점근선 (y = {q:.1f}):** ✅ 정답입니다!")
        else:
            st.error(f"**수평 점근선 (y = {q:.1f}):** ❌ 오답입니다. 다시 시도해보세요.")
        
        if abs(user_domain_guess - p) < epsilon:
             st.success(f"**정의역에서 x가 될 수 없는 값 (x ≠ {p:.1f}):** ✅ 정답입니다!")
        else:
            st.error(f"**정의역에서 x가 될 수 없는 값 (x ≠ {p:.1f}):** ❌ 오답입니다. 다시 시도해보세요.")

        if abs(user_range_guess - q) < epsilon:
             st.success(f"**치역에서 y가 될 수 없는 값 (y ≠ {q:.1f}):** ✅ 정답입니다!")
        else:
            st.error(f"**치역에서 y가 될 수 없는 값 (y ≠ {q:.1f}):** ❌ 오답입니다. 다시 시도해보세요.")

    st.markdown("---")


# --- 무리함수 모드 ---
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
    try:
        if a == 0:
             st.warning("a 값이 0이면 무리함수가 아닙니다 (일차함수 형태). a를 0이 아닌 값으로 설정해주세요.")
             st.stop()
        start_x = -b / a
    except ZeroDivisionError:
        st.warning("a 값이 0이면 무리함수가 아닙니다.")
        st.stop()

    start_y = c

    # 그래프 데이터 생성
    if a > 0:
        x_range = np.linspace(start_x, start_x + 10, 400)
    else: # a < 0
        x_range = np.linspace(start_x - 10, start_x, 400)

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
        mode='lines',
        name=f'y = {sqrt_sign}√({a:.1f}x + {b:.1f}) + {c:.1f}',
        line=dict(color='purple', width=2)
    ))

    # 시작점 표시
    fig.add_trace(go.Scatter(
        x=[start_x],
        y=[start_y],
        mode='markers',
        name=f'시작점 ({start_x:.2f}, {start_y:.2f})',
        marker=dict(color='darkorange', size=10, symbol='circle')
    ))

    # 레이아웃 설정 (dtick=1 추가)
    fig.update_layout(
        title=f'무리함수: y = {sqrt_sign}√({a:.1f}x + {b:.1f}) + {c:.1f}',
        xaxis_title="x",
        yaxis_title="y",
        hovermode="x unified",
        height=600,
        showlegend=True,
        xaxis=dict(
            range=[min(x_range)-1, max(x_range)+1],
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            dtick=1 # 정수 단위 그리드 라인 추가
        ),
        yaxis=dict(
            range=[min(y_range) if not np.isnan(min(y_range)) else -10, max(y_range) if not np.isnan(max(y_range)) else 10],
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            dtick=1 # 정수 단위 그리드 라인 추가
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 학습 도구 부분: 내 생각은? (무리함수) ---
    st.subheader("💡 내 생각은?")
    st.markdown("이 함수의 **시작점**과 **그래프가 뻗어나가는 방향**을 예측하여 입력하고 정답을 확인해보세요.")

    st.markdown("---")
    st.markdown("#### 1. 시작점 예측")
    guess_start_x = st.number_input("시작점의 x 좌표 예측", key="guess_start_x", value=0.0, step=0.1, format="%.1f")
    guess_start_y = st.number_input("시작점의 y 좌표 예측", key="guess_start_y", value=0.0, step=0.1, format="%.1f")

    st.markdown("---")
    st.markdown("#### 2. 그래프가 어느 방향으로 뻗어나가나요?")
    user_directions = st.multiselect(
        "그래프가 뻗어나가는 방향을 모두 선택하세요.",
        ['오른쪽 (x 증가)', '왼쪽 (x 감소)', '위 (y 증가)', '아래 (y 감소)'],
        key="user_directions_multiselect"
    )

    st.markdown("---")

    if st.button("정답 확인하기", key="check_irrational_answer"):
        st.subheader("📝 정답 확인 결과")
        epsilon = 0.001

        # 시작점 확인
        is_start_x_correct = abs(guess_start_x - start_x) < epsilon
        is_start_y_correct = abs(guess_start_y - start_y) < epsilon

        if is_start_x_correct and is_start_y_correct:
            st.success(f"**시작점:** ✅ 정답입니다! `({start_x:.2f}, {start_y:.2f})`")
        else:
            feedback_x = "정답" if is_start_x_correct else "오답"
            feedback_y = "정답" if is_start_y_correct else "오답"
            st.error(f"**시작점:** ❌ 오답입니다. (정답: `({start_x:.2f}, {start_y:.2f})`)"
                     f" (x 예측: {feedback_x}, y 예측: {feedback_y})")

        # 방향 확인
        correct_directions = []
        if a > 0:
            correct_directions.append('오른쪽 (x 증가)')
        else:
            correct_directions.append('왼쪽 (x 감소)')
        
        if sqrt_sign == "+":
            correct_directions.append('위 (y 증가)')
        else:
            correct_directions.append('아래 (y 감소)')

        user_directions_set = set(user_directions)
        correct_directions_set = set(correct_directions)

        if user_directions_set == correct_directions_set:
            st.success(f"**그래프 방향:** ✅ 정답입니다! ({', '.join(correct_directions)})")
        else:
            st.error(f"**그래프 방향:** ❌ 오답입니다. (정답: {', '.join(correct_directions)})")
            
        st.info("정의역과 치역은 그래프 아래 '함수 정보' 섹션을 참고하세요.")

    st.markdown("---")

st.markdown("© 2025 함수 그래프 탐색기 앱. Made for Math Class.")
