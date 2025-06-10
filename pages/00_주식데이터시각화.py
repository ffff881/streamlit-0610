
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("글로벌 시총 Top 10 기업 주가 변화 시각화 (최근 3년)")

# --- 가상의 글로벌 시총 Top 10 기업 티커 (실제 데이터는 직접 확인 필요) ---
# 이 목록은 예시이며, 실제 최신 Top 10 기업과 다를 수 있습니다.
top_10_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL", # 또는 GOOG
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Meta Platforms": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-A", # 또는 BRK-B
    "Eli Lilly and Company": "LLY",
    "TSMC": "TSM",
}

# 날짜 설정 (최근 3년)
end_date = datetime.now()
start_date = end_date - timedelta(days=3 * 365) # 대략 3년

st.sidebar.header("설정")
selected_companies = st.sidebar.multiselect(
    "조회할 기업을 선택하세요:",
    options=list(top_10_tickers.keys()),
    default=list(top_10_tickers.keys()) # 기본적으로 모든 기업 선택
)

if not selected_companies:
    st.warning("최소 하나 이상의 기업을 선택해주세요.")
else:
    st.subheader(f"선택된 기업들의 주가 변화 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")

    all_data = pd.DataFrame()
    for company_name in selected_companies:
        ticker = top_10_tickers[company_name]
        try:
            # yfinance로 주가 데이터 가져오기
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty:
                # 종가(Close)만 사용
                data = data[['Close']]
                data.columns = [company_name]
                if all_data.empty:
                    all_data = data
                else:
                    all_data = pd.merge(all_data, data, left_index=True, right_index=True, how='outer')
            else:
                st.warning(f"'{company_name}' ({ticker})의 데이터를 가져올 수 없거나 데이터가 비어있습니다.")
        except Exception as e:
            st.error(f"'{company_name}' ({ticker})의 데이터를 가져오는 중 오류가 발생했습니다: {e}")

    if not all_data.empty:
        # 각 기업의 초기 주가를 기준으로 정규화하여 변화율 시각화
        normalized_data = all_data / all_data.iloc[0] * 100

        fig = go.Figure()

        for col in normalized_data.columns:
            fig.add_trace(go.Scatter(x=normalized_data.index, y=normalized_data[col], mode='lines', name=col))

        fig.update_layout(
            title="선택 기업들의 주가 변화율 (초기 시점 대비)",
            xaxis_title="날짜",
            yaxis_title="주가 변화율 (%) (초기 시점 = 100)",
            hovermode="x unified",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("원시 주가 데이터 (종가)")
        st.dataframe(all_data)

    else:
        st.info("선택된 기업들의 주가 데이터를 로드할 수 없습니다.")
