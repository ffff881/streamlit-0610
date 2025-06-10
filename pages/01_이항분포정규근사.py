import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom, norm

st.set_page_config(layout="wide")
st.title("📊 이항분포의 정규근사 시각화")
st.markdown("시행 횟수(`n`)와 성공 확률(`p`)을 조절하여 이항분포가 정규분포에 얼마나 가까워지는지 확인해보세요.")

# --- 사이드바 설정 ---
st.sidebar.header("설정")
n = st.sidebar.slider("시행 횟수 (n)", 1, 500, 30) # n 값 슬라이더 (1부터 500까지, 기본값 30)
p = st.sidebar.slider("성공 확률 (p)", 0.01, 0.99, 0.50, 0.01) # p 값 슬라이더 (0.01부터 0.99까지, 기본값 0.50, 스텝 0.01)

# --- 이항분포 계산 ---
# 가능한 성공 횟수 (0부터 n까지)
k_values = np.arange(0, n + 1)
# 이항분포의 각 성공 횟수에 대한 확률 계산
binomial_pmf = binom.pmf(k_values, n, p)

# --- 정규근사 계산 ---
# 이항분포의 평균 (mu)과 표준편차 (sigma)
mu = n * p
sigma = np.sqrt(n * p * (1 - p))

# 정규분포를 그릴 x 값 범위 설정 (평균 주변으로 4 표준편차 정도)
x_values = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 500)
# 정규분포의 확률 밀도 함수(PDF) 계산
normal_pdf = norm.pdf(x_values, loc=mu, scale=sigma)

# --- 시각화 ---
fig = go.Figure()

# 1. 이항분포 막대 그래프 추가
fig.add_trace(go.Bar(
    x=k_values,
    y=binomial_pmf,
    name='이항분포 (B(n, p))',
    marker_color='lightblue',
    opacity=0.7
))

# 2. 정규분포 곡선 추가
# sigma가 0에 가까워지면 (p가 0이나 1에 너무 가까울 때) NaN이 될 수 있으므로 조건 추가
if sigma > 0:
    fig.add_trace(go.Scatter(
        x=x_values,
        y=normal_pdf,
        mode='lines',
        name=f'정규분포 (N({mu:.2f}, {sigma**2:.2f}))', # N(평균, 분산) 표시
        line=dict(color='red', width=3)
    ))

# --- 레이아웃 설정 ---
fig.update_layout(
    title=f'이항분포 B(n={n}, p={p})와 정규근사 N(μ={mu:.2f}, σ²={sigma**2:.2f})',
    xaxis_title="성공 횟수 (k)",
    yaxis_title="확률 / 확률 밀도",
    hovermode="x unified",
    height=600,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# --- 근사 조건 및 정보 표시 ---
st.subheader("📊 계산 결과 및 근사 조건")
col1, col2 = st.columns(2)

with col1:
    st.metric("이항분포 평균 (np)", f"{mu:.2f}")
    st.metric("이항분포 분산 (np(1-p))", f"{sigma**2:.2f}")

with col2:
    st.metric("이항분포 표준편차 (√(np(1-p)))", f"{sigma:.2f}")
    # 정규근사가 좋은지 판단하는 기준
    if mu >= 5 and n * (1 - p) >= 5:
        st.success("✅ **정규근사 조건 만족!** (np ≥ 5, n(1-p) ≥ 5)")
        st.markdown("`n`이 크고 `p`가 0.5에 가까울수록 정규근사가 더 정확합니다.")
    else:
        st.warning("⚠️ **정규근사 조건이 완전히 만족되지 않습니다.**")
        st.markdown("`np` 또는 `n(1-p)` 값이 5보다 작으면 정규근사의 정확도가 떨어질 수 있습니다. `n`을 늘려보세요!")

st.markdown("---")
st.markdown("© 2025 이항분포 시각화 앱. Made for Math Class.")
