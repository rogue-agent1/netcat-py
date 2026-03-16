#!/usr/bin/env python3
"""netcat - Simple netcat (nc) replacement in Python."""
import socket, argparse, sys, threading, select, os

def listen(host, port, execute=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    print(f"Listening on {host}:{port}...")
    conn, addr = s.accept()
    print(f"Connected from {addr[0]}:{addr[1]}")
    if execute:
        import subprocess
        out = subprocess.check_output(execute, shell=True, stderr=subprocess.STDOUT)
        conn.sendall(out)
        conn.close()
    else:
        relay(conn)
    s.close()

def connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    try:
        s.connect((host, port))
        print(f"Connected to {host}:{port}")
        s.settimeout(None)
        relay(s)
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

def relay(sock):
    def recv_loop():
        try:
            while True:
                data = sock.recv(4096)
                if not data: break
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
        except: pass
        os._exit(0)
    
    t = threading.Thread(target=recv_loop, daemon=True)
    t.start()
    try:
        while True:
            data = sys.stdin.buffer.read(4096)
            if not data: break
            sock.sendall(data)
    except (KeyboardInterrupt, BrokenPipeError): pass
    sock.close()

def scan(host, ports, timeout=1):
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                print(f"{port} open")
            s.close()
        except: pass

def main():
    p = argparse.ArgumentParser(description='Simple netcat replacement')
    p.add_argument('host', nargs='?', default='0.0.0.0')
    p.add_argument('port', nargs='?', type=int)
    p.add_argument('-l', '--listen', action='store_true', help='Listen mode')
    p.add_argument('-p', '--port-bind', type=int, help='Port (listen mode)')
    p.add_argument('-e', '--execute', help='Execute command on connect')
    p.add_argument('-z', '--scan', action='store_true', help='Port scan mode')
    p.add_argument('--range', help='Port range for scan (e.g. 1-1024)')
    args = p.parse_args()

    if args.scan:
        if args.range:
            a, b = map(int, args.range.split('-'))
            ports = range(a, b+1)
        elif args.port:
            ports = [args.port]
        else:
            ports = [21,22,23,25,53,80,110,143,443,993,995,3306,5432,8080]
        scan(args.host, ports)
    elif args.listen:
        port = args.port_bind or args.port or 4444
        listen(args.host, port, args.execute)
    else:
        if not args.port:
            print("Usage: netcat HOST PORT or netcat -l -p PORT"); sys.exit(1)
        connect(args.host, args.port)

if __name__ == '__main__':
    main()
