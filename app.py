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
from src.utils.logger import setup_logging
from src.utils.data_export import DataExporter
from src.utils.background_monitor import BackgroundMonitor

# Setup
logger = setup_logging()
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

# Background Monitor (cached) - Continuously updates data in background
@st.cache_resource
def get_background_monitor():
    monitor = BackgroundMonitor(sensor_manager, update_interval=1.0)  # Update every 1 second
    monitor.start()
    return monitor

background_monitor = get_background_monitor()

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
    if st.button("🔄 Refresh Data", width="stretch"):
        st.rerun()
    
    st.info("💡 **Real-time mode**: Data updates every 1 second in background. Just refresh browser to see latest.")
    
    st.divider()
    
    # Background monitor stats
    with st.expander("⚡ Performance Stats"):
        stats = background_monitor.get_stats()
        st.metric("Updates", f"{stats['update_count']}")
        st.metric("Avg Update Time", f"{stats['avg_update_time_ms']:.1f} ms")
        st.metric("Status", "🟢 Healthy" if background_monitor.is_healthy() else "🔴 Error")
    
    st.divider()
    
    # Export options
    st.subheader("📤 Export Data")
    if st.button("Export JSON Snapshot", width="stretch"):
        # Collect all sensor data
        data = {}
        for name, sensor in sensor_manager.sensors.items():
            data[name] = sensor.get_data()
        
        filename = exporter.export_snapshot(data)
        st.success(f"Exported to {filename}")
    
    st.divider()
    
    # System info
    st.subheader("💻 System Info")
    try:
        import platform
        st.text(f"OS: {platform.system()} {platform.release()}")
        cpu_info = sensor_manager.get_sensor("cpu")
        if hasattr(cpu_info, 'core_count'):
            st.text(f"Cores: {cpu_info.core_count}P / {cpu_info.thread_count}L")
    except:
        st.text("System info unavailable")

# Get data from background monitor (instant, no I/O wait!)
cached_data = background_monitor.get_cached_data()

# Fallback if cache not ready yet (first 1-2 seconds)
if not cached_data or not cached_data.get('cpu'):
    st.info("⏳ Initializing background monitoring... (takes 1-2 seconds)")
    sensor_manager.update_all()
    cpu_data = sensor_manager.get_sensor("cpu").get_last_reading()
    gpu_data = sensor_manager.get_sensor("gpu").get_last_reading()
    ram_data = sensor_manager.get_sensor("ram").get_last_reading()
    disk_data = sensor_manager.get_sensor("disk").get_last_reading()
    net_data = sensor_manager.get_sensor("network").get_last_reading()
else:
    # Use cached data (instant!)
    cpu_data = cached_data['cpu']
    gpu_data = cached_data['gpu']
    ram_data = cached_data['ram']
    disk_data = cached_data['disk']
    net_data = cached_data['network']

# Normalize data for app consumption
cpu_usage = cpu_data.get('usage_percent', 0)
cpu_temp_raw = cpu_data.get('temperature', {}).get('current')
cpu_temp = cpu_temp_raw if cpu_temp_raw is not None else 0
cpu_freq = cpu_data.get('frequency', {}).get('current', 0)

# Handle GPU data (may have multiple GPUs or none)
gpu_available = gpu_data.get('available', False)
if gpu_available and gpu_data.get('gpus'):
    gpu_info = gpu_data['gpus'][0]  # Use first GPU
    gpu_usage = gpu_info.get('load_percent', 0)
    gpu_temp = gpu_info.get('temperature_c', 0)
    gpu_name = gpu_info.get('name', 'Unknown GPU')
    gpu_mem_used = gpu_info.get('memory', {}).get('used_mb', 0)
    gpu_mem_total = gpu_info.get('memory', {}).get('total_mb', 0)
else:
    gpu_usage = 0
    gpu_temp = 0
    gpu_name = "No NVIDIA GPU detected (Optimus may be using Intel iGPU)"
    gpu_mem_used = 0
    gpu_mem_total = 0

ram_percent = ram_data.get('percent', 0)
ram_used = ram_data.get('used_gb', 0)
ram_total = ram_data.get('total_gb', 0)
ram_available = ram_data.get('available_gb', 0)

# Network data
net_up = net_data.get('upload_speed_mbps', 0)
net_down = net_data.get('download_speed_mbps', 0)
net_sent = net_data.get('bytes_sent_gb', 0)
net_recv = net_data.get('bytes_recv_gb', 0)

# Update history (keep last 120 samples = 10 minutes at 5s interval)
st.session_state.history['cpu'].append(cpu_usage)
st.session_state.history['gpu'].append(gpu_usage)
st.session_state.history['ram'].append(ram_percent)
st.session_state.history['network_up'].append(net_up)
st.session_state.history['network_down'].append(net_down)

for key in st.session_state.history:
    if len(st.session_state.history[key]) > 120:
        st.session_state.history[key] = st.session_state.history[key][-120:]

# Check for alerts (AlertManager expects metrics dict, not sensor objects)
alert_manager.check_rules({
    'cpu': {'usage_percent': cpu_usage},
    'gpu': {'temperature': gpu_temp},
    'ram': {'percent': ram_percent}
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
            value=f"{cpu_usage:.1f}%",
            delta=f"{cpu_freq:.0f} MHz"
        )
        st.progress(cpu_usage / 100)
    
    with col2:
        st.metric(
            label="🎮 GPU Usage",
            value=f"{gpu_usage:.1f}%",
            delta=f"{gpu_temp:.0f}°C"
        )
        st.progress(gpu_usage / 100)
    
    with col3:
        st.metric(
            label="🧠 RAM Usage",
            value=f"{ram_percent:.1f}%",
            delta=f"{ram_used:.1f} / {ram_total:.1f} GB"
        )
        st.progress(ram_percent / 100)
    
    with col4:
        st.metric(
            label="🌐 Network",
            value=f"↓ {net_down:.1f} Mbps",
            delta=f"↑ {net_up:.1f} Mbps"
        )
    
    st.divider()
    
    # Detailed info in expandable sections
    with st.expander("🖥️ CPU Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Per-Core Usage", f"{cpu_usage:.1f}%")
            temp_display = f"{cpu_temp:.1f}°C" if cpu_temp > 0 else "N/A (Install OpenHardwareMonitor)"
            st.metric("Temperature", temp_display)
        with col2:
            st.metric("Frequency", f"{cpu_freq:.0f} MHz")
            st.metric("Power Draw", "Coming in Phase 2")
        
        st.info("🔌 **CPU Power**: Requires OpenHardwareMonitor integration (Phase 2) to read CPU package power from hardware sensors.")
    
    with st.expander("🎮 GPU Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("GPU Name", gpu_name)
            st.metric("Usage", f"{gpu_usage:.1f}%")
        with col2:
            st.metric("Temperature", f"{gpu_temp:.1f}°C")
            st.metric("Memory Used", f"{gpu_mem_used:.0f} / {gpu_mem_total:.0f} MB")
        
        if not gpu_available or "Intel" in gpu_name or "AMD" in gpu_name:
            st.info("💡 **GPU Detection Note**: You have NVIDIA RTX 5050 with Optimus hybrid graphics. If GPU shows 0%, it means Windows is using Intel iGPU for power saving. To force NVIDIA GPU:\n\n1. Open NVIDIA Control Panel\n2. Manage 3D Settings → Program Settings\n3. Add Python.exe from your .venv folder\n4. Set to 'High-performance NVIDIA processor'\n\nAlternatively: Windows Settings → Display → Graphics → Add Python.exe → High Performance")
    
    with st.expander("🧠 RAM Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Used", f"{ram_used:.2f} GB")
            st.metric("Available", f"{ram_available:.2f} GB")
        with col2:
            st.metric("Total", f"{ram_total:.2f} GB")
            st.metric("Usage %", f"{ram_percent:.1f}%")
        
        if ram_total < 24 and ram_total > 19:
            st.info("💡 **RAM Display Note**: You have 24GB installed, but Windows shows ~19.6GB available. This is normal - Windows reserves 4-5GB for:\n- Hardware reserved memory (iGPU, system)\n- Kernel and drivers\n- Memory-mapped I/O")
    
    with st.expander("💾 Disk Details"):
        st.info("ℹ️ Warming up disk I/O monitoring... (takes 2-3 seconds)")
        disks = disk_data.get('partitions', [])  # Sensor returns 'partitions'
        io_stats = disk_data.get('io_stats', {})
        
        if not disks:
            st.warning("⚠️ No disks detected. This includes internal and external drives.")
        
        for disk in disks:
            col1, col2, col3 = st.columns(3)
            with col1:
                drive_label = disk.get('mountpoint', disk.get('device', 'Unknown'))
                st.metric(f"Drive {drive_label}", f"{disk.get('percent', 0):.1f}%")
            with col2:
                st.metric("Used / Total", f"{disk.get('used_gb', 0):.0f} / {disk.get('total_gb', 0):.0f} GB")
            with col3:
                # Get I/O stats for this specific disk
                disk_io = io_stats.get(disk.get('device', '').replace(':\\', ''), {})
                read_mb = disk_io.get('read_speed_mb', 0)
                write_mb = disk_io.get('write_speed_mb', 0)
                st.metric("Read / Write", f"{read_mb:.1f} / {write_mb:.1f} MB/s")
        
        st.caption("💿 Includes all drives: Internal SSD/HDD + External USB drives (if mounted)")
    
    with st.expander("🌐 Network Details"):
        st.info("💡 **Network Speed Note**: Speed shows as 0 Mbps initially. Needs 2-3 seconds to calculate transfer rate delta. Keep dashboard open for accurate readings.")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Download Speed", f"{net_down:.2f} Mbps")
            st.metric("Total Downloaded", f"{net_recv:.2f} GB (session)")
        with col2:
            st.metric("Upload Speed", f"{net_up:.2f} Mbps")
            st.metric("Total Uploaded", f"{net_sent:.2f} GB (session)")
    
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
            width="stretch"
        )

with tab2:
    st.header("📈 Performance Charts")
    st.info("💡 Charts show recent history. Use full width for better readability. Tab switching is instant (no reload).")
    
    # CPU Usage History
    st.subheader("CPU Usage Over Time")
    if len(st.session_state.history['cpu']) > 0:
        cpu_history = pd.DataFrame({'usage': st.session_state.history['cpu']})
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=cpu_history.index,
            y=cpu_history['usage'],
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
        st.plotly_chart(fig1, width="stretch")
    else:
        st.info("Collecting CPU data... Refresh in a few seconds.")
    
    # RAM Usage History
    st.subheader("RAM Usage Over Time")
    if len(st.session_state.history['ram']) > 0:
        ram_history = pd.DataFrame({'percent': st.session_state.history['ram']})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=ram_history.index,
            y=ram_history['percent'],
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
        st.plotly_chart(fig2, width="stretch")
    else:
        st.info("Collecting RAM data... Refresh in a few seconds.")
    
    # GPU Temperature History (using usage as proxy since we track that)
    st.subheader("GPU Usage Over Time")
    if len(st.session_state.history['gpu']) > 0:
        gpu_history = pd.DataFrame({'usage': st.session_state.history['gpu']})
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=gpu_history.index,
            y=gpu_history['usage'],
            mode='lines',
            name='GPU Usage',
            line=dict(color='#ff6b35', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 53, 0.1)'
        ))
        fig3.update_layout(
            height=300,
            margin=dict(l=50, r=20, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Samples (5s interval)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Usage %', range=[0, 100])
        )
        st.plotly_chart(fig3, width="stretch")
    else:
        st.info("Collecting GPU data... Refresh in a few seconds.")
    
    # Network Speed History
    st.subheader("Network Speed Over Time")
    if len(st.session_state.history['network_down']) > 0:
        net_history = pd.DataFrame({
            'download': st.session_state.history['network_down'],
            'upload': st.session_state.history['network_up']
        })
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=net_history.index,
            y=net_history['download'],
            mode='lines',
            name='Download',
            line=dict(color='#00d4ff', width=2)
        ))
        fig4.add_trace(go.Scatter(
            x=net_history.index,
            y=net_history['upload'],
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
        st.plotly_chart(fig4, width="stretch")
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
                width="stretch"
            )
        else:
            st.info("No process data available yet. Refresh to load.")
    
    with col2:
        st.subheader("Disk Usage")
        disks = disk_data.get('partitions', [])  # Sensor returns 'partitions'
        
        if not disks:
            st.warning("No disks detected")
        
        for disk in disks:
            st.metric(
                label=f"Drive {disk.get('device', 'Unknown')}",
                value=f"{disk.get('used_gb', 0):.0f} / {disk.get('total_gb', 0):.0f} GB",
                delta=f"{disk.get('percent', 0)}% used"
            )
            st.progress(disk.get('percent', 0) / 100)
        
        st.divider()
        st.subheader("Disk I/O Speed")
        read_speed = disk_data.get('read_speed_mbps', 0)
        write_speed = disk_data.get('write_speed_mbps', 0)
        st.metric("Read Speed", f"{read_speed:.1f} MB/s")
        st.metric("Write Speed", f"{write_speed:.1f} MB/s")

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
    all_alerts = alert_manager.alert_history
    
    if all_alerts:
        alert_df = pd.DataFrame([
            {
                "Time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Level": a.level.value,
                "Message": a.message
            }
            for a in all_alerts[-20:]  # Last 20 alerts
        ])
        st.dataframe(alert_df, width="stretch", hide_index=True)
    else:
        st.info("No alerts triggered yet.")

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("GameCore Monitor v0.1.1 | Phase 1 Complete | Next: Phase 2 (Thermal & Health Deep Dive)")
with col2:
    monitor_stats = background_monitor.get_stats()
    st.caption(f"⚡ Real-time monitoring active | {monitor_stats['update_count']} updates | Avg {monitor_stats['avg_update_time_ms']:.0f}ms")
st.caption("💡 Tip: Data auto-updates in background every 1s. Just refresh browser (F5) to see latest stats.")
