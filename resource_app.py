import streamlit as st
import psutil
import plotly.graph_objects as go
import paramiko

# 페이지 기본 설정
st.set_page_config(page_title="System Monitor", layout="wide")
st.title("💻 통합 시스템 모니터링 대시보드")

# 깜빡임(Blink) 효과 CSS
st.markdown("""
    
""", unsafe_allow_html=True)

# 게이지 차트 생성 함수
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

# 원격 리눅스 자원 가져오기 함수
def get_linux_resources(ip, port, user, pw):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=user, password=pw, timeout=3)
        
        # CPU: vmstat 사용 (100 - idle)
        _, stdout, _ = ssh.exec_command("vmstat 1 2 | tail -1 | awk '{print 100 - $15}'")
        cpu = float(stdout.read().decode().strip())
        
        # 메모리: free 명령어 계산
        _, stdout, _ = ssh.exec_command("free | grep Mem | awk '{print $3/$2 * 100.0}'")
        mem = float(stdout.read().decode().strip())
        
        # 디스크: 루트(/) 경로 기준
        _, stdout, _ = ssh.exec_command("df / | tail -1 | awk '{print $5}' | sed 's/%//'")
        disk = float(stdout.read().decode().strip())
        
        ssh.close()
        return cpu, mem, disk
    except Exception as e:
        return None, None, None

# 1. 사이드바: 리눅스 서버 접속 정보 입력
with st.sidebar:
    st.header("🐧 원격 리눅스 연결")
    linux_ip = st.text_input("IP 주소", "192.168.0.x")
    linux_port = st.number_input("SSH 포트", value=22)
    linux_user = st.text_input("사용자 ID", "root")
    linux_pw = st.text_input("비밀번호", type="password")
    is_connect = st.toggle("서버 연결 켜기")

# 2. 탭 생성 (내 컴퓨터 vs 원격 서버)
tab_local, tab_remote = st.tabs(["💻 내 컴퓨터 (Local Windows)", "🐧 원격 서버 (Linux)"])

# ====== 탭 1: 내 컴퓨터 ======
with tab_local:
    cpu_usage = psutil.cpu_percent(interval=3) # 대기 시간을 3초로 약간 줄임
    mem_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    mem_color = "red" if mem_usage >= 80 else "orange" if mem_usage >= 50 else "#1f77b4"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(create_gauge_chart(cpu_usage, "CPU (%)", "#1f77b4"), use_container_width=True, key="l_cpu")
    with col2:
        st.plotly_chart(create_gauge_chart(mem_usage, "Memory (%)", mem_color), use_container_width=True, key="l_mem")
        if mem_usage >= 80:
            st.markdown('🚨 로컬 메모리 위험! 🚨', unsafe_allow_html=True)
    with col3:
        st.plotly_chart(create_gauge_chart(disk_usage, "Disk (%)", "#1f77b4"), use_container_width=True, key="l_disk")

# ====== 탭 2: 리눅스 서버 ======
with tab_remote:
    if is_connect:
        r_cpu, r_mem, r_disk = get_linux_resources(linux_ip, linux_port, linux_user, linux_pw)
        
        if r_cpu is not None:
            r_mem_color = "red" if r_mem >= 80 else "orange" if r_mem >= 50 else "#1f77b4"
            
            r_col1, r_col2, r_col3 = st.columns(3)
            with r_col1:
                st.plotly_chart(create_gauge_chart(r_cpu, "Linux CPU (%)", "#1f77b4"), use_container_width=True, key="r_cpu")
            with r_col2:
                st.plotly_chart(create_gauge_chart(r_mem, "Linux Memory (%)", r_mem_color), use_container_width=True, key="r_mem")
                if r_mem >= 80:
                    st.markdown('🚨 서버 메모리 위험! 🚨', unsafe_allow_html=True)
            with r_col3:
                st.plotly_chart(create_gauge_chart(r_disk, "Linux Disk / (%)", "#1f77b4"), use_container_width=True, key="r_disk")
        else:
            st.error("서버에 접속할 수 없습니다. IP, ID, 비밀번호를 확인하거나 서버의 SSH 포트가 열려있는지 확인하세요.")
    else:
        st.info("👈 좌측 사이드바에서 서버 정보를 입력하고 '연결 켜기'를 활성화해 주세요.")

# 3. 새로고침
st.rerun()