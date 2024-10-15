import socket

def scanner(ip, start_port, end_port):
    '''
    Scans a range of user-supplied ports on a Specified IP Address

    Parameters:
        ip(str) : The IP address to scan
        start_port (int): First port to scan
        end_port (int): Last port to scan
    '''
    count = 0
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates IPv4 Socket
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is open")
        else:
            count += 1
        s.close()
    print("There are ", count -1 ," closed ports")

# Menu function. Allows multiple inputs, like Enter for common ports. Planning as functionality grows to add a "man" page here

def display_menu(ip):
    '''
    Menu Function.

    Parameters:
        ip (str): The IP Address to scan
    '''
    port = input("Type your starting port, or hit Enter to scan common ports\n").strip()
    if port == "":
        start_port = 0
        end_port = 1024
    else:
        try:
            start_port = int(port)
            end_port = int(input("Enter your end port\n"))
        except ValueError:
            print("Invalid input. Please enter numeric port values.")
            return # Exits function if port number is invalid

    # Calls teh scanner function
    scanner(ip, start_port, end_port)

def main():
    '''
    Main function
    '''
    ip = input("What IP Address do you wish to scan?\n")
    while True:
        display_menu(ip)
        again = input("Press 'Y' to scan again, or anything else to exit\n") #allows breaking of Loop
        if again != "y":
            print("GTFO!")
            break

if __name__ == "__main__":
    main()
