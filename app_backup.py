"""
GameCore Monitor - Main Streamlit Dashboard
Gaming & System Performance Intelligence
"""

import streamlit as st
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd

# Import GameCore modules
from src.sensors import SensorManager
from src.alerts import AlertManager, create_default_rules, AlertLevel
from src.utils.config_manager import ConfigManager
from src.utils.data_export import DataExporter
from src.utils.logger import setup_logging

# Page configuration
st.set_page_config(
    page_title="GameCore Monitor",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache sensor data to prevent full reloads
@st.cache_resource
def get_sensor_manager():
    """Get cached sensor manager instance"""
    return SensorManager()

@st.cache_resource
def get_alert_manager():
    """Get cached alert manager instance"""
    manager = AlertManager()
    for rule in create_default_rules():
        manager.add_rule(rule)
    return manager

@st.cache_resource
def get_config():
    """Get cached config manager"""
    return ConfigManager()

@st.cache_resource
def get_exporter():
    """Get cached data exporter"""
    return DataExporter()

@st.cache_resource
def get_logger():
    """Get cached logger"""
    return setup_logging()

# Initialize session state with cached instances
if 'initialized' not in st.session_state:
    st.session_state.sensor_manager = get_sensor_manager()
    st.session_state.alert_manager = get_alert_manager()
    st.session_state.config = get_config()
    st.session_state.exporter = get_exporter()
    st.session_state.logger = get_logger()
    st.session_state.history = {
        'timestamps': [],
        'cpu': [],
        'ram': [],
        'gpu_temp': [],
        'gpu_load': [],
        'net_down': [],
        'net_up': []
    }
    st.session_state.max_history = 120  # Keep 120 data points (2 minutes at 1sec refresh)
    st.session_state.initialized = True
    st.session_state.logger.info("GameCore Monitor initialized")

# Preload all data at start
if 'all_processes' not in st.session_state:
    st.session_state.all_processes = []
if 'disk_data_cached' not in st.session_state:
    st.session_state.disk_data_cached = {}
if 'alerts_cached' not in st.session_state:
    st.session_state.alerts_cached = []

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00ff88;
    }
    .alert-critical {
        background-color: #ff4444;
        padding: 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .alert-warning {
        background-color: #ffaa00;
        padding: 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .stMetric {
        background-color: #2b2b2b;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🎮 GameCore Monitor")
st.markdown("**Gaming & System Performance Intelligence** | v0.1.0")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Refresh interval
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 2)
    
    # Sensor toggles
    st.subheader("Active Sensors")
    enable_cpu = st.checkbox("CPU", value=True)
    enable_gpu = st.checkbox("GPU", value=True)
    enable_ram = st.checkbox("RAM", value=True)
    enable_disk = st.checkbox("Disk", value=True)
    enable_network = st.checkbox("Network", value=True)
    
    st.divider()
    
    # Export options
    st.subheader("📊 Export")
    if st.button("Export Current Snapshot"):
        metrics = st.session_state.sensor_manager.read_all()
        filepath = st.session_state.exporter.create_snapshot(metrics)
        st.success(f"Snapshot saved to: {filepath}")
    
    if st.button("Export History (CSV)"):
        if st.session_state.history['timestamps']:
            df = pd.DataFrame(st.session_state.history)
            filepath = st.session_state.exporter.export_to_csv(df.to_dict('records'))
            st.success(f"History saved to: {filepath}")
        else:
            st.warning("No history data available")
    
    st.divider()
    
    # System info
    st.subheader("ℹ️ System Info")
    metrics = st.session_state.sensor_manager.system.read()
    st.text(f"Uptime: {metrics['uptime']['formatted']}")
    st.text(f"Processes: {metrics['processes']['total']}")

# Read all sensors
metrics = st.session_state.sensor_manager.read_all()

# Update history
if len(st.session_state.history['timestamps']) >= st.session_state.max_history:
    # Remove oldest entries
    for key in st.session_state.history:
        st.session_state.history[key].pop(0)

st.session_state.history['timestamps'].append(datetime.now())
st.session_state.history['cpu'].append(metrics.get('cpu', {}).get('usage_percent', 0))
st.session_state.history['ram'].append(metrics.get('ram', {}).get('percent', 0))

gpu_data = metrics.get('gpu', {})
if gpu_data.get('available') and gpu_data.get('gpus'):
    st.session_state.history['gpu_temp'].append(gpu_data['gpus'][0].get('temperature_c', 0))
    st.session_state.history['gpu_load'].append(gpu_data['gpus'][0].get('load_percent', 0))
else:
    st.session_state.history['gpu_temp'].append(0)
    st.session_state.history['gpu_load'].append(0)

net_data = metrics.get('network', {})
st.session_state.history['net_down'].append(net_data.get('download_speed_mbps', 0))
st.session_state.history['net_up'].append(net_data.get('upload_speed_mbps', 0))

# Cache process and disk data (update every cycle)
st.session_state.all_processes = st.session_state.sensor_manager.system.get_top_processes(count=15)
st.session_state.disk_data_cached = metrics.get('disk', {})

# Check alerts
new_alerts = st.session_state.alert_manager.check_rules(metrics)

# Display critical alerts
critical_alerts = st.session_state.alert_manager.get_active_alerts(AlertLevel.CRITICAL)
if critical_alerts:
    for alert in critical_alerts:
        if not alert.acknowledged:
            st.error(f"🚨 CRITICAL: {alert.message}")

warning_alerts = st.session_state.alert_manager.get_active_alerts(AlertLevel.WARNING)
if warning_alerts:
    for alert in warning_alerts:
        if not alert.acknowledged:
            st.warning(f"⚠️ WARNING: {alert.message}")

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    cpu_data = metrics.get('cpu', {})
    st.metric(
        "CPU Usage",
        f"{cpu_data.get('usage_percent', 0):.1f}%",
        delta=None
    )
    st.caption(f"Freq: {cpu_data.get('frequency', {}).get('current', 0):.0f} MHz")
    
    temp = cpu_data.get('temperature', {}).get('current')
    if temp:
        st.caption(f"Temp: {temp}°C")

with col2:
    ram_data = metrics.get('ram', {})
    st.metric(
        "RAM Usage",
        f"{ram_data.get('percent', 0):.1f}%",
        delta=None
    )
    st.caption(f"{ram_data.get('used_gb', 0):.1f} GB / {ram_data.get('total_gb', 0):.1f} GB")

with col3:
    gpu_data = metrics.get('gpu', {})
    if gpu_data.get('available') and gpu_data.get('gpus'):
        gpu = gpu_data['gpus'][0]
        st.metric(
            "GPU Usage",
            f"{gpu.get('load_percent', 0):.1f}%",
            delta=None
        )
        st.caption(f"Temp: {gpu.get('temperature_c', 0)}°C")
        st.caption(f"VRAM: {gpu.get('memory', {}).get('percent', 0):.1f}%")
    else:
        st.metric("GPU", "Integrated/AMD")
        st.caption("NVIDIA GPU not detected")
        st.caption("(AMD support in v0.2)")

with col4:
    net_data = metrics.get('network', {})
    st.metric(
        "Network",
        f"↓ {net_data.get('download_speed_mbps', 0):.1f} Mbps"
    )
    st.caption(f"↑ {net_data.get('upload_speed_mbps', 0):.1f} Mbps")

st.divider()
Navigation tabs - but load all data upfront
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Performance Charts", "💻 Processes & Disk", "🔔 Alerts"])

with tab1:
    st.subheader("System Overview")
    
    # System info cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💻 System")
        sys_data = metrics.get('system', {})
        st.text(f"Uptime: {sys_data.get('uptime', {}).get('formatted', 'N/A')}")
        st.text(f"Processes: {sys_data.get('processes', {}).get('total', 0)}")
        st.text(f"CPU Cores: {metrics.get('cpu', {}).get('core_count', 0)}")
        st.text(f"CPU Threads: {metrics.get('cpu', {}).get('thread_count', 0)}")
    
    with col2:
        st.markdown("### 🌡️ Temperatures")
        cpu_temp = metrics.get('cpu', {}).get('temperature', {}).get('current')
        if cpu_temp:
            st.text(f"CPU: {cpu_temp}°C")
        else:
            st.text("CPU: Not available")
        
        if gpu_data.get('available') and gpu_data.get('gpus'):
            gpu_temp = gpu_data['gpus'][0].get('temperature_c', 0)
            st.text(f"GPU: {gpu_temp}°C")
        else:
            st.text("GPU: Not available")
    
    with col3:
        st.markdown("### 📊 Quick Stats")
        st.text(f"CPU Frequency: {metrics.get('cpu', {}).get('frequency', {}).get('current', 0):.0f} MHz")
        ram_used = metrics.get('ram', {}).get('used_gb', 0)
        ram_total = metrics.get('ram', {}).get('total_gb', 0)
        st.text(f"RAM: {ram_used:.1f} / {ram_total:.1f} GB")
        
        if gpu_data.get('available') and gpu_data.get('gpus'):
            vram_used = gpu_data['gpus'][0].get('memory', {}).get('used_mb', 0) / 1024
            vram_total = gpu_data['gpus'][0].get('memory', {}).get('total_mb', 0) / 1024
            st.text(f"VRAM: {vram_used:.1f} / {vram_total:.1f} GB")
    
    st.divider()
    
    # Top 5 processes
    st.subheader("Top 5 Resource Consumers")
    if st.session_state.all_processes:
        top5 = st.session_state.all_processes[:5]
        df_top5 = pd.DataFrame(top5)
        st.dataframe(
            df_top5,
            column_config={
                "name": "Process",
                "cpu_percent": st.column_config.NumberColumn("CPU %", format="%.1f%%"),
                "memory_percent": st.column_config.NumberColumn("Memory %", format="%.1f%%"),
            },
            hide_index=True,
            width='stretch'
        )

with tab2:
    st.subheader("Performance Trends (Last 2 Minutes)")
    
    # Better chart with proper axes
    fig1 = go.Figure()
    
    # CPU Usage Chart
    fig1.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history['cpu']))),
        y=st.session_state.history['cpu'],
        mode='lines+markers',
        name='CPU %',
        line=dict(color='#00ff88', width=3),
        marker=dict(size=4),
        hovertemplate='CPU: %{y:.1f}%<extra></extra>'
    ))
    
    fig1.update_layout(
        title="CPU Usage Over Time",
        xaxis_title="Time (samples)",
        yaxis_title="Usage (%)",
        3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💻 All Processes (Top 15)")
        
        if st.session_state.all_processes:
            df = pd.DataFrame(st.session_state.all_processes)
            st.dataframe(
                df,
                column_config={
                    "pid": "PID",
                    "name": "Process",
                    "cpu_percent": st.column_config.NumberColumn("CPU %", format="%.1f%%"),
                    "memory_percent": st.column_config.NumberColumn("Memory %", format="%.1f%%"),
                    "status": "Status"
                },
                hide_index=True,
                width='stretch',
                height=400
            )
    
    with col2:
        st.subheader("💾 Disk Usage")
        
        disk_data = st.session_state.disk_data_cached
        partitions = disk_data.get('partitions', [])
        
        for partition in partitions:
            st.markdown(f"**{partition['mountpoint']}** ({partition['device']})")
            
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.progress(partition['percent'] / 100)
            with col_b:
                st.metric("Used", f"{partition['used_gb']:.1f} GB", delta=None)
            with col_c:
                st.metric("Free", f"{partition['free_gb']:.1f} GB", delta=None)
            
            st.caption(f"Total: {partition['total_gb']:.1f} GB | {partition['percent']:.1f}% used")
            st.divider()
        
        # Disk I/O
        st.subheader("💾 Disk I/O Speed")
        io_stats = disk_data.get('io_stats', {})
        
        if io_stats:
            for disk, stats in io_stats.items():
                st.text(f"📀 {disk}")
                st.text(f"   Read: {stats['read_speed_mb']:.2f} MB/s")
                st.text(f"   Write: {stats['write_speed_mb']:.2f} MB/s")
                st.text("")
        else:
            st.info("Warming up disk I/O monitoring... (takes 2-3 seconds)")
        
        fig3.update_layout(
            title="GPU Temperature Over Time",
            xaxis_title="Time (samples)",
            yaxis_title="Temperature (°C)",
            yaxis=dict(range=[0, 100]),
            height=300,
            template="plotly_dark",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig3, width='stretch')
    
    # Network Speed Chart
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history['net_down']))),
        y=st.session_state.history['net_down'],
        mode='lines',
        name='Download',
        line=dict(color='#00ff00', width=2),
        hovertemplate='↓ %{y:.2f} Mbps<extra></extra>'
    ))
    
    fig4.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history['net_up']))),
        y=st.session_state.history['net_up'],
        mode='lines',
        name='Upload',
        line=dict(color='#ff00ff', width=2),
        hovertemplate='↑ %{y:.2f} Mbps<extra></extra>'
    ))
    
    fig4.update_layout(
        title="Network Speed Over Time",
        xaxis_title="Time (samples)",
        yaxis_title="Speed (Mbps)",
        height=300,
        template="plotly_dark",
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig4, width='stretch')

with tab3
with tab2:
    st.subheader("Top Resource Consumers")
    
    top_processes = st.session_state.sensor_manager.system.get_top_processes(count=15)
    
    if top_processes:
        df = pd.DataFrame(top_processes)
        st.dataframe(
            df,
            column_config={
                "pid": "PID",
                "name": "Process",
                "cpu_percent": st.column_config.NumberColumn("CPU %", format="%.1f%%"),
                "memory_percent": st.column_config.NumberColumn("Memory %", format="%.1f%%"),
                "status": "Status"
            },
            hide_index=True,
            width='stretch'
        )

with tab3:
    st.subheader("Disk Usage")
    
    disk_data = metrics.get('disk', {})
    partitions = disk_data.get('partitions', [])
    
    for partition in partitions:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.progress(partition['percent'] / 100)
            st.caption(f"{partition['mountpoint']} - {partition['device']}")
        
        with col2:
            st.metric(
                "Free",
                f"{partition['free_gb']:.1f} GB",
                delta=None
            )
    
    # Disk I/O
    st.subheader("Disk I/O")
    io_stats = disk_data.get('io_stats', {})
    
    if io_stats:
        for disk, stats in io_stats.items():
            st.text(f"{disk}: Read {stats['read_speed_mb']:.1f} MB/s | Write {stats['write_speed_mb']:.1f} MB/s")

with tab4:
    st.subheader("Active Alerts")
    
    active_alerts = st.session_state.alert_manager.get_active_alerts()
    
    if active_alerts:
        for i, alert in enumerate(active_alerts):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if alert.level == AlertLevel.CRITICAL:
                    st.error(f"🚨 {alert.message} - {alert.timestamp}")
                elif alert.level == AlertLevel.WARNING:
                    st.warning(f"⚠️ {alert.message} - {alert.timestamp}")
                else:
                    st.info(f"ℹ️ {alert.message} - {alert.timestamp}")
            
            with col2:
                if st.button("Clear", key=f"clear_{i}"):
                    st.session_state.alert_manager.acknowledge_alert(alert)
                    st.rerun()
        
        if st.button("Clear All Acknowledged"):
            st.session_state.alert_manager.clear_acknowledged()
            st.rerun()
    else:
        st.success("✅ No active alerts")
    
    st.subheader("Alert History")
    history = st.session_state.alert_manager.alert_history[-10:]
    
    if history:
        for alert in reversed(history):
            st.caption(f"{alert.timestamp.strftime('%H:%M:%S')} - {alert.level.value.upper()}: {alert.message}")

# Auto-refresh
time.sleep(refresh_interval)
st.rerun()
