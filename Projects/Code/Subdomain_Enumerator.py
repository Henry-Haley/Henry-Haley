'''
Subdomain Enumerator. Plan to expand functionality to allow file inputs and eventually trying SQL Injection, etc. 
'''

import socket
import dns.resolver
subdomains = [
    "www",
    "mail",
    "ftp",
    "admin",
    "api",
    "dev",
    "test",
    "staging",
    "beta",
    "portal",
    "blog",
    "webmail",
    "secure",
    "support",
    "dashboard",
    "help",
    "shop",
    "news",
    "cms",
    "static"
]

def enumerate_subdomains(domain):
    '''
    Enumerate subdomains for a given domain by attempting both dns.resolver and socket connections.

    Parameters:
    domain (str): The target domain

    Variables:
    failed_resolves - A list that appends whenever a resolve fails
    print_subdomains - Prints subdomains once scanning is over
    socket_success - Prints if a socket connection was made successfully

    Process:
    1. For each subdomain in the list, append it tot he domain
    2. Try to resolve the full domain using dns.resolver and socket
    3. If resolved, store in the respective success lists; if not, in the failed list
    4. At the end, print both successes and failures    
    '''
    failed_resolves = []
    print_subdomains = []
    socket_success = []
    for subdomain in subdomains:
        full_domain = f"{subdomain}.{domain}"
        try:
            answers = dns.resolver.resolve(full_domain, "A")
            for answer in answers:
                print_subdomains.append(answer)

            ip_address = socket.gethostbyname(full_domain) # prints dns.resolver connections as they happen
            print(f"Resolved {full_domain} to IP address: {ip_address}")
        except(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            failed_resolves.append(full_domain)
        except socket.gaierror:
            failed_resolves.append(full_domain)
    if socket_success: # Prints socket successes once scanning is over
        print("\nSuccessful Socket connection: ")
        for success in socket_success:
            print(f"\nSuccessful Socket Connections")
    if failed_resolves: # Prints list of failed connections at the end
        print("\nSubdomains that failed to resolve:")
        for failed in failed_resolves:
            print(failed)
    else:
        print("All subdomains enumerated successfully")



def main():
    '''
    Main function to control the flow of a program:
    - Presents the user with a menu and an inpur option
    - Calls the enumerate_subdomains if they press enter
    - Adding a functionality for file input
    '''
    while True:
        try:
            choice = input("Press Enter to use a list, or type 'f' to input a file: ")
            if choice == "":
                    domain = input("Enter the domain for enumeration.")
                    enumerate_subdomains(domain)
            elif choice == "f":
                print("Not yet implemented")
            else:
                print("Please type a valid input")
        except Exception as e:
            print(f"An error occured: {e}")

if __name__ == "__main__":
    main()
