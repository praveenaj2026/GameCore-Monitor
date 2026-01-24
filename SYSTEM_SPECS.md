# System Specifications - HP Victus 15-fa2409TX

## Hardware Profile

### Processor
- **CPU**: Intel Core 7 240H (Raptor Lake-H Refresh)
- **Cores/Threads**: 10 cores (6P + 4E) / 16 threads
- **Base Clock**: 2.4 GHz
- **Max Turbo**: 5.2 GHz
- **L3 Cache**: 24 MB
- **TDP**: 45W (boosts higher)

### Graphics
- **Discrete GPU**: NVIDIA GeForce RTX 5050 Laptop
- **VRAM**: 8 GB GDDR7
- **Ray Tracing**: Yes (3rd gen)
- **DLSS**: DLSS 3 with Frame Generation
- **Mux Switch**: ❌ No (Optimus only)
- **GPU Power**: ~75-90W

- **Integrated GPU**: Intel UHD Graphics (Xe-LP)
- **Usage**: Power saving, video decode

### Memory
- **Installed**: 24 GB DDR5
- **Speed**: DDR5-5600 MT/s
- **Configuration**: 1×24 GB (Single channel)
- **Slots**: 2 SO-DIMM
- **Max Supported**: 32 GB

**Note**: Currently single-channel. Dual-channel (2×16GB) provides 5-10% uplift in CPU-bound games.

### Storage
- **Primary**: 1 TB PCIe Gen4 NVMe SSD
- **Expansion**: ❌ No second NVMe slot
- **SATA Bay**: ❌ Not present

### Display
- **Size**: 15.6" (39.6 cm)
- **Resolution**: 1920×1080 (Full HD)
- **Refresh Rate**: 144 Hz
- **Panel**: IPS, Anti-glare
- **Brightness**: 300 nits
- **Color Gamut**: ~62.5% sRGB

### Connectivity
- **USB-A**: 2× USB 3.2 Gen 1 (5 Gbps)
- **USB-C**: 1× USB-C 5 Gbps (DP 1.4a, PD 3.1)
- **HDMI**: HDMI 2.1
- **Ethernet**: RJ-45 Gigabit
- **Wi-Fi**: Wi-Fi 6 (2×2)
- **Bluetooth**: 5.4

### Battery & Power
- **Battery**: 70 Wh (4-cell Li-ion)
- **Adapter**: 200W HP Smart AC
- **Fast Charge**: 50% in ~30 min

### Physical
- **Weight**: ~2.29 kg
- **Chassis**: Plastic (Mica Silver)
- **Keyboard**: Full-size + numpad, 1-zone RGB
- **Cooling**: Dual-fan, shared heatpipes

---

## GameCore Monitor Configuration Notes

### ⚠️ Hybrid Graphics (Optimus)
Your laptop has **BOTH** Intel iGPU + NVIDIA RTX 5050.

**Issue**: Windows may use Intel iGPU by default for power saving.

**Solution**: Force GameCore Monitor to use NVIDIA GPU:

#### Method 1: NVIDIA Control Panel
1. Right-click Desktop → NVIDIA Control Panel
2. Manage 3D Settings → Program Settings
3. Add: `python.exe` (from GameCore Monitor venv)
4. Select: "High-performance NVIDIA processor"

#### Method 2: Windows Graphics Settings
1. Settings → Display → Graphics Settings
2. Browse → Add Python.exe
3. Options → High Performance

### Expected Monitoring Values

**CPU**:
- Idle: 5-15%
- Gaming: 40-70%
- Max Turbo: 5.2 GHz
- Temp: 35-45°C idle, 75-90°C gaming

**GPU (RTX 5050)**:
- VRAM: 8192 MB total
- Idle: 0-5%
- Gaming: 60-99%
- Temp: 40-50°C idle, 70-85°C gaming

**RAM**:
- Total: 24 GB
- Available to OS: ~19-20 GB (4-5 GB reserved by Windows)
- Single-channel: May show lower bandwidth

**Storage**:
- 1 TB NVMe Gen4
- Read: 5000-7000 MB/s
- Write: 4000-5000 MB/s

### Optimization Recommendations

**Memory**:
- Consider 2×16 GB for dual-channel (5-10% FPS boost)
- Improves CPU-bound game performance

**Thermal**:
- Elevate laptop for better airflow
- Clean vents every 3-6 months
- Consider cooling pad for sustained gaming

**Storage**:
- External USB 3.2 SSD for game storage
- Keep main drive < 80% full for performance

**Power**:
- Use plugged in for gaming (200W adapter)
- Battery gaming limits GPU to ~60W

---

## Benchmark Expectations

**1080p Gaming (RTX 5050 + DLSS)**:
- AAA Titles (High/Ultra): 60-80 FPS
- Competitive (Medium): 100-144 FPS
- DLSS Quality: +30-50% FPS
- Ray Tracing: Playable with DLSS

**CPU Performance**:
- Cinebench R23: ~12,000-14,000 multi-core
- Single-core: ~1,800-2,000
- Excellent for emulation (PS3, Switch)

**Thermal Under Load**:
- CPU: 85-95°C (normal for gaming laptops)
- GPU: 75-85°C (well within spec)
- Thermal throttling: Rare with proper cooling

---

## Known Limitations

1. **No Mux Switch**: ~5-15% FPS loss vs direct GPU connection
2. **Single-channel RAM**: 5-10% performance loss
3. **No storage expansion**: External SSD required for extra games
4. **Plastic build**: Less premium feel than metal chassis
5. **Average display color**: Not ideal for photo/video editing

---

## Perfect Use Cases

✅ **Excellent For**:
- 1080p AAA gaming (High/Ultra)
- DLSS-enabled titles
- Emulation (PS2/PS3/Switch)
- External SSD gaming library
- Productivity + gaming hybrid use

❌ **Not Ideal For**:
- 4K gaming
- Competitive 240Hz gaming
- Color-critical creative work
- Maximum RGB customization
- Internal multi-drive gaming library

---

**GameCore Monitor** is perfect for managing this system's thermal profile and game library!
