# GameCore Monitor - Quick Start Guide

Welcome to **GameCore Monitor** - Your gaming & system performance intelligence suite!

## 🚀 Getting Started

### 1. Install Dependencies

Open a terminal in this directory and run:

```bash
pip install -r requirements.txt
```

### 2. Launch the Monitor

**Easy way:**
```bash
python start.py
```

**Direct way:**
```bash
streamlit run app.py
```

### 3. Access the Dashboard

The dashboard will automatically open in your default browser at:
```
http://localhost:8501
```

## 📊 Features Available (v0.1)

### Real-Time Monitoring
- **CPU**: Usage %, frequency, temperature, per-core stats
- **GPU**: Usage %, temperature, VRAM (NVIDIA cards)
- **RAM**: Usage %, available memory, swap stats
- **Disk**: Free space, read/write speeds, I/O statistics
- **Network**: Upload/download speeds, connection counts
- **System**: Uptime, process counts, resource consumers

### Smart Alerts
- CPU usage > 90% for 2 minutes
- GPU temperature > 85°C
- RAM usage > 90% for 1 minute
- Disk space < 10%

### Data Export
- Export current system snapshot (JSON)
- Export performance history (CSV)
- Automatic logging to `data/logs/`

## 🎮 Dashboard Navigation

### Main View
- **Top Metrics**: Real-time CPU, RAM, GPU, Network
- **Performance Charts**: Historical trends with live updates
- **Quick Stats**: System uptime and process count

### Tabs
1. **Overview**: Live performance graphs
2. **Processes**: Top CPU/memory consumers
3. **Disk**: Drive usage and I/O speeds
4. **Alerts**: Active alerts and history

### Sidebar
- Adjust refresh interval (1-10 seconds)
- Enable/disable specific sensors
- Export data snapshots
- View system information

## ⚙️ Configuration

Edit `config/default_config.json` to customize:

```json
{
  "monitoring": {
    "refresh_interval": 2,
    "history_length": 300
  },
  "alerts": {
    "cpu_threshold": 90,
    "gpu_temp_threshold": 85,
    "disk_space_threshold": 10
  }
}
```

## 🔧 Troubleshooting

### GPU Not Detected
- Ensure you have an NVIDIA GPU
- Install NVIDIA drivers
- GPUtil requires proper NVIDIA toolkit

### Temperature Not Showing
- Run as Administrator for full hardware access
- Install OpenHardwareMonitor for better temperature support
- Some systems require WMI configuration

### High CPU Usage from Monitor
- Increase refresh interval in sidebar
- Disable unused sensors
- Reduce history length in config

## 📁 Project Structure

```
GameCore Monitor/
├── app.py                  # Main Streamlit dashboard
├── start.py               # Quick start launcher
├── requirements.txt       # Python dependencies
├── config/
│   └── default_config.json
├── src/
│   ├── sensors/           # Hardware monitoring modules
│   ├── alerts/            # Alert system
│   └── utils/             # Utilities (export, logging)
└── data/
    ├── exports/           # Exported data files
    └── logs/              # Application logs
```

## 🎯 What's Next?

**Phase 2** (Coming Soon):
- Advanced thermal monitoring
- Fan speed control
- Disk SMART analytics
- Custom alert rules

**Phase 3** (Future):
- Game library detection (Steam, Epic, Xbox)
- Drive usage mapping
- Game metadata and stats

**Phase 4** (Advanced):
- Safe game mover with robocopy
- One-click game relocation
- Save file backup

## 💡 Tips

1. **First Run**: Let it run for a few minutes to build performance history
2. **Admin Rights**: Run as admin for full hardware access (temperatures, SMART)
3. **Background Running**: Minimize to system tray for continuous monitoring
4. **Performance**: Disable sensors you don't need to reduce overhead

## 🐛 Known Limitations

- GPU monitoring currently supports NVIDIA only
- Temperature readings require admin rights on some systems
- Network speed calculation requires ~2 seconds to initialize
- SMART data availability varies by hardware

## 📝 Notes for Development

This is **v0.1** - the foundation phase. Core monitoring is stable and production-ready.

The architecture is designed for expansion:
- **Sensor abstraction layer** makes adding new sensors easy
- **Alert system** is fully extensible
- **Export utilities** support multiple formats
- **Config manager** handles user customization

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

MIT License - See LICENSE file for details

---

**GameCore Monitor** - Built for gaming infrastructure excellence.

Questions or issues? Check the logs in `data/logs/` for detailed error information.
