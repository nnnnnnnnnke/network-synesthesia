#!/usr/bin/env python3
"""Network Synesthesia - Turn network traffic into music and visual art"""

import asyncio
import json
import logging
import re
import os
from aiohttp import web

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('synesthesia')

clients = set()

def parse_packet(line):
    """Parse tcpdump output into a packet dict.

    Handles Linux cooked v2 format (tcpdump -i any):
      1773819268.395803 eth0  Out IP 10.10.0.118.22 > 10.10.0.1.41194: tcp 76
      1773819268.395803 eth0  In  IP 10.10.0.1.53 > 10.10.0.118.53: UDP, length 45
      1773819268.395803 eth0  Out IP 10.10.0.118 > 10.10.0.1: ICMP echo request ...
    """
    line = line.strip()
    if not line:
        return None

    # Extract timestamp
    ts_m = re.match(r'(\d+\.\d+)\s', line)
    if not ts_m:
        return None
    ts = float(ts_m.group(1))

    # Strip interface/direction prefix: "eth0  Out " or "eth0  In  "
    # After timestamp, skip everything up to "IP " or "ARP"
    ip_pos = line.find(' IP ')
    arp_pos = line.find(' ARP')

    # ARP
    if arp_pos != -1 and (ip_pos == -1 or arp_pos < ip_pos):
        return {'ts': ts, 'proto': 'arp', 'src': '0.0.0.0', 'dst': '255.255.255.255', 'size': 42}

    if ip_pos == -1:
        return None

    # Get the part after "IP "
    rest = line[ip_pos + 4:]

    # ICMP: "10.10.0.118 > 10.10.0.1: ICMP echo request, ..."
    m = re.match(r'(\d+\.\d+\.\d+\.\d+) > (\d+\.\d+\.\d+\.\d+): ICMP', rest)
    if m:
        size_m = re.search(r'length (\d+)', rest)
        return {
            'ts': ts,
            'proto': 'icmp',
            'src': m.group(1),
            'dst': m.group(2),
            'size': int(size_m.group(1)) if size_m else 64,
        }

    # TCP/UDP: "10.10.0.118.22 > 10.10.0.1.41194: tcp 76"
    #      or: "10.10.0.118.22 > 10.10.0.1.41194: Flags [P.], ..."
    #      or: "10.10.0.1.53 > 10.10.0.118.12345: UDP, length 45"
    m = re.match(
        r'(\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+): (.*)', rest
    )
    if m:
        src_port = int(m.group(2))
        dst_port = int(m.group(4))
        tail = m.group(5)

        ports = {src_port, dst_port}
        if ports & {53}:
            proto = 'dns'
        elif ports & {22}:
            proto = 'ssh'
        elif ports & {80, 443, 8080, 3000}:
            proto = 'http'
        elif ports & {3306, 5432, 27017, 6379}:
            proto = 'db'
        elif tail.startswith('UDP') or tail.startswith('udp'):
            proto = 'udp'
        else:
            proto = 'tcp'

        # Size: "tcp 76", "UDP, length 45", "length 99"
        size = 64
        size_m = re.search(r'(?:tcp|udp)\s+(\d+)', tail, re.IGNORECASE)
        if size_m:
            size = int(size_m.group(1))
        else:
            size_m = re.search(r'length (\d+)', tail)
            if size_m:
                size = int(size_m.group(1))

        return {
            'ts': ts,
            'proto': proto,
            'src': m.group(1),
            'dst': m.group(3),
            'size': max(size, 1),
        }

    return None


async def packet_capture():
    """Capture packets using tcpdump and broadcast to WebSocket clients"""
    global clients
    log.info('Starting packet capture...')
    try:
        proc = await asyncio.create_subprocess_exec(
            'tcpdump', '-i', 'any', '-l', '-n', '-tt', '-s', '128',
            '--immediate-mode', '-q',
            'not', 'port', '3000',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        log.info(f'tcpdump started (pid={proc.pid})')

        pkt_count = 0
        sent_count = 0

        while True:
            line = await proc.stdout.readline()
            if not line:
                stderr_out = await proc.stderr.read()
                log.error(f'tcpdump exited. stderr: {stderr_out.decode(errors="ignore")}')
                break

            packet = parse_packet(line.decode('utf-8', errors='ignore'))
            pkt_count += 1

            if pkt_count <= 3:
                log.info(f'Packet #{pkt_count}: parsed={packet is not None}, clients={len(clients)}, raw={line.decode().strip()[:100]}')

            if pkt_count % 500 == 0:
                log.info(f'Stats: captured={pkt_count}, sent={sent_count}, clients={len(clients)}')

            if packet and clients:
                msg = json.dumps(packet)
                dead = set()
                for ws in clients.copy():
                    try:
                        await ws.send_str(msg)
                        sent_count += 1
                    except Exception as e:
                        log.warning(f'WebSocket send error: {e}')
                        dead.add(ws)
                clients -= dead
    except Exception as e:
        log.error(f'packet_capture crashed: {e}', exc_info=True)


async def traffic_generator():
    """Generate gentle background traffic for continuous visualization"""
    log.info('Traffic generator starting...')

    # Discover active VMs on the SDN
    targets = []
    for i in range(100, 120):
        ip = f'10.10.0.{i}'
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        if proc.returncode == 0 and ip != '10.10.0.118':
            targets.append(ip)

    log.info(f'Discovered {len(targets)} hosts: {targets}')

    domains = ['example.com', 'google.com', 'github.com', 'cloudflare.com',
               'python.org', 'kernel.org', 'ubuntu.com', 'mozilla.org']

    import random
    cycle = 0
    while True:
        cycle += 1

        # Ping 2-3 random VMs (not gateway)
        for t in random.sample(targets, min(3, len(targets))):
            sz = random.choice([56, 128, 256, 512])
            proc = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', '1', '-s', str(sz), t,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            await asyncio.sleep(1)

        # DNS lookup (1-2 random domains)
        for d in random.sample(domains, 2):
            qtype = random.choice(['A', 'AAAA', 'MX'])
            proc = await asyncio.create_subprocess_exec(
                'dig', '+short', '+time=2', '+tries=1', qtype, d,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            await asyncio.sleep(1.5)

        # HTTP probe (every 3rd cycle only)
        if cycle % 3 == 0:
            url = random.choice([
                'http://example.com', 'http://detectportal.firefox.com',
            ])
            proc = await asyncio.create_subprocess_exec(
                'curl', '-s', '-o', '/dev/null', '-m', '3', url,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()

        await asyncio.sleep(5)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    log.info(f'WebSocket client connected. Total clients: {len(clients)}')
    try:
        async for msg in ws:
            pass
    finally:
        clients.discard(ws)
        log.info(f'WebSocket client disconnected. Total clients: {len(clients)}')
    return ws


async def index_handler(request):
    return web.FileResponse(os.path.join(os.path.dirname(__file__), 'static', 'index.html'))


async def start_background_tasks(app):
    app['capture_task'] = asyncio.create_task(packet_capture())
    app['traffic_task'] = asyncio.create_task(traffic_generator())


async def cleanup_background_tasks(app):
    app['capture_task'].cancel()
    app['traffic_task'].cancel()


app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/', index_handler)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=3000)
