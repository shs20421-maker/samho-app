import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="삼호씨엠 마감 시스템", layout="wide")
st.title("📊 삼호씨엠 마감 자동 분석 시스템")

uploaded_files = st.file_uploader("업체에서 받은 엑셀 파일을 모두 올려주세요", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for f in uploaded_files:
        try:
            # 1. 엑셀 파일 읽기 (인코딩 문제 해결)
            df = pd.read_excel(f, header=None)
            
            # 2. '일자' 또는 '날짜' 키워드가 포함된 행 찾기
            header_idx = 0
            for i in range(min(10, len(df))):
                if df.iloc[i].astype(str).str.contains('일자|날짜').any():
                    header_idx = i
                    break
            
            # 찾은 행을 기준으로 데이터 새로 구성
            df.columns = df.iloc[header_idx].astype(str).str.replace(r'\n', '', regex=True).str.strip()
            df = df.iloc[header_idx+1:].reset_index(drop=True)
            
            # 3. 필수 컬럼만 골라내기 (키워드 매칭)
            # 날짜, 도착지, 차량, 출하량(중량) 키워드
            cols_map = {
                '날짜': [c for c in df.columns if '날짜' in c or '일자' in c][0],
                '도착지': [c for c in df.columns if '도착' in c or '현장' in c or '장소' in c][0],
                '차량': [c for c in df.columns if '차량' in c or '차호' in c][0],
                '출하량': [c for c in df.columns if '중량' in c or '수량' in c or '출하' in c or '계' in c][0]
            }
            
            df = df[list(cols_map.values())]
            df.columns = ['날짜', '도착지', '차량', '출하량']
            
            # 4. 데이터 정제
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            df = df.dropna(subset=['날짜'])
            df['출하량'] = pd.to_numeric(df['출하량'], errors='coerce').fillna(0)
            
            all_data.append(df)
            st.success(f"✅ {f.name} 파일 분석 성공!")
            
        except Exception as e:
            st.error(f"❌ {f.name} 파일 분석 중 에러: {e}. (파일 형식을 확인해주세요.)")

    if all_data:
        df_final = pd.concat(all_data)
        output = io.BytesIO()
        df_final.to_excel(output, index=False)
        st.download_button("📥 통합 마감 장부 다운로드", output.getvalue(), "통합마감장부.xlsx")
