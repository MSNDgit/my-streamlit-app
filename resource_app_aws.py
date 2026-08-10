import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import paramiko
import random # 테스트용 임시 데이터 생성용

st.set_page_config(page_title="AWS Server Monitor", layout="wide")

# 게이지 차트 함수 (이전과 동일)
def create_gauge_chart(value, title, bar_color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': bar_color},
            'steps': [
                {'range': [0, 50], 'color': "#e6f2ff"},
                {'range': [50, 80], 'color': "#ffebcc"},
                {'range': [80, 100], 'color': "#ffcccc"}
            ],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# 데이터프레임 색상 칠하기 함수 (80% 이상이면 빨간색 배경)
def highlight_danger(val):
    if isinstance(val, (int, float)) and val >= 80:
        return 'background-color: #ffcccc; color: red; font-weight: bold'
    elif isinstance(val, (int, float)) and val >= 50:
        return 'background-color: #ffebcc; color: orange'
    return ''

# 사이드바 메뉴 구성
st.sidebar.title("☁️ AWS 모니터링 메뉴")
menu = st.sidebar.radio("이동할 페이지를 선택하세요", ["📊 24시간 전체 현황판", "💻 개별 서버 상세 모니터링"])

# 관리하는 AWS 서버 목록 (실제 IP로 변경 필요)
server_list = {
    "Web Server 1": "192.168.0.10",
    "Web Server 2": "192.168.0.11",
    "DB Server": "192.168.0.20",
    "API Server": "192.168.0.30"
}

# ==========================================
# 1. 전체 서버 24시간 현황판 화면
# ==========================================
if menu == "📊 24시간 전체 현황판":
    st.title("📊 24시간 AWS 서버 리소스 초과 현황")
    st.markdown("지난 24시간 동안 **CPU 또는 메모리 사용량이 80%를 초과한 이력**이 있는 서버를 강조 표시합니다.")
    
    # 실무에서는 AWS CloudWatch API(boto3)를 통해 이 데이터를 가져와야 합니다.
    # 현재는 UI 테스트를 위해 가상의 24시간 최대 사용량 데이터를 만듭니다.
    data = []
    for name, ip in server_list.items():
        data.append({
            "서버명": name,
            "IP 주소": ip,
            "24h 최대 CPU (%)": random.randint(30, 95), # 가짜 데이터
            "24h 최대 메모리 (%)": random.randint(40, 99), # 가짜 데이터
            "상태": "점검 필요 🚨" if random.choice([True, False]) else "정상 🟢"
        })
    
    df = pd.DataFrame(data)
    
    # 판다스 스타일링을 적용하여 80% 이상인 셀에 색상을 칠해서 출력
    styled_df = df.style.map(highlight_danger, subset=["24h 최대 CPU (%)", "24h 최대 메모리 (%)"])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.info("💡 개별 서버의 실시간 상태를 보려면 좌측 메뉴에서 '개별 서버 상세 모니터링'을 클릭하세요.")

# ==========================================
# 2. 개별 서버 실시간 모니터링 화면
# ==========================================
elif menu == "💻 개별 서버 상세 모니터링":
    st.title("💻 실시간 개별 서버 모니터링")
    
    # 콤보박스(Selectbox)로 확인할 서버 선택
    selected_server_name = st.selectbox("📌 모니터링할 서버를 선택하세요:", list(server_list.keys()))
    selected_ip = server_list[selected_server_name]
    
    st.subheader(f"[{selected_server_name}] ({selected_ip}) 실시간 리소스")
    
    # 서버 접속 정보 입력칸 (펼치기/접기 형태로 깔끔하게)
    with st.expander("🔑 SSH 접속 정보 설정", expanded=True):
        col_port, col_user, col_pw = st.columns(3)
        port = col_port.number_input("SSH 포트", value=22, key="port")
        user = col_user.text_input("사용자 ID", "ubuntu", key="user") # AWS는 보통 ubuntu나 ec2-user 사용
        pw = col_pw.text_input("비밀번호 (또는 Key 경로)", type="password", key="pw")
        is_connect = st.toggle("🚀 실시간 연결 시작")

    if is_connect:
        st.caption("🔄 3초 주기로 실시간 통신 중...")
        # 실제 서버 연결 로직 (이전 코드의 get_linux_resources 함수 호출)
        # ※ 이 부분은 이전 답변의 paramiko 연결 코드를 그대로 사용하시면 됩니다.
        
        # --- UI 테스트용 가짜 데이터 출력 (실제 연결 성공 시 아래 코드를 진짜 데이터로 교체하세요) ---
        r_cpu, r_mem, r_disk = random.randint(10,90), random.randint(10,95), random.randint(30,60)
        
        r_mem_color = "red" if r_mem >= 80 else "orange" if r_mem >= 50 else "#1f77b4"
        
        r_col1, r_col2, r_col3 = st.columns(3)
        with r_col1:
            st.plotly_chart(create_gauge_chart(r_cpu, "CPU (%)", "#1f77b4"), use_container_width=True)
        with r_col2:
            st.plotly_chart(create_gauge_chart(r_mem, "Memory (%)", r_mem_color), use_container_width=True)
        with r_col3:
            st.plotly_chart(create_gauge_chart(r_disk, "Disk / (%)", "#1f77b4"), use_container_width=True)
            
        import time
        time.sleep(3)
        st.rerun()