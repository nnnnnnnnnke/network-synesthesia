# Network Synesthesia

Real-time network traffic visualization and sonification. Packets become particles of light and musical notes.

## Demo

[![Demo Video](demo-thumbnail.jpg)](https://github.com/nnnnnnnnnke/network-synesthesia/releases/download/v1.0.0/demo.mp4)

*Click the image to download the demo video (with sound)*

## What it does

- Captures live network packets via `tcpdump`
- Streams packet data to the browser via WebSocket
- Each protocol has a unique color and instrument:
  - **HTTP/S** (blue, sine wave pad)
  - **DNS** (yellow, bell/chime)
  - **SSH** (green, sawtooth bass)
  - **ICMP** (red, percussion)
  - **TCP** (purple, sine)
  - **UDP** (gray, triangle)
- Packets fly as glowing particles between source and destination hosts
- Pentatonic scale ensures everything sounds harmonious
- Built-in reverb for ambient atmosphere

## Architecture

```
tcpdump → Python (aiohttp) → WebSocket → Browser
                                          ├── Canvas (particles, ripples, host glow)
                                          └── Web Audio API (oscillators, reverb)
```

## Quick Start

```bash
# Install dependencies
sudo apt-get install -y python3-aiohttp tcpdump dnsutils curl traceroute

# Run the server (requires root for tcpdump)
sudo python3 server.py

# Open http://localhost:3000 in your browser
# Click "Sound ON" to enable audio
```

## Traffic Generator

Generate test traffic to make the visualization more interesting:

```bash
# Run all patterns in a loop
sudo python3 traffic-gen.py auto

# Run a specific pattern
sudo python3 traffic-gen.py heartbeat   # Steady ICMP rhythm
sudo python3 traffic-gen.py storm       # All protocols at once
sudo python3 traffic-gen.py cascade     # ICMP → DNS → HTTP → TCP → UDP wave
sudo python3 traffic-gen.py pulse       # Quiet → burst → quiet → burst
sudo python3 traffic-gen.py exploration # Traceroute + port scan

# Run each pattern once as a demo
sudo python3 traffic-gen.py demo
```

## systemd Services

```bash
# Main service
sudo systemctl enable --now synesthesia.service

# Traffic generator (optional)
sudo systemctl enable --now traffic-gen.service
```

## Tech Stack

- **Backend**: Python 3, aiohttp, tcpdump
- **Frontend**: Vanilla JS, Canvas API, Web Audio API
- **No external JS dependencies**
