import streamlit as st
import psutil
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="System Monitor", layout="wide")
st.title("💻 내 컴퓨터 시스템 모니터링")

def create_gauge_chart(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 60], 'color': "#e6f2ff"},
                {'range': [60, 85], 'color': "#ffebcc"},
                {'range': [85, 100], 'color': "#ffcccc"}
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# 1. 시스템 정보 가져오기
# [핵심 변경 사항] 
# interval=1로 설정하면 psutil이 정확히 1초 동안 대기하며 실제 CPU 점유율을 계산합니다.
# 윈도우 작업 관리자와 동일한 측정 방식이며, 이 자체가 1초를 대기하므로 time.sleep()이 필요 없습니다.
cpu_usage = psutil.cpu_percent(interval=1)
mem_usage = psutil.virtual_memory().percent
disk_usage = psutil.disk_usage('/').percent

# 2. 화면에 그리기
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(create_gauge_chart(cpu_usage, "CPU 사용량 (%)"), use_container_width=True, key="chart_cpu")
with col2:
    st.plotly_chart(create_gauge_chart(mem_usage, "메모리 사용량 (%)"), use_container_width=True, key="chart_mem")
with col3:
    st.plotly_chart(create_gauge_chart(disk_usage, "HDD/SSD 사용량 (%)"), use_container_width=True, key="chart_disk")
    
st.caption("🔄 운영체제(작업 관리자)와 동일한 1초 주기로 정확히 연동 중입니다...")

# 3. Streamlit 앱 전체를 새로고침 (time.sleep() 제거)
st.rerun()