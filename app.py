import streamlit as st
import pandas as pd

st.set_page_config(page_title="삼호씨엠 마감 대시보드", layout="wide")
st.title("📊 삼호씨엠 실시간 마감 대시보드")

uploaded_files = st.file_uploader("업체 엑셀 파일들을 올려주세요", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for f in uploaded_files:
        try:
            df = pd.read_excel(f, header=None, engine='openpyxl')
            # (이전 로직 유지: 헤더 찾기 및 데이터 추출)
            header_idx = next(i for i, row in df.iterrows() if row.astype(str).str.contains('일자|날짜').any())
            df.columns = df.iloc[header_idx].astype(str).str.replace(r'\n', '', regex=True).str.strip()
            df = df.iloc[header_idx+1:].reset_index(drop=True)
            
            # 컬럼 매핑
            cols_map = {
                '날짜': [c for c in df.columns if '날짜' in c or '일자' in c][0],
                '도착지': [c for c in df.columns if '도착' in c or '현장' in c or '장소' in c][0],
                '차량': [c for c in df.columns if '차량' in c or '차호' in c][0],
                '출하량': [c for c in df.columns if '중량' in c or '수량' in c or '출하' in c or '계' in c][0]
            }
            df = df[list(cols_map.values())]
            df.columns = ['날짜', '도착지', '차량', '출하량']
            
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            all_data.append(df.dropna(subset=['날짜']))
        except: continue

    if all_data:
        final_df = pd.concat(all_data)
        
        # [웹 화면에서 바로 필터링]
        st.subheader("📋 통합 마감 내역 조회")
        site_filter = st.multiselect("현장별 필터링", final_df['도착지'].unique())
        
        if site_filter:
            final_df = final_df[final_df['도착지'].isin(site_filter)]
            
        st.dataframe(final_df, use_container_width=True) # 여기서 웹 화면에 바로 표가 나옵니다!
        
        # 합계 표시
        st.metric("총 출하량", f"{final_df['출하량'].sum():,.0f}")
