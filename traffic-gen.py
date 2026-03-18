#!/usr/bin/env python3
"""Traffic Generator for Network Synesthesia - Generate diverse network patterns"""

import asyncio
import random
import socket
import sys


# === Traffic Patterns ===

async def icmp_burst(targets, count=10, interval=0.1):
    """Rapid ICMP ping burst"""
    for _ in range(count):
        t = random.choice(targets)
        sz = str(random.choice([56, 128, 512, 1024]))
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', '-s', sz, t,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        await asyncio.sleep(interval)


async def dns_storm(domains, count=15, interval=0.08):
    """Rapid DNS lookups"""
    for _ in range(count):
        d = random.choice(domains)
        qtype = random.choice(['A', 'AAAA', 'MX', 'TXT', 'NS'])
        proc = await asyncio.create_subprocess_exec(
            'dig', '+short', '+time=2', '+tries=1', qtype, d,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        await asyncio.sleep(interval)


async def http_wave(urls, count=8, interval=0.2):
    """HTTP request wave"""
    for _ in range(count):
        u = random.choice(urls)
        proc = await asyncio.create_subprocess_exec(
            'curl', '-s', '-o', '/dev/null', '-m', '3',
            '-H', 'User-Agent: NetworkSynesthesia/1.0', u,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        await asyncio.sleep(interval)


async def tcp_scan(target, ports, interval=0.05):
    """TCP connect scan - generates SYN/ACK/RST packets"""
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect_ex((target, port))
            s.close()
        except Exception:
            pass
        await asyncio.sleep(interval)


async def udp_scatter(targets, count=10, interval=0.1):
    """UDP packets to random high ports"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.3)
    for _ in range(count):
        t = random.choice(targets)
        port = random.randint(10000, 60000)
        payload = random.randbytes(random.choice([32, 64, 128, 256]))
        try:
            s.sendto(payload, (t, port))
        except Exception:
            pass
        await asyncio.sleep(interval)
    s.close()


async def traceroute_sim(target):
    """Traceroute - generates TTL-exceeded ICMP"""
    proc = await asyncio.create_subprocess_exec(
        'traceroute', '-n', '-m', '10', '-w', '1', target,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()


# === Named Patterns ===

async def pattern_heartbeat(targets):
    """Steady rhythmic pings like a heartbeat"""
    print('  [heartbeat] Steady ICMP rhythm')
    for _ in range(20):
        t = random.choice(targets)
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', t,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        await asyncio.sleep(0.5)


async def pattern_storm(targets, domains, urls):
    """Everything at once - chaotic burst"""
    print('  [storm] All protocols simultaneously!')
    await asyncio.gather(
        icmp_burst(targets, 15, 0.05),
        dns_storm(domains, 20, 0.05),
        http_wave(urls, 10, 0.15),
        udp_scatter(targets, 15, 0.05),
    )


async def pattern_cascade(targets, domains, urls):
    """Protocols fire one after another like a cascade"""
    print('  [cascade] ICMP -> DNS -> HTTP -> TCP -> UDP')
    await icmp_burst(targets, 8, 0.08)
    await asyncio.sleep(0.3)
    await dns_storm(domains, 10, 0.06)
    await asyncio.sleep(0.3)
    await http_wave(urls, 6, 0.15)
    await asyncio.sleep(0.3)
    ports = random.sample(range(1, 1024), 15)
    await tcp_scan(random.choice(targets), ports, 0.04)
    await asyncio.sleep(0.3)
    await udp_scatter(targets, 10, 0.06)


async def pattern_pulse(targets, domains):
    """Alternating quiet and loud moments"""
    print('  [pulse] Quiet... BURST... quiet... BURST...')
    for _ in range(4):
        await asyncio.sleep(1.5)
        await asyncio.gather(
            icmp_burst(targets, 8, 0.03),
            dns_storm(domains, 8, 0.03),
        )


async def pattern_exploration(targets):
    """Traceroute + port scan - discovery mode"""
    print('  [exploration] Traceroute + port scan')
    t = random.choice(targets)
    await traceroute_sim(t)
    ports = [22, 53, 80, 443, 3000, 3306, 5432, 8080, 8443, 9090]
    await tcp_scan(t, ports, 0.1)


# === Config ===

TARGETS = ['10.10.0.1', '10.10.0.100', '10.10.0.111']
DOMAINS = [
    'example.com', 'google.com', 'github.com', 'cloudflare.com',
    'amazon.com', 'wikipedia.org', 'python.org', 'kernel.org',
    'stackoverflow.com', 'reddit.com', 'ubuntu.com', 'mozilla.org',
]
URLS = [
    'http://example.com', 'http://detectportal.firefox.com',
    'http://www.google.com', 'http://httpbin.org/get',
]


async def discover():
    """Discover live hosts on the SDN"""
    live = list(TARGETS)
    for i in range(100, 130):
        ip = f'10.10.0.{i}'
        if ip in live:
            continue
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        if proc.returncode == 0:
            live.append(ip)
    return live


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    print('Network Synesthesia Traffic Generator')
    print(f'Mode: {mode}')
    print('Discovering live hosts...')
    targets = await discover()
    print(f'Live hosts: {targets}')
    print()

    patterns = {
        'heartbeat': lambda: pattern_heartbeat(targets),
        'storm': lambda: pattern_storm(targets, DOMAINS, URLS),
        'cascade': lambda: pattern_cascade(targets, DOMAINS, URLS),
        'pulse': lambda: pattern_pulse(targets, DOMAINS),
        'exploration': lambda: pattern_exploration(targets),
    }

    if mode == 'auto':
        print('Running all patterns in rotation (Ctrl+C to stop)')
        while True:
            for name, fn in patterns.items():
                print(f'\n--- Pattern: {name} ---')
                await fn()
                await asyncio.sleep(2)
    elif mode == 'demo':
        print('Running each pattern once as demo')
        for name, fn in patterns.items():
            print(f'\n--- Pattern: {name} ---')
            await fn()
            await asyncio.sleep(1)
        print('\nDemo complete!')
    elif mode in patterns:
        print(f'Running pattern: {mode}')
        await patterns[mode]()
    else:
        names = ', '.join(patterns.keys())
        print(f'Available modes: auto, demo, {names}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nStopped.')
