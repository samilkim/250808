import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Streamlit 앱의 제목 설정
st.title('파일 업로드 및 다양한 시각화 앱')
st.write('CSV 또는 엑셀 파일을 업로드하면 데이터를 읽어 다양한 Plotly 그래프를 한 번에 시각화해 줍니다.')

# 파일 업로더 위젯
uploaded_file = st.file_uploader("CSV 또는 엑셀 파일을 선택해 주세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 파일 확장자에 따라 다른 방식으로 파일 읽기
        file_extension = uploaded_file.name.split('.')[-1]

        if file_extension == 'csv':
            # CSV 파일 처리: 인코딩 자동 감지 시도
            try:
                # pandas가 자동으로 인코딩을 감지하도록 시도
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                # UTF-8 실패 시, EUC-KR 및 CP949 인코딩으로 재시도
                bytes_data = uploaded_file.getvalue()
                try:
                    df = pd.read_csv(io.StringIO(bytes_data.decode('euc-kr')))
                except UnicodeDecodeError:
                    df = pd.read_csv(io.StringIO(bytes_data.decode('cp949')))
            
            # CSV 파일의 헤더 문제 해결 (만약 있다면)
            # 파일 내용에 따라 헤더 행을 조정해야 할 수 있습니다.
            # 이 예시에서는 이전 대화의 문제 해결 코드를 포함하지 않았습니다.
            
        elif file_extension == 'xlsx':
            # 엑셀 파일 처리
            df = pd.read_excel(uploaded_file)
            
        else:
            st.error("지원하지 않는 파일 형식입니다. CSV 또는 엑셀 파일만 업로드해 주세요.")
            st.stop()

        # 데이터 미리보기
        st.write("---")
        st.subheader("✅ 업로드된 데이터 미리보기")
        st.dataframe(df.head())
        
        # 데이터 열 유형에 따라 자동 시각화
        st.subheader("📊 자동 생성된 그래프")
        
        # 숫자형, 비숫자형 열 구분
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        if not numeric_cols:
            st.warning("데이터에 숫자형 열이 없어 그래프를 생성할 수 없습니다.")
        else:
            # 1. 히스토그램 (Histogram)
            st.write("### 📈 히스토그램")
            st.write("각 숫자형 열의 분포를 한눈에 확인할 수 있습니다.")
            for col in numeric_cols:
                fig_hist = px.histogram(df, x=col, title=f'{col} 히스토그램')
                st.plotly_chart(fig_hist)

            # 2. 산점도 행렬 (Scatter Matrix)
            if len(numeric_cols) >= 2:
                st.write("### 🔵 산점도 행렬")
                st.write("두 개 이상의 숫자형 열 간의 상관관계를 보여줍니다.")
                fig_scatter_matrix = px.scatter_matrix(df, dimensions=numeric_cols, title="산점도 행렬")
                st.plotly_chart(fig_scatter_matrix)
            
            # 3. 막대 그래프 (Bar Chart) - 비숫자형 vs 숫자형
            if non_numeric_cols and numeric_cols:
                st.write("### 📊 막대 그래프")
                st.write("비숫자형 열과 숫자형 열을 결합하여 데이터를 비교합니다.")
                # 첫 번째 비숫자형 열과 첫 번째 숫자형 열을 사용하여 막대 그래프 생성
                fig_bar = px.bar(df, x=non_numeric_cols[0], y=numeric_cols[0], title=f'{non_numeric_cols[0]}별 {numeric_cols[0]}')
                st.plotly_chart(fig_bar)

    except Exception as e:
        st.error(f"파일을 읽는 도중 오류가 발생했습니다: {e}")
