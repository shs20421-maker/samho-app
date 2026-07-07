import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="삼호씨엠 마감 시스템", layout="wide")
st.title("📊 삼호씨엠 에러 제로 마감 시스템")

uploaded_files = st.file_uploader("파일을 올려주세요", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for f in uploaded_files:
        try:
            # 1. 파일 읽기 및 헤더 찾기
            df = pd.read_csv(f)
            # '일자' 키워드가 포함된 행을 찾아 헤더로 지정
            header_idx = df[df.apply(lambda row: row.astype(str).str.contains('일자').any(), axis=1)].index[0]
            df = pd.read_csv(f, skiprows=header_idx)
            
            # 2. 필수 데이터만 골라내기 (순서/컬럼 개수 무관)
            target_cols = ['일자', '도착지', '차량', '출하계']
            df = df[[c for c in df.columns if any(t in c for t in target_cols)]]
            df.columns = ['날짜', '도착지', '차량', '출하량']
            
            # 3. 불필요한 행 제거 (소계 등)
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            df = df.dropna(subset=['날짜'])
            
            all_data.append(df)
            st.success(f"✅ {f.name} 분석 완료")
        except Exception as e:
            st.error(f"❌ {f.name} 에러: {e}. 파일을 확인해주세요.")

    if all_data:
        df_final = pd.concat(all_data)
        output = io.BytesIO()
        df_final.to_excel(output, index=False)
        st.download_button("📥 결과물 다운로드", output.getvalue(), "통합마감.xlsx")