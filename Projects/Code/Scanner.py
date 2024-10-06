import socket

def scanner(ip, start_port, end_port):
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is open")
        else:
            print(f"Port {port} is closed")
        s.close()


if __name__ == "__main__":
    ip = input("What IP Address do you want to scan?\n")
    start_port = int(input("Enter your starting port\n"))
    end_port = int(input("Enter your last port you wish to scan\n"))
    scanner(ip, start_port, end_port)


