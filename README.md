# Network Synesthesia

**EN** | Real-time network traffic visualization and sonification. Packets become particles of light and musical notes.

**JP** | ネットワークトラフィックをリアルタイムで可視化・音響化するツール。パケットが光の粒子と音符に変わります。

## Demo

[![Demo Video](demo-thumbnail.jpg)](https://github.com/nnnnnnnnnke/network-synesthesia/blob/main/demo.mp4)

*Click the image to watch the demo video (with sound) / 画像をクリックしてデモ動画を再生（音声あり）*

## What it does / 機能

- **EN**: Captures live network packets via `tcpdump` and streams them to the browser via WebSocket
- **JP**: `tcpdump` でネットワークパケットをリアルタイムにキャプチャし、WebSocket でブラウザへ配信

Each protocol has a unique color and instrument / プロトコルごとに固有の色と楽器を割り当て:

| Protocol | Color | Sound | 色 | 音 |
|----------|-------|-------|-----|-----|
| HTTP/S | Blue | Sine wave pad | 青 | シンセパッド |
| DNS | Yellow | Bell / Chime | 黄 | ベル・チャイム |
| SSH | Green | Sawtooth bass | 緑 | ノコギリ波ベース |
| ICMP | Red | Percussion | 赤 | パーカッション |
| TCP | Purple | Sine | 紫 | サイン波 |
| UDP | Gray | Triangle | 灰 | 三角波 |

- Packets fly as glowing particles between source and destination hosts
- Pentatonic scale ensures everything sounds harmonious
- Built-in reverb for ambient atmosphere

---

- パケットは光る粒子として送信元と宛先ホスト間を飛行
- ペンタトニックスケールにより常に調和のとれたサウンドを実現
- リバーブ内蔵でアンビエントな雰囲気を演出

## Architecture / アーキテクチャ

```
tcpdump → Python (aiohttp) → WebSocket → Browser
                                          ├── Canvas (particles, ripples, host glow)
                                          └── Web Audio API (oscillators, reverb)
```

**EN**: The Python backend captures raw packets with `tcpdump`, parses protocol/address/size, and broadcasts JSON to all connected browsers via WebSocket. The frontend renders each packet as a glowing particle on Canvas and plays a musical note with the Web Audio API.

**JP**: Python バックエンドが `tcpdump` で生パケットをキャプチャし、プロトコル・アドレス・サイズを解析して WebSocket で接続中の全ブラウザへ JSON を配信します。フロントエンドでは各パケットを Canvas 上の光る粒子として描画し、Web Audio API で音符を再生します。

## Quick Start / クイックスタート

```bash
# Install dependencies / 依存パッケージをインストール
sudo apt-get install -y python3-aiohttp tcpdump dnsutils curl traceroute

# Run the server (requires root for tcpdump)
# サーバーを起動（tcpdump のため root 権限が必要）
sudo python3 server.py

# Open http://localhost:3000 in your browser
# ブラウザで http://localhost:3000 を開く
# Click "Sound ON" to enable audio
# 「Sound ON」をクリックして音声を有効化
```

## Traffic Generator / トラフィックジェネレーター

Generate test traffic to make the visualization more interesting.

テスト用トラフィックを生成して、より面白い可視化を体験できます。

```bash
# Run all patterns in a loop / 全パターンをループ実行
sudo python3 traffic-gen.py auto

# Run a specific pattern / 特定のパターンを実行
sudo python3 traffic-gen.py heartbeat   # Steady ICMP rhythm / 安定したICMPリズム
sudo python3 traffic-gen.py storm       # All protocols at once / 全プロトコル同時
sudo python3 traffic-gen.py cascade     # ICMP → DNS → HTTP → TCP → UDP wave / 順番に波
sudo python3 traffic-gen.py pulse       # Quiet → burst → quiet → burst / 静寂→爆発の繰り返し
sudo python3 traffic-gen.py exploration # Traceroute + port scan / 経路探索＋ポートスキャン

# Run each pattern once as a demo / 各パターンを1回ずつデモ実行
sudo python3 traffic-gen.py demo
```

## systemd Services / systemd サービス

```bash
# Main service / メインサービス
sudo systemctl enable --now synesthesia.service

# Traffic generator (optional) / トラフィックジェネレーター（オプション）
sudo systemctl enable --now traffic-gen.service
```

## Tech Stack / 技術スタック

- **Backend / バックエンド**: Python 3, aiohttp, tcpdump
- **Frontend / フロントエンド**: Vanilla JS, Canvas API, Web Audio API
- **No external JS dependencies / 外部JSライブラリ不要**
