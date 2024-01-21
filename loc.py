import socket
import sys
import threading
from colorama import Fore, Style


banner ="""HUM"""

def test_http_proxy(proxy, live_proxies_file, timeout=5):
    try:
        proxy_parts = proxy.split(':')
        proxy_host = proxy_parts[0]
        proxy_port = int(proxy_parts[1])

        with socket.create_connection((proxy_host, proxy_port), timeout=timeout) as s:
            print(f"{Fore.GREEN}Live: HTTP Proxy {proxy}.{Style.RESET_ALL}")
            with open(live_proxies_file, 'a') as live_file:
                live_file.write(f"{proxy}\n")
    except Exception as e:
        print(f"{Fore.RED}Die: HTTP Proxy {proxy}.{Style.RESET_ALL}")

def test_socks5_proxy(proxy, live_proxies_file, timeout=5):
    try:
        proxy_parts = proxy.split(':')
        proxy_host = proxy_parts[0]
        proxy_port = int(proxy_parts[1])

        with socket.create_connection((proxy_host, proxy_port), timeout=timeout) as s:
            s.sendall(b'\x05\x01\x00')  
            response = s.recv(2)
            if response == b'\x05\x00':
                print(f"{Fore.GREEN}Live: SOCKS5 Proxy {proxy}.{Style.RESET_ALL}")
                with open(live_proxies_file, 'a') as live_file:
                    live_file.write(f"{proxy}\n")
            else:
                raise Exception("Invalid SOCKS5 response")
    except Exception as e:
        print(f"{Fore.RED}Die: SOCKS5 Proxy {proxy}.{Style.RESET_ALL}")

def test_socks4_proxy(proxy, live_proxies_file, timeout=5):
    try:
        proxy_parts = proxy.split(':')
        proxy_host = proxy_parts[0]
        proxy_port = int(proxy_parts[1])

        with socket.create_connection((proxy_host, proxy_port), timeout=timeout) as s:
            s.sendall(b'\x04\x01' + socket.inet_aton('0.0.0.1') + b'\x00')  # Gửi yêu cầu SOCKS4
            response = s.recv(8)
            if response.startswith(b'\x00\x5A'):
                print(f"{Fore.GREEN}Live: SOCKS4 Proxy {proxy}.{Style.RESET_ALL}")
                with open(live_proxies_file, 'a') as live_file:
                    live_file.write(f"{proxy}\n")
            else:
                raise Exception("Invalid SOCKS4 response")
    except Exception as e:
        print(f"{Fore.RED}Die: SOCKS4 Proxy {proxy}.{Style.RESET_ALL}")

def check_proxies_from_file(file_path, live_proxies_file, num_threads, timeout):
    try:
        with open(file_path, 'r') as file:
            proxy_list = file.read().splitlines()
            threads = []

            for proxy in proxy_list:
                http_thread = threading.Thread(target=test_http_proxy, args=(proxy, live_proxies_file, timeout))
                socks5_thread = threading.Thread(target=test_socks5_proxy, args=(proxy, live_proxies_file, timeout))
                socks4_thread = threading.Thread(target=test_socks4_proxy, args=(proxy, live_proxies_file, timeout))

                http_thread.start()
                socks5_thread.start()
                socks4_thread.start()

                threads.extend([http_thread, socks5_thread, socks4_thread])

                if len(threads) >= num_threads:
                    for thread in threads:
                        thread.join()
                    threads = []

            for thread in threads:
                thread.join()
    except FileNotFoundError:
        print(f"File not found: {file_path}")

if __name__ == "__main__":
    print(banner)
    file_path = input("Enter the path to the proxy file:\n=> ")
    live_proxies_file = input("Enter the path to the live proxies file:\n=> ")
    num_threads = int(input("Enter the number of threads: "))
    timeout = int(input("Enter the timeout for each proxy check (seconds):\n=> "))
    
    from colorama import init
    init()
    
    check_proxies_from_file(file_path, live_proxies_file, num_threads, timeout)

    input("Press Enter to exit.")
    sys.exit(0)
