# GameCore Monitor

**Gaming & System Performance Intelligence**

A comprehensive desktop dashboard for monitoring PC health, hardware performance, and gaming infrastructure.

## 🎯 Project Vision

GameCore Monitor is the foundation of a gaming infrastructure suite, designed to provide real-time insights into:
- Hardware performance (CPU, GPU, RAM, Disk)
- System health and thermal monitoring
- Process management and resource consumption
- Network activity and uptime tracking

## 🚀 Current Version: v0.1

**Phase 1 - Core PC Monitor**

### Features
- ✅ Real-time CPU monitoring (usage, frequency, temperature)
- ✅ GPU monitoring (usage, temperature, VRAM)
- ✅ RAM usage tracking
- ✅ Disk health (free space, read/write speed, SMART status)
- ✅ Network speed monitoring (upload/download)
- ✅ Top resource-consuming processes
- ✅ System uptime tracking
- ✅ Intelligent alerts system

### Alerts
- CPU usage > 90% for 2 minutes
- GPU temperature > 85°C
- Disk space < 10%

## 🛠️ Tech Stack

- **Python 3.8+**
- **psutil** - CPU, RAM, disk, network monitoring
- **wmi / pywin32** - Hardware temperatures and info
- **GPUtil** - GPU statistics
- **Streamlit** - Interactive dashboard UI

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the monitor
streamlit run app.py
```

## 🗂️ Project Structure

```
GameCore-Monitor/
├── src/
│   ├── sensors/          # Hardware sensor abstraction layer
│   ├── monitors/         # Monitoring modules
│   ├── alerts/           # Alert system
│   └── utils/            # Helper utilities
├── data/                 # Logs and exports
├── config/               # Configuration files
├── app.py               # Streamlit dashboard
└── requirements.txt     # Dependencies
```

## 🎮 Future Roadmap

**Phase 2** - Thermal & Health Deep Dive
- Advanced GPU monitoring
- Fan speed control
- Disk SMART analytics

**Phase 3** - Game Library Indexer
- Detect Steam/Epic/Xbox games
- Drive usage mapping
- Game metadata

**Phase 4** - Safe Game Mover (Flagship)
- One-click game relocation
- Robocopy-powered transfers
- Resume-safe operations

**Phase 5** - Analytics & Intelligence
- Performance history
- Disk usage trends
- Gaming insights

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built with precision for gaming infrastructure excellence.

---

**GameCore Monitor** - The foundation of your gaming performance suite.
