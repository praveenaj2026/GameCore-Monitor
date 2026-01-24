"""
GameCore Monitor v0.1.1
PC Performance Monitoring Dashboard
Optimized: Full-width charts, instant tab switching, proper GPU detection
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.sensors.cpu_sensor import CPUSensor
from src.sensors.gpu_sensor import GPUSensor
from src.sensors.ram_sensor import RAMSensor
from src.sensors.disk_sensor import DiskSensor
from src.sensors.network_sensor import NetworkSensor
from src.sensors.system_sensor import SystemSensor
from src.alerts.alert_system import AlertManager
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger
from src.utils.data_export import DataExporter

# Setup
logger = setup_logger()
config_manager = ConfigManager()
exporter = DataExporter()

# Page Config
st.set_page_config(
    page_title="GameCore Monitor",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3140;
    }
    .stAlert {
        background-color: #1e2130;
        border-left: 4px solid #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

# Sensor Manager with caching
@st.cache_resource
def get_sensor_manager():
    """Initialize all sensors once and cache them"""
    class SensorManager:
        def __init__(self):
            self.sensors = {
                "cpu": CPUSensor(),
                "gpu": GPUSensor(),
                "ram": RAMSensor(),
                "disk": DiskSensor(),
                "network": NetworkSensor(),
                "system": SystemSensor()
            }
            
        def get_sensor(self, name):
            return self.sensors[name]
            
        def update_all(self):
            """Update all sensors"""
            for sensor in self.sensors.values():
                sensor.update()
    
    return SensorManager()

# Initialize sensor manager (cached)
sensor_manager = get_sensor_manager()

# Alert Manager (cached)
@st.cache_resource
def get_alert_manager():
    return AlertManager()

alert_manager = get_alert_manager()

# Session state initialization
if 'history' not in st.session_state:
    st.session_state.history = {
        'cpu': [],
        'gpu': [],
        'ram': [],
        'disk': [],
        'network_up': [],
        'network_down': []
    }

if 'all_processes' not in st.session_state:
    st.session_state.all_processes = []

# Header
st.title("🎮 GameCore Monitor")
st.markdown("**Phase 1: PC Health & Performance Monitor** | v0.1.1")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        sensor_manager.update_all()
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("Auto-refresh (5s)", value=False)
    
    if auto_refresh:
        time.sleep(5)
        sensor_manager.update_all()
        st.rerun()
    
    st.divider()
    
    # Export options
    st.subheader("📤 Export Data")
    if st.button("Export JSON Snapshot", use_container_width=True):
        # Collect all sensor data
        data = {}
        for name, sensor in sensor_manager.sensors.items():
            data[name] = sensor.get_data()
        
        filename = exporter.export_snapshot(data)
        st.success(f"Exported to {filename}")
    
    st.divider()
    
    # System info
    st.subheader("💻 System Info")
    sys_data = sensor_manager.get_sensor("system").get_data()
    st.text(f"OS: {sys_data['os']}")
    st.text(f"CPU: {sys_data['processor']}")
    st.text(f"Cores: {sys_data['physical_cores']}P / {sys_data['logical_cores']}L")

# Update all sensors
sensor_manager.update_all()

# Get latest data
cpu_data = sensor_manager.get_sensor("cpu").get_data()
gpu_data = sensor_manager.get_sensor("gpu").get_data()
ram_data = sensor_manager.get_sensor("ram").get_data()
disk_data = sensor_manager.get_sensor("disk").get_data()
net_data = sensor_manager.get_sensor("network").get_data()

# Update history (keep last 120 samples = 10 minutes at 5s interval)
st.session_state.history['cpu'].append(cpu_data['usage'])
st.session_state.history['gpu'].append(gpu_data['usage'])
st.session_state.history['ram'].append(ram_data['percent'])
st.session_state.history['network_up'].append(net_data['upload_speed'])
st.session_state.history['network_down'].append(net_data['download_speed'])

for key in st.session_state.history:
    if len(st.session_state.history[key]) > 120:
        st.session_state.history[key] = st.session_state.history[key][-120:]

# Check for alerts
cpu_sensor = sensor_manager.get_sensor("cpu")
gpu_sensor = sensor_manager.get_sensor("gpu")
ram_sensor = sensor_manager.get_sensor("ram")

alert_manager.check_all_rules({
    'cpu': cpu_sensor,
    'gpu': gpu_sensor,
    'ram': ram_sensor
})

# Show active alerts
active_alerts = alert_manager.get_active_alerts()
if active_alerts:
    st.warning(f"⚠️ {len(active_alerts)} Active Alert(s)")
    for alert in active_alerts[:3]:  # Show top 3
        st.error(f"**{alert.level.value}**: {alert.message}")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Performance Charts", "💻 Processes & Disk", "🚨 Alerts"])

with tab1:
    st.header("System Overview")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🖥️ CPU Usage",
            value=f"{cpu_data['usage']:.1f}%",
            delta=f"{cpu_data['frequency']:.0f} MHz"
        )
        st.progress(cpu_data['usage'] / 100)
    
    with col2:
        st.metric(
            label="🎮 GPU Usage",
            value=f"{gpu_data['usage']:.1f}%",
            delta=f"{gpu_data['temperature']:.0f}°C"
        )
        st.progress(gpu_data['usage'] / 100)
    
    with col3:
        st.metric(
            label="🧠 RAM Usage",
            value=f"{ram_data['percent']:.1f}%",
            delta=f"{ram_data['used_gb']:.1f} / {ram_data['total_gb']:.1f} GB"
        )
        st.progress(ram_data['percent'] / 100)
    
    with col4:
        st.metric(
            label="🌐 Network",
            value=f"↓ {net_data['download_speed']:.1f} Mbps",
            delta=f"↑ {net_data['upload_speed']:.1f} Mbps"
        )
    
    st.divider()
    
    # Detailed info in expandable sections
    with st.expander("🖥️ CPU Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Per-Core Usage", f"{cpu_data['usage']:.1f}%")
            st.metric("Temperature", f"{cpu_data['temperature']:.1f}°C")
        with col2:
            st.metric("Frequency", f"{cpu_data['frequency']:.0f} MHz")
            st.metric("Power", "N/A (Future)")
    
    with st.expander("🎮 GPU Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("GPU Name", gpu_data['name'])
            st.metric("Usage", f"{gpu_data['usage']:.1f}%")
        with col2:
            st.metric("Temperature", f"{gpu_data['temperature']:.1f}°C")
            st.metric("Memory Used", f"{gpu_data['memory_used']:.0f} / {gpu_data['memory_total']:.0f} MB")
        
        if "Integrated" in gpu_data['name'] or "AMD" in gpu_data['name']:
            st.info("💡 **GPU Detection Note**: You have NVIDIA RTX 5050 with Optimus hybrid graphics. If GPU shows 0%, it means Windows is using Intel iGPU for power saving. To force NVIDIA GPU:\n\n1. Open NVIDIA Control Panel\n2. Manage 3D Settings → Program Settings\n3. Add Python.exe from your .venv folder\n4. Set to 'High-performance NVIDIA processor'\n\nAlternatively: Windows Settings → Display → Graphics → Add Python.exe → High Performance")
    
    with st.expander("🧠 RAM Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Used", f"{ram_data['used_gb']:.2f} GB")
            st.metric("Available", f"{ram_data['available_gb']:.2f} GB")
        with col2:
            st.metric("Total", f"{ram_data['total_gb']:.2f} GB")
            st.metric("Usage %", f"{ram_data['percent']:.1f}%")
        
        if ram_data['total_gb'] < 24 and ram_data['total_gb'] > 19:
            st.info("💡 **RAM Display Note**: You have 24GB installed, but Windows shows ~19.6GB available. This is normal - Windows reserves 4-5GB for:\n- Hardware reserved memory (iGPU, system)\n- Kernel and drivers\n- Memory-mapped I/O")
    
    with st.expander("💾 Disk Details"):
        st.info("ℹ️ Warming up disk I/O monitoring... (takes 2-3 seconds)")
        for disk in disk_data['disks']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"Drive {disk['device']}", f"{disk['percent']}%")
            with col2:
                st.metric("Used / Total", f"{disk['used_gb']:.0f} / {disk['total_gb']:.0f} GB")
            with col3:
                st.metric("Read / Write", f"{disk_data.get('read_speed', 0):.1f} / {disk_data.get('write_speed', 0):.1f} MB/s")
    
    with st.expander("🌐 Network Details"):
        st.info("💡 **Network Speed Note**: Speed shows as 0 Mbps initially. Needs 2-3 seconds to calculate transfer rate delta. Keep dashboard open for accurate readings.")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Download Speed", f"{net_data['download_speed']:.2f} Mbps")
            st.metric("Total Downloaded", f"{net_data['bytes_sent_gb']:.2f} GB (session)")
        with col2:
            st.metric("Upload Speed", f"{net_data['upload_speed']:.2f} Mbps")
            st.metric("Total Uploaded", f"{net_data['bytes_recv_gb']:.2f} GB (session)")
    
    # Top processes summary
    st.divider()
    st.subheader("🔝 Top 5 Resource Consumers")
    
    # Get all processes
    import psutil
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU usage
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    st.session_state.all_processes = processes[:15]
    
    if processes:
        top5 = processes[:5]
        df_top5 = pd.DataFrame(top5)
        st.dataframe(
            df_top5,
            column_config={
                "pid": "PID",
                "name": "Process",
                "cpu_percent": st.column_config.NumberColumn("CPU %", format="%.1f"),
                "memory_percent": st.column_config.NumberColumn("Memory %", format="%.1f"),
            },
            hide_index=True,
            use_container_width=True
        )

with tab2:
    st.header("📈 Performance Charts")
    st.info("💡 Charts show recent history. Use full width for better readability. Tab switching is instant (no reload).")
    
    # CPU Usage History
    st.subheader("CPU Usage Over Time")
    cpu_sensor_hist = sensor_manager.get_sensor("cpu")
    if hasattr(cpu_sensor_hist, 'history') and len(cpu_sensor_hist.history) > 0:
        cpu_df = pd.DataFrame(cpu_sensor_hist.history[-60:])  # Last 60 samples
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=cpu_df.index,
            y=cpu_df['usage'],
            mode='lines',
            name='CPU %',
            line=dict(color='#00d4ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        fig1.update_layout(
            height=300,
            margin=dict(l=50, r=20, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Samples (5s interval)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Usage %', range=[0, 100])
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Collecting CPU data... Refresh in a few seconds.")
    
    # RAM Usage History
    st.subheader("RAM Usage Over Time")
    ram_sensor_hist = sensor_manager.get_sensor("ram")
    if hasattr(ram_sensor_hist, 'history') and len(ram_sensor_hist.history) > 0:
        ram_df = pd.DataFrame(ram_sensor_hist.history[-60:])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=ram_df.index,
            y=ram_df['percent'],
            mode='lines',
            name='RAM %',
            line=dict(color='#00ff88', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.1)'
        ))
        fig2.update_layout(
            height=300,
            margin=dict(l=50, r=20, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Samples (5s interval)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Usage %', range=[0, 100])
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Collecting RAM data... Refresh in a few seconds.")
    
    # GPU Temperature History
    st.subheader("GPU Temperature Over Time")
    gpu_sensor_hist = sensor_manager.get_sensor("gpu")
    if hasattr(gpu_sensor_hist, 'history') and len(gpu_sensor_hist.history) > 0:
        gpu_df = pd.DataFrame(gpu_sensor_hist.history[-60:])
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=gpu_df.index,
            y=gpu_df['temperature'],
            mode='lines',
            name='GPU Temp',
            line=dict(color='#ff6b35', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 53, 0.1)'
        ))
        # Add warning threshold line at 85°C
        fig3.add_hline(
            y=85, 
            line_dash="dash", 
            line_color="yellow", 
            annotation_text="⚠️ Warning Threshold (85°C)",
            annotation_position="right"
        )
        fig3.update_layout(
            height=300,
            margin=dict(l=50, r=20, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Samples (5s interval)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Temperature °C')
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Collecting GPU data... Refresh in a few seconds.")
    
    # Network Speed History
    st.subheader("Network Speed Over Time")
    net_sensor_hist = sensor_manager.get_sensor("network")
    if hasattr(net_sensor_hist, 'history') and len(net_sensor_hist.history) > 0:
        net_df = pd.DataFrame(net_sensor_hist.history[-60:])
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=net_df.index,
            y=net_df['download_speed'],
            mode='lines',
            name='Download',
            line=dict(color='#00d4ff', width=2)
        ))
        fig4.add_trace(go.Scatter(
            x=net_df.index,
            y=net_df['upload_speed'],
            mode='lines',
            name='Upload',
            line=dict(color='#ff6b35', width=2)
        ))
        fig4.update_layout(
            height=300,
            margin=dict(l=50, r=20, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Samples (5s interval)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Speed (Mbps)'),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0.5)')
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Collecting network data... Refresh in a few seconds.")

with tab3:
    st.header("💻 Processes & Disk I/O")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Top 15 Processes (by CPU)")
        if st.session_state.all_processes:
            df = pd.DataFrame(st.session_state.all_processes)
            st.dataframe(
                df,
                column_config={
                    "pid": st.column_config.NumberColumn("PID", format="%d"),
                    "name": "Process Name",
                    "cpu_percent": st.column_config.NumberColumn("CPU %", format="%.1f"),
                    "memory_percent": st.column_config.NumberColumn("Memory %", format="%.1f"),
                },
                hide_index=True,
                height=400,
                use_container_width=True
            )
        else:
            st.info("No process data available yet. Refresh to load.")
    
    with col2:
        st.subheader("Disk Usage")
        for disk in disk_data['disks']:
            st.metric(
                label=f"Drive {disk['device']}",
                value=f"{disk['used_gb']:.0f} / {disk['total_gb']:.0f} GB",
                delta=f"{disk['percent']}% used"
            )
            st.progress(disk['percent'] / 100)
        
        st.divider()
        st.subheader("Disk I/O Speed")
        st.metric("Read Speed", f"{disk_data.get('read_speed', 0):.1f} MB/s")
        st.metric("Write Speed", f"{disk_data.get('write_speed', 0):.1f} MB/s")

with tab4:
    st.header("🚨 Alert System")
    
    # Alert configuration
    st.subheader("Configure Alert Rules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Rule Name", value="High CPU Usage", disabled=True)
        st.number_input("Threshold (%)", value=90, min_value=0, max_value=100)
        st.number_input("Duration (seconds)", value=10, min_value=1)
    
    with col2:
        st.selectbox("Metric", ["CPU Usage", "GPU Temperature", "RAM Usage"])
        st.selectbox("Alert Level", ["WARNING", "CRITICAL"])
        if st.button("Save Rule"):
            st.success("Rule saved! (Feature coming in Phase 2)")
    
    st.divider()
    
    # Active alerts
    st.subheader("Active Alerts")
    active_alerts = alert_manager.get_active_alerts()
    
    if active_alerts:
        for alert in active_alerts:
            if alert.level.value == "CRITICAL":
                st.error(f"🔴 **{alert.level.value}**: {alert.message} (triggered at {alert.timestamp.strftime('%H:%M:%S')})")
            else:
                st.warning(f"🟡 **{alert.level.value}**: {alert.message} (triggered at {alert.timestamp.strftime('%H:%M:%S')})")
    else:
        st.success("✅ No active alerts. System running normally.")
    
    st.divider()
    
    # Alert history
    st.subheader("Recent Alert History")
    all_alerts = alert_manager.get_all_alerts()
    
    if all_alerts:
        alert_df = pd.DataFrame([
            {
                "Time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Level": a.level.value,
                "Message": a.message
            }
            for a in all_alerts[-20:]  # Last 20 alerts
        ])
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
    else:
        st.info("No alerts triggered yet.")

# Footer
st.divider()
st.caption("GameCore Monitor v0.1.1 | Phase 1 Complete | Next: Phase 2 (Thermal & Health Deep Dive)")
st.caption("💡 Tip: Enable auto-refresh in sidebar for real-time monitoring")
