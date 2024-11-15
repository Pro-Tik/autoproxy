import os
import glob
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from termcolor import colored
import time

# Delete existing proxy files
for file in glob.glob("proxies*.txt"):
    os.remove(file)
print("Old proxy files deleted.")

# List of proxy source URLs
urls = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
    "https://proxyscrape.com/free-proxy-list",
    "https://geonode.com/free-proxy-list",
    "https://free-proxy-list.net/",
    "https://advanced.name/freeproxy",
    "https://iproyal.com/free-proxy-list/?page=1",
    "https://spys.one/en/",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
]

# Request headers
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Test endpoint for proxy validation (httpbin.org)
TEST_URL = "https://httpbin.org/ip"

# Function to fetch proxies from different sources
def fetch_proxies(url):
    proxies = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            if "geonode.com" in url or "free-proxy-list.net" in url:
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table tbody tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        proxies.append(f"http://{cols[0].text.strip()}:{cols[1].text.strip()}")
            elif "spys.one" in url:
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("tr[onmouseover]")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 1:
                        ip_port = cols[0].text.strip().split(" ")[0]
                        proxies.append(f"http://{ip_port}")
            elif url.endswith(".txt"):
                proxies.extend([f"http://{line.strip()}" for line in response.text.splitlines() if line.strip()])
            elif "advanced.name" in url or "proxifly" in url:
                proxies.extend([f"http://{line.strip()}" for line in response.text.splitlines() if line.strip()])
    except Exception as e:
        print(colored(f"Failed to fetch proxies from {url}: {e}", "yellow"))
    return proxies

# Fetch proxies from all sources
proxies = []
for url in urls:
    proxies.extend(fetch_proxies(url))

print(f"Total proxies fetched: {len(proxies)}")

# Function to test a proxy with httpbin.org
def test_proxy(proxy):
    test_proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get(TEST_URL, proxies=test_proxies, timeout=5)
        if response.status_code == 200:
            print(colored(f"Working proxy: {proxy}", "green"))
            return proxy
    except requests.RequestException:
        pass
    print(colored(f"Bad proxy: {proxy}", "red"))
    return None

# Concurrently test proxies
working_proxies = []
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(test_proxy, proxies))
    working_proxies = [proxy for proxy in results if proxy]
end_time = time.time()

# Save working proxies to a file
with open("proxies.txt", "w") as file:
    file.writelines(f"{proxy}\n" for proxy in working_proxies)

print(f"Saved {len(working_proxies)} working proxies to proxies.txt")
print(f"Time taken: {end_time - start_time:.2f} seconds")
