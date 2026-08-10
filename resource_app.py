import streamlit as st
import psutil
import plotly.graph_objects as go


## Git test branch user 

# 페이지 기본 설정
st.set_page_config(page_title="System Monitor", layout="wide")
st.title("💻 내 컴퓨터 시스템 모니터링")

# [추가됨] CSS 깜빡임(Blink) 효과 정의
# 웹페이지에 깜빡이는 애니메이션 스타일을 미리 주입합니다.
st.markdown("""
    <style>
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    .blink-text {
        animation: blink 1s infinite;
        color: red;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-top: -10px;
    }
    </style>
""", unsafe_allow_html=True)

def create_gauge_chart(value, title, bar_color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': bar_color}, # 막대 색상을 외부에서 받아와 동적으로 변경
            'steps': [
                {'range': [0, 50], 'color': "#e6f2ff"},   # 0~50: 연한 파랑 (정상)
                {'range': [50, 80], 'color': "#ffebcc"},  # 50~80: 연한 주황 (주의)
                {'range': [80, 100], 'color': "#ffcccc"}  # 80~100: 연한 빨강 (위험)
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# 1. 5초 주기로 시스템 정보 가져오기
# interval=5로 설정하면 파이썬이 5초 동안 대기하며 측정합니다.
# 이 코드가 5초 타이머 역할을 하므로 앱 전체의 갱신 주기가 자연스럽게 5초가 됩니다.
cpu_usage = psutil.cpu_percent(interval=5)
mem_usage = psutil.virtual_memory().percent
disk_usage = psutil.disk_usage('/').percent

# 2. 메모리 사용량에 따른 색상 결정 로직
if mem_usage >= 80:
    mem_color = "red"      # 80% 이상: 빨간색
elif mem_usage >= 50:
    mem_color = "orange"   # 50% 이상: 주황색
else:
    mem_color = "#1f77b4"  # 50% 미만: 기본 파란색

# 3. 화면에 그리기
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(create_gauge_chart(cpu_usage, "CPU 사용량 (%)", "#1f77b4"), use_container_width=True, key="chart_cpu")

with col2:
    # 결정된 mem_color를 함수에 전달하여 차트 막대 색상을 바꿉니다.
    st.plotly_chart(create_gauge_chart(mem_usage, "메모리 사용량 (%)", mem_color), use_container_width=True, key="chart_mem")
    
    # 메모리가 80% 이상일 때만 깜빡이는 HTML 텍스트를 출력합니다.
    if mem_usage >= 80:
        st.markdown('<div class="blink-text">🚨 메모리 위험 수준! 🚨</div>', unsafe_allow_html=True)

with col3:
    st.plotly_chart(create_gauge_chart(disk_usage, "HDD/SSD 사용량 (%)", "#1f77b4"), use_container_width=True, key="chart_disk")
    
st.caption("🔄 5초 주기로 업데이트 및 모니터링 중입니다...")

# 4. Streamlit 앱 다시 실행
st.rerun()