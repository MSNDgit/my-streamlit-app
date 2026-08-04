import streamlit as st
import pandas as pd
import numpy as np

# 1. 텍스트 출력
# 타이틀과 마크다운을 손쉽게 작성

st.title("나의 첫 번째 Streamlit 앱")
st.write("파이썬 몇 줄만 작성하면 멋진 웹이 만들어진대.")


# 2. 사용자 입력 받기
# 슬라이더와 텍스트 입력 위젯 활용
user_name = st.text_input("이름이 무엇인가요?","홍길동")
age = st.slider("나이를 선택해주세요",1, 100, 25)

st.success(f"반갑습니다, **{user_name}**님! 당신의 나이는 **{age}세**이군요.")

# 3. 데이터프레임 및 차트 그리기
# 난수를 이용한 간단한 데이터 생성
st.subheader(" 샘플 데이터 및 차트")
chart_data = pd.DataFrame(
	np.random.randn(20, 3),
	columns=['A', 'B', 'C']
)

# 표(DataFrame) 보여주기
st.dataframe(chart_data)

# 선 그래프(Line Chart) 그려주기
st.line_chart(chart_data)

