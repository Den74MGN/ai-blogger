import socket
import ssl
import sys

HOST = "api.telegram.org"
PORT = 443

def test_proxy(proxy_type, proxy_addr, proxy_port):
    """Test a proxy connection to api.telegram.org"""
    try:
        import socks
        s = socks.socksocket()
        if proxy_type == "socks5":
            s.set_proxy(socks.SOCKS5, proxy_addr, proxy_port)
        elif proxy_type == "socks4":
            s.set_proxy(socks.SOCKS4, proxy_addr, proxy_port)
        elif proxy_type == "http":
            s.set_proxy(socks.HTTP, proxy_addr, proxy_port)
        else:
            return "UNKNOWN TYPE"
        
        s.settimeout(10)
        s.connect((HOST, PORT))
        ctx = ssl.create_default_context()
        ssock = ctx.wrap_socket(s, server_hostname=HOST)
        ssock.write(b"GET /bot123456:fake/test HTTP/1.0\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n")
        resp = ssock.read(1024)
        ssock.close()
        return f"OK: {resp[:50]}"
    except ImportError:
        return "pysocks NOT INSTALLED"
    except Exception as e:
        return f"FAIL: {e}"

def test_direct():
    try:
        sock = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ssock = ctx.wrap_socket(sock, server_hostname=HOST)
        ssock.write(b"GET /bot123456:fake/test HTTP/1.0\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n")
        resp = ssock.read(1024)
        ssock.close()
        return f"OK: {resp[:50]}"
    except Exception as e:
        return f"FAIL: {e}"

print("=" * 60)
print("Telegram Bot API Proxy Test")
print("=" * 60)
print()

print(f"[1] Direct connection: {test_direct()}")
print()

# Test proxies
proxies = [
    # ("socks5", "127.0.0.1", 1443),  # tg-ws-proxy (MTProto, won't work)
]

for i, (ptype, addr, port) in enumerate(proxies, 2):
    print(f"[{i}] {ptype.upper()} {addr}:{port}: {test_proxy(ptype, addr, port)}")

print()
print("=" * 60)
print("If all fail, recommend:")
print("  1. Cloudflare WARP (socks5://127.0.0.1:40000)")
print("  2. Tor (socks5://127.0.0.1:9050)")
print("  3. Psiphon (socks5://127.0.0.1:1080)")
print("=" * 60)

sys.exit(0)
