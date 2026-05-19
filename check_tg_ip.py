import socket, ssl

ip = '149.154.167.220'
try:
    sock = socket.create_connection((ip, 443), timeout=10)
    print(f'TCP connected to {ip}:443')

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    ssock = ctx.wrap_socket(sock, server_hostname='api.telegram.org')
    print(f'TLS: {ssock.version()}')

    cert = ssock.getpeercert()
    subj = cert.get("subject", [])
    alt = cert.get("subjectAltName", [])
    print(f'Subject: {subj}')
    print(f'SAN: {alt}')

    # Try Bot API request
    req = b'GET /bot123456:fake/test HTTP/1.0\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n'
    ssock.write(req)
    resp = ssock.read(4096)
    print(f'Response: {resp[:500]}')
    ssock.close()
except Exception as e:
    print(f'FAILED: {e}')
