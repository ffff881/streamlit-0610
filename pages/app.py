import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🌎 국가별 탄소배출량 시각화 (최근 3개년)")
st.markdown("Our World in Data의 CO2 배출량 데이터를 기반으로 합니다.")

# --- 데이터 로드 ---
# CSV 파일 경로 (다운로드한 파일 이름과 동일하게 설정)
DATA_PATH = 'co2-emissions-total.csv' # 이 파일 이름을 다운로드한 실제 파일 이름으로 변경하세요!

@st.cache_data # 데이터 로드를 캐싱하여 앱 성능 향상
def load_data(path):
    df = pd.read_csv(path)
    # 필요한 컬럼만 선택하고, 데이터 정제 (예: NaN 값 처리)
    df_filtered = df[['Entity', 'Code', 'Year', 'Annual CO2 emissions']].dropna()
    df_filtered.columns = ['Country', 'Code', 'Year', 'CO2_Emissions']
    return df_filtered

df = load_data(DATA_PATH)

if df is None:
    st.error(f"'{DATA_PATH}' 파일을 로드할 수 없습니다. 파일이 올바른 위치에 있는지 확인해주세요.")
else:
    # --- 데이터 필터링 (최근 3년) ---
    current_year = datetime.now().year
    # Our World in Data는 보통 전년도 또는 그 이전 연도까지 데이터를 제공합니다.
    # 따라서 "최근 3개년"을 현재 연도 기준으로 하는 것보다,
    # 데이터에 있는 가장 최신 연도를 기준으로 이전 3년을 잡는 것이 현실적입니다.
    max_year_in_data = df['Year'].max()
    min_year_for_display = max_year_in_data - 2 # 가장 최신 연도 포함 3개년

    df_recent = df[df['Year'] >= min_year_for_display]

    st.sidebar.header("필터 설정")
    selected_years = st.sidebar.multiselect(
        "조회할 연도를 선택하세요:",
        options=sorted(df_recent['Year'].unique(), reverse=True),
        default=[max_year_in_data] # 기본값으로 가장 최신 연도 선택
    )

    selected_countries = st.sidebar.multiselect(
        "비교할 국가를 선택하세요:",
        options=sorted(df_recent['Country'].unique()),
        default=['World', 'United States', 'China', 'India', 'Russia', 'South Korea'] # 예시 국가
    )

    if not selected_years or not selected_countries:
        st.warning("최소 하나의 연도와 하나의 국가를 선택해주세요.")
    else:
        df_display = df_recent[(df_recent['Year'].isin(selected_years)) & (df_recent['Country'].isin(selected_countries))]

        st.subheader(f"선택된 국가들의 CO2 배출량 추이 ({min_year_for_display}~{max_year_in_data}년)")

        # --- 1. 국가별 CO2 배출량 추이 (라인 차트) ---
        if not df_display.empty:
            fig_line = px.line(df_display,
                            x='Year',
                            y='CO2_Emissions',
                            color='Country',
                            title='국가별 연간 CO2 배출량',
                            labels={'CO2_Emissions': 'CO2 배출량 (백만 톤)', 'Year': '연도'},
                            hover_name='Country',
                            line_shape="spline") # 부드러운 선
            fig_line.update_traces(mode='lines+markers')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("선택된 필터에 해당하는 데이터가 없습니다.")

        # --- 2. 특정 연도 기준 상위 N개 국가 막대 차트 ---
        st.subheader("특정 연도 기준 상위 국가 CO2 배출량")
        if selected_years:
            selected_year_for_bar = st.sidebar.selectbox(
                "막대 차트 조회 연도 선택:",
                options=sorted(selected_years, reverse=True) # 선택된 연도 중 하나 선택
            )
            top_n = st.sidebar.slider("상위 몇 개 국가를 볼까요?", 5, 50, 10)

            df_year = df_recent[df_recent['Year'] == selected_year_for_bar].sort_values(by='CO2_Emissions', ascending=False)
            df_top_n = df_year.head(top_n)

            if not df_top_n.empty:
                fig_bar = px.bar(df_top_n,
                                x='Country',
                                y='CO2_Emissions',
                                title=f'{selected_year_for_bar}년 상위 {top_n}개 국가 CO2 배출량',
                                labels={'CO2_Emissions': 'CO2 배출량 (백만 톤)', 'Country': '국가'},
                                hover_data={'CO2_Emissions': ':.2f'})
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info(f"{selected_year_for_bar}년에 해당하는 데이터가 없거나, 상위 {top_n}개 국가를 찾을 수 없습니다.")

        # --- 3. 지도 시각화 (선택 연도 기준) ---
        st.subheader("세계 지도상의 CO2 배출량 분포")
        if selected_years:
            selected_year_for_map = st.sidebar.selectbox(
                "지도 조회 연도 선택:",
                options=sorted(selected_years, reverse=True),
                key='map_year_select' # selectbox가 여러 개일 때 key를 다르게 설정
            )
            df_map_data = df_recent[df_recent['Year'] == selected_year_for_map].dropna(subset=['Code']) # 국가 코드가 없는 행 제거

            if not df_map_data.empty:
                fig_map = px.choropleth(df_map_data,
                                        locations="Code", # 국가 코드를 사용하여 지도에 매핑
                                        color="CO2_Emissions", # CO2 배출량에 따라 색상 변경
                                        hover_name="Country", # 마우스 오버 시 국가 이름 표시
                                        color_continuous_scale=px.colors.sequential.Plasma, # 색상 스케일
                                        title=f'{selected_year_for_map}년 국가별 CO2 배출량 분포',
                                        labels={'CO2_Emissions': 'CO2 배출량 (백만 톤)'},
                                        projection="natural earth") # 지도 투영 방식
                fig_map.update_layout(height=600)
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info(f"{selected_year_for_map}년에 해당하는 지도 데이터가 없습니다.")

        # --- 원시 데이터 테이블 ---
        st.subheader("원시 데이터 미리보기")
        st.dataframe(df_display.sort_values(by=['Year', 'Country']).reset_index(drop=True))

st.markdown("---")
st.markdown("© 2025 탄소배출량 시각화 앱. Data from Our World in Data.")
