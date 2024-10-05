import socket

def scanner(ip, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    print(f"Scanning...")
    print(f"Port {port} is open!")


if __name__ == "__main__":
    ip = input("What IP Address do you want to scan?")
    #Only one port for now as I test
    port = int(input("Enter the port"))
    scanner(ip, port)


