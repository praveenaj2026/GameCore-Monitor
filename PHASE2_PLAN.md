# Phase 2 Implementation Plan
## Thermal & Health Deep Dive - v0.2.0

### 🎯 Goals
Transform basic monitoring into **professional-grade hardware diagnostics** with:
- Per-core CPU temperatures
- CPU/GPU power consumption
- Fan speed monitoring
- Disk SMART health analytics
- Battery status (for your laptop)

---

## 📊 Priority Order (Your HP Victus 15)

### **Priority 1: OpenHardwareMonitor Integration** ⭐
**Why First:** Unlocks ALL advanced sensors at once
- Per-core CPU temps (all 16 threads)
- CPU package power (28-64W)
- GPU power consumption
- Fan speeds (CPU fan, GPU fan)
- Motherboard temps

**Implementation:**
```python
# New sensor: thermal_sensor.py
from LibreHardwareMonitor import Hardware

class ThermalSensor:
    - Read all temperature sensors
    - Per-core CPU temps
    - GPU hotspot temp
    - Motherboard VRM temps
```

**Benefits for You:**
- See which cores get hottest during gaming
- Monitor if laptop cooling is adequate
- Detect thermal throttling

---

### **Priority 2: Power Monitoring** ⚡
**Your Hardware:**
- Intel Core 7 240H: 28W base, 64W turbo
- RTX 5050: ~75W TGP (laptop variant)
- Total system: ~140W under load

**Implementation:**
```python
class PowerSensor:
    - CPU package power
    - GPU power draw
    - Battery charge/discharge rate
    - Estimated system total
```

**Benefits:**
- Know if you're thermal throttling
- Optimize power vs performance
- Battery drain rate estimation

---

### **Priority 3: Enhanced GPU Monitoring** 🎮
**Current:** Basic usage, temp, memory
**Add:**
- GPU clock speeds (core, memory)
- GPU power limit
- Fan speed (% and RPM)
- PCIe link speed

**Your RTX 5050 Specs:**
- Base: 1650 MHz
- Boost: 2370 MHz
- Memory: 2000 MHz (16 Gbps GDDR7)
- Power: 60-75W

---

### **Priority 4: Disk SMART Analytics** 💾
**For Your 1TB NVMe:**
- Drive health percentage
- Temperature
- Total bytes written (wear level)
- Power-on hours
- Estimated lifespan

**Implementation:**
```python
class SMARTSensor:
    - Read SMART attributes via WMI
    - Parse critical values
    - Predict failure warnings
```

---

### **Priority 5: Fan Control & Monitoring** 🌪️
**Your Laptop Fans:**
- CPU cooling fan
- GPU cooling fan (shared heat pipe?)

**Implementation:**
```python
class FanSensor:
    - Read fan speeds (RPM)
    - Calculate fan duty cycle (%)
    - Visualize fan curves
```

**Note:** Fan *control* (changing speeds) may be locked by HP BIOS.

---

## 🛠️ Technical Implementation

### Step 1: LibreHardwareMonitor Setup
**Why LibreHardwareMonitor vs OpenHardwareMonitor?**
- ✅ Actively maintained (2025+ updates)
- ✅ Better Windows 11 support
- ✅ More sensors supported
- ✅ Python bindings available

**Installation:**
```bash
# Option A: Python package (if exists)
pip install LibreHardwareMonitor

# Option B: COM wrapper
pip install pythonnet
# Use .NET assembly directly
```

**Requires:**
- Admin rights (to read MSR/SMBus)
- Service running in background

---

### Step 2: New Sensors Architecture

**New Files:**
```
src/sensors/
  ├── thermal_sensor.py      # Per-core temps, motherboard
  ├── power_sensor.py        # CPU/GPU/battery power
  ├── fan_sensor.py          # Fan speeds
  ├── smart_sensor.py        # Disk health
  └── enhanced_gpu_sensor.py # Extended GPU metrics
```

**Integration:**
```python
# Update sensor_manager.py
self.sensors = {
    "cpu": CPUSensor(),
    "gpu": GPUSensor(),
    "ram": RAMSensor(),
    "disk": DiskSensor(),
    "network": NetworkSensor(),
    
    # NEW Phase 2 sensors:
    "thermal": ThermalSensor(),    # ← Per-core temps
    "power": PowerSensor(),        # ← Power consumption
    "fans": FanSensor(),           # ← Fan speeds
    "smart": SMARTSensor()         # ← Disk health
}
```

---

### Step 3: Dashboard Updates

**New Tab: "🔥 Thermal & Power"**

**Layout:**
```
┌─────────────────────────────────────┐
│  CPU Core Temperatures (16 cores)  │
│  ████ ████ ████ ████  (heatmap)   │
├─────────────────────────────────────┤
│  Power Consumption                  │
│  CPU: 45W ████████                 │
│  GPU: 60W ████████████             │
├─────────────────────────────────────┤
│  Fan Speeds                         │
│  CPU Fan: 3200 RPM (65%)           │
│  GPU Fan: 3800 RPM (75%)           │
└─────────────────────────────────────┘
```

**New Tab: "💾 Disk Health"**
```
┌─────────────────────────────────────┐
│  C:\ NVMe Health: 98% ✅           │
│  Temperature: 45°C                  │
│  Total Writes: 15.2 TB              │
│  Power-On Hours: 1,234h             │
│  Estimated Life: 4+ years           │
└─────────────────────────────────────┘
```

---

### Step 4: Enhanced Visualizations

**CPU Core Temp Heatmap:**
```python
import plotly.graph_objects as go

fig = go.Figure(data=go.Heatmap(
    z=core_temps.reshape(8, 2),  # 8 P-cores + E-cores
    colorscale='RdYlGn_r',
    zmin=30, zmax=100
))
```

**Power Consumption Over Time:**
```python
# Stacked area chart
fig.add_trace(go.Scatter(
    x=time, y=cpu_power,
    fill='tozeroy', name='CPU'
))
fig.add_trace(go.Scatter(
    x=time, y=gpu_power,
    fill='tonexty', name='GPU'
))
```

**Fan Speed vs Temperature:**
```python
# Dual-axis chart
fig.add_trace(go.Scatter(
    y=fan_rpm, name='Fan Speed'
))
fig.add_trace(go.Scatter(
    y=temp, name='Temperature',
    yaxis='y2'
))
```

---

## 🎯 Phase 2 Milestones

### **Milestone 1: LibreHardwareMonitor Integration** (Week 1)
- [ ] Install and test LibreHardwareMonitor
- [ ] Create thermal_sensor.py
- [ ] Read per-core CPU temps
- [ ] Display in dashboard

### **Milestone 2: Power Monitoring** (Week 1-2)
- [ ] Create power_sensor.py
- [ ] Read CPU package power
- [ ] Read GPU power (via nvidia-smi or sensors)
- [ ] Add battery monitoring
- [ ] Create power consumption charts

### **Milestone 3: Enhanced GPU & Fans** (Week 2)
- [ ] Extend gpu_sensor.py with clocks
- [ ] Create fan_sensor.py
- [ ] Read fan speeds
- [ ] Visualize fan curves

### **Milestone 4: SMART Analytics** (Week 2-3)
- [ ] Create smart_sensor.py
- [ ] Parse SMART attributes
- [ ] Calculate disk health score
- [ ] Add predictive warnings

### **Milestone 5: Dashboard Polish** (Week 3)
- [ ] New "Thermal & Power" tab
- [ ] New "Disk Health" tab
- [ ] Heatmap visualizations
- [ ] Alert rules for thermal/power

---

## 💡 Expected Results

### **Before Phase 2:**
```
CPU: 15% usage, 2499 MHz, N/A temp
GPU: 0% usage, 52°C
```

### **After Phase 2:**
```
CPU: 15% usage, 2499 MHz
  Core 0: 45°C | Core 1: 47°C | Core 2: 43°C ...
  Package Power: 28W (Base) | Max: 64W

GPU: RTX 5050
  Core: 1650 MHz | Memory: 2000 MHz
  Power: 15W idle | Max: 75W
  Fan: 1200 RPM (30%)

Disk: Samsung NVMe
  Health: 98% ✅
  Temp: 45°C
  Writes: 15.2 TB
  Life: 4+ years remaining

Fans:
  CPU: 2800 RPM (60%)
  GPU: 3200 RPM (65%)
```

---

## 🚨 Prerequisites Check

### **Required:**
- ✅ Windows (you have)
- ✅ Admin rights (needed for hardware access)
- ⚠️ LibreHardwareMonitor compatible hardware

### **Your Hardware Compatibility:**
- ✅ Intel Core 7 240H - Full support
- ✅ NVIDIA RTX 5050 - Full support via nvidia-smi
- ✅ NVMe SSD - SMART via WMI
- ✅ Laptop battery - Windows API

---

## 🎮 Benefits for Gaming

### **Thermal Monitoring:**
- See if laptop throttles during gaming
- Know when to clean fans
- Optimize game settings for thermals

### **Power Monitoring:**
- See power consumption per game
- Know battery drain rate
- Optimize for battery vs performance

### **Disk Health:**
- Know if SSD is healthy
- Predict when to upgrade
- Monitor game install wear

---

## 📝 Questions Before We Start:

1. **Do you have admin rights on your laptop?** (Required for thermal sensors)
2. **Any specific sensors you want FIRST?** (Per-core temps? Power? SMART?)
3. **How detailed should fan monitoring be?** (Just speeds, or try control too?)
4. **Want battery stats since it's a laptop?** (Charge rate, health, time remaining)

**Ready to start Phase 2?** I'll begin with LibreHardwareMonitor integration! 🚀
