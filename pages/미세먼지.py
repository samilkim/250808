import streamlit as st
import pandas as pd
import urllib.request
import json
from pandas import json_normalize
from urllib.parse import urlencode, quote_plus, unquote
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 24:00 처리 함수 ---
# API에서 24:00로 들어오는 시간을 다음날 00:00으로 변환하는 함수
def fix_24hour_times(dt_series):
    def fix_time(s):
        if isinstance(s, str) and re.match(r"\d{4}-\d{2}-\d{2} 24:00", s):
            day = pd.to_datetime(s[:10])
            day = day + pd.Timedelta(days=1)
            return day.strftime('%Y-%m-%d') + " 00:00"
        return s
    return dt_series.apply(fix_time)

# --- 데이터 요청 함수 ---
# 캐싱을 통해 데이터를 한 번만 불러오고, API 키를 URL 인코딩하여 안전하게 사용
@st.cache_data(show_spinner=False)
def get_air_quality_df(station_list, rows=300):
    api = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    key = unquote('8imLOEIhmGIxq8Ud7TglAuHG2zQ%2BA2wGRiPnVhbHb60UJDhwJlbMqzv4SOTE5B9D3Moc713ob6bioiJywC3S3Q%3D%3D')
    
    all_dfs = []
    
    for station in station_list:
        queryParams = '?' + urlencode({
            quote_plus('serviceKey'): key,
            quote_plus('returnType'): 'json',
            quote_plus('numOfRows'): str(rows),
            quote_plus('pageNo'): '1',
            quote_plus('stationName'): station,
            quote_plus('dataTerm'): '3MONTH',
            quote_plus('ver'): '1.0'
        })
        url = api + queryParams
        try:
            with urllib.request.urlopen(url) as response:
                text = response.read().decode('utf-8')
                json_return = json.loads(text)
                if 'response' in json_return and 'body' in json_return['response'] and 'items' in json_return['response']['body']:
                    get_data = json_return.get('response')
                    df = json_normalize(get_data['body']['items'])
                    df['stationName'] = station # 측정소 이름 컬럼 추가
                    all_dfs.append(df)
        except Exception as e:
            st.error(f"'{station}' 측정소 데이터를 불러오는 중 오류가 발생했습니다: {e}")

    if not all_dfs:
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df

# --- Streamlit App UI ---
st.set_page_config("수원시 대기질 시각화", layout="wide", page_icon="🌫️")
st.title("🌫️ 수원시 대기질 실시간 시각화")
st.caption("공공데이터포털 환경부 OpenAPI 활용, 최근 3개월간 데이터 (출처: 에어코리아)")

# 수원시 측정소 목록
suwon_stations = [
    '가평', '수지', '동탄', '신장동', '천천동', '향남읍', '호매실', '정자동', '미사'
]

# 데이터 불러오기
with st.spinner('데이터 불러오는 중...'):
    df_combined = get_air_quality_df(suwon_stations, 300)

if df_combined.empty:
    st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

# 컬럼 한글 라벨링
col_map = {
    'dataTime': '측정시각',
    'pm10Value': '미세먼지(PM10) ㎍/㎥',
    'pm25Value': '초미세먼지(PM2.5) ㎍/㎥',
    'o3Value': '오존(O3) ppm',
    'no2Value': '이산화질소(NO2) ppm',
    'coValue': '일산화탄소(CO) ppm',
    'so2Value': '아황산가스(SO2) ppm',
    'khaiValue': '통합대기환경지수',
    'stationName': '측정소명'
}

# 컬럼 정리 및 타입 변환
df_combined = df_combined[[*col_map.keys()]].copy()
df_combined.rename(columns=col_map, inplace=True)

# 24:00 처리 먼저!
df_combined['측정시각'] = fix_24hour_times(df_combined['측정시각'])
df_combined['측정시각'] = pd.to_datetime(df_combined['측정시각'], format='%Y-%m-%d %H:%M')

# 숫자형 컬럼 변환
for c in col_map.values():
    if 'ppm' in c or '㎍/㎥' in c or '지수' in c:
        df_combined[c] = pd.to_numeric(df_combined[c], errors='coerce')

# --- 사이드바 및 필터링 기능 ---
st.sidebar.title("측정소 및 항목 선택")
selected_station_list = st.sidebar.multiselect(
    "비교할 측정소를 선택하세요:",
    options=suwon_stations,
    default=suwon_stations
)

# 필터링된 데이터프레임
df_filtered = df_combined[df_combined['측정소명'].isin(selected_station_list)].sort_values('측정시각')

if df_filtered.empty:
    st.warning("선택된 측정소의 데이터가 없습니다. 다른 측정소를 선택해 주세요.")
    st.stop()

# --- 선택된 측정소의 최신 측정값 ---
st.subheader("최근 대기질 현황")
latest_all_stations = df_filtered.loc[df_filtered.groupby('측정소명')['측정시각'].idxmax()]
st.dataframe(latest_all_stations.set_index('측정소명'))

st.markdown("---")

# --- 게이지 차트 (선택된 측정소의 최신 값) ---
st.subheader("선택 측정소별 현재 미세먼지 농도")
gauge_cols = st.columns(len(selected_station_list) if len(selected_station_list) <= 3 else 3)
latest_selected = df_filtered.loc[df_filtered.groupby('측정소명')['측정시각'].idxmax()]

if not latest_selected.empty:
    for i, (idx, row) in enumerate(latest_selected.iterrows()):
        with gauge_cols[i % 3]:
            st.markdown(f"##### {row['측정소명']} (PM10)")
            pm10_grade = [0, 30, 80, 150, 500]
            fig_pm10 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row['미세먼지(PM10) ㎍/㎥'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "미세먼지(PM10) ㎍/㎥"},
                gauge={
                    'axis': {'range': [None, pm10_grade[-1]], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [pm10_grade[0], pm10_grade[1]], 'color': "#007bff"}, # 좋음
                        {'range': [pm10_grade[1], pm10_grade[2]], 'color': "#28a745"}, # 보통
                        {'range': [pm10_grade[2], pm10_grade[3]], 'color': "#ffc107"}, # 나쁨
                        {'range': [pm10_grade[3], pm10_grade[4]], 'color': "#dc3545"}  # 매우 나쁨
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': row['미세먼지(PM10) ㎍/㎥']
                    }
                }
            ))
            fig_pm10.update_layout(height=250)
            st.plotly_chart(fig_pm10, use_container_width=True, key=f"pm10_gauge_{row['측정소명']}")

st.markdown("---")

# --- 막대 그래프 (최신 데이터 비교) ---
st.subheader("최신 미세먼지 농도 막대 그래프")
latest_pm_df = latest_selected[['측정소명', '미세먼지(PM10) ㎍/㎥', '초미세먼지(PM2.5) ㎍/㎥']].set_index('측정소명').stack().reset_index()
latest_pm_df.columns = ['측정소명', '항목', '농도']

fig_bar = px.bar(
    latest_pm_df,
    x='측정소명',
    y='농도',
    color='항목',
    barmode='group',
    labels={"농도": "농도(㎍/㎥)", "측정소명": "측정소"},
    template="plotly_white"
)
fig_bar.update_layout(height=450, legend=dict(title="항목", orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
st.plotly_chart(fig_bar, use_container_width=True)


# --- 비교 꺾은선 그래프 ---
st.subheader("선택된 측정소별 항목 변화 추이")
selected_y_value = st.selectbox(
    "어떤 항목을 비교하시겠습니까?",
    ['미세먼지(PM10) ㎍/㎥', '초미세먼지(PM2.5) ㎍/㎥', '통합대기환경지수', '오존(O3) ppm', '이산화질소(NO2) ppm']
)

fig_compare = px.line(
    df_filtered,
    x='측정시각',
    y=selected_y_value,
    color='측정소명',
    labels={"value": "농도", "측정시각": "시간", "stationName": "측정소명"},
    markers=True,
    template="plotly_white"
)
fig_compare.update_layout(height=450, legend=dict(title="측정소명", orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
st.plotly_chart(fig_compare, use_container_width=True)

# 데이터 테이블 보기
with st.expander("📋 전체 데이터 테이블 (최근순)"):
    st.dataframe(df_combined.style.highlight_max(axis=0), height=400)

# 다운로드 기능
csv = df_combined.to_csv(index=False, encoding='utf-8-sig')
st.download_button("📥 전체 데이터 CSV로 다운로드", csv, file_name="수원시_대기질_통합.csv", mime="text/csv")

