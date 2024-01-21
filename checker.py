import requests
import threading
from termcolor import colored
from datetime import datetime
import os, sys
from time import sleep
import time
import random
import requests
import glob
import zipfile
import io
import time
import shutil
import platform

def clear():
    os.system("cls") if os.name == "nt" else os.system("clear")

clear()
class ProxyInfo:
    def __init__(self, proxy):
        self.proxy = proxy
        self.location = None
        self.type = None
        self.response_time = None

    def determine_location(self):
        try:
            response = requests.get('https://ipinfo.io/json', proxies={"http": self.proxy, "https": self.proxy}, timeout=5)
            self.location = response.json().get("city", "Unknown")
            return True
        except:
            self.location = "Unknown"
            return False

    def determine_type(self):
        types = ["http", "https"]
        for t in types:
            try:
                response = requests.get("http://www.google.com", proxies={t: self.proxy}, timeout=5)
                if response.status_code == 200:
                    self.type = t.upper()
                    return
            except:
                pass
        self.type = "Unknown"

    def measure_response_time(self):
        try:
            response = requests.get("http://www.google.com", proxies={"http": self.proxy, "https": self.proxy}, timeout=5)
            self.response_time = response.elapsed.total_seconds()
        except:
            self.response_time = float('inf')

    def get_info(self):
        is_live = self.determine_location()
        if is_live:
            self.determine_type()
            self.measure_response_time()
        return is_live

def check_live_proxies(filename, num_threads):
    live_proxies = {"HTTP": [], "HTTPS": [], "Unknown": []}
    
    def check_proxy_thread(proxy):
        proxy_info = ProxyInfo(proxy)
        if proxy_info.get_info():
            live_proxies[proxy_info.type].append(proxy_info.proxy)
            print(colored(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {proxy} - Live | Location: {proxy_info.location} | Type: {proxy_info.type} | Response Time: {proxy_info.response_time}s", "green"))
        else:
            print(colored(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {proxy} - Die", "red"))

    with open(filename, "r") as file:
        proxies = file.readlines()
        threads = []

        for proxy in proxies:
            proxy = proxy.strip()
            thread = threading.Thread(target=check_proxy_thread, args=(proxy,))
            thread.start()
            threads.append(thread)

            if len(threads) >= num_threads:
                for thread in threads:
                    thread.join()
                threads = []

        for thread in threads:
            thread.join()

    with open("http.txt", "w") as file:
        for proxy in live_proxies["HTTP"]:
            file.write(proxy + "\n")
    
    with open("https.txt", "w") as file:
        for proxy in live_proxies["HTTPS"]:
            file.write(proxy + "\n")
    
    with open("live.txt", "w") as file:
        for t, proxies in live_proxies.items():
            for proxy in proxies:
                file.write(proxy + "\n")

    with open("live.txt", "r") as f:
        lines = f.read().splitlines()

    print("ALL is Done Total Proxy Live:", len(lines))
    print("Đã lưu vào file http.txt và file https.txt và file live.txt")
    print("Tool sẽ tự động dừng trong vài giây nữa! Cám ơn đã sử dụng tool chúng tôi!!")

def typing_effect(text, speed=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed + random.uniform(-0.02, 0.02))
    print()



if __name__ == "__main__":
    try:
        
        time.sleep(1.5)
        clear()
        typing_effect("Input proxyfile to check (Ex: proxy.txt): ")
        filename = input("> \033[0m")

        typing_effect("Threading To Check Proxies: ")
        num_threads = int(input("> \033[0m"))
        check_live_proxies(filename, num_threads)
    except KeyboardInterrupt:
        print("Đang dừng tool vui lòng chờ giây lát....")
        time.sleep(1)
        exit()
