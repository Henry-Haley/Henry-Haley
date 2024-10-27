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
    failed_resolves = []
    resolved_domain = []
    print_subdomains = []
    socket_success = []
    for subdomain in subdomains:
        full_domain = f"{subdomain}.{domain}"
        try:
            answers = dns.resolver.resolve(full_domain, "A")
            for answer in answers:
                print_subdomains.append(answer)

            ip_address = socket.gethostbyname(full_domain)
            print(f"Resolved {full_domain} to IP address: {ip_address}")
        except(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            failed_resolves.append(full_domain)
        except socket.gaierror:
            failed_resolves.append(full_domain)
    if socket_success:
        print("\nSuccessful Socket connection: ")
        for success in socket_success:
            print(f"\nSuccessful Socket Connections")
    if failed_resolves:
        print("\nSubdomains that failed to resolve:")
        for failed in failed_resolves:
            print(failed)
    else:
        print("All subdomains enumerated successfully")



def main():
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
