import socket
import threading
import requests
import platform
import re
import subprocess
import urllib3
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_PORTS = [80, 443, 554, 8000, 8001, 8080, 8443, 8888, 37777, 5000]
COMMON_PATHS = [
    "/", "/admin", "/login", "/viewer", "/webadmin", "/video", "/stream", "/live",
    "/snapshot", "/onvif-http/snapshot", "/system.ini", "/config", "/setup",
    "/cgi-bin/", "/api/", "/camera", "/img/main.cgi"
]
HTTPS_PORTS = [443, 8443, 8444]
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
TIMEOUT = 5
PORT_SCAN_TIMEOUT = 1.5

def print_banner():
    cctv_ascii = f'''
{Fore.RED}  ______!fsc!_....-' .g8888888p. '-------....._
.'          //     .g8:       :8p..---....___ \\'.
| Unnamed  //  ()  d88:       :88b|==========! !|
|         //       888:       :888|==========| !|
|___      \\_______'T88888888888P''----------'//|   
|   \\       {Fore.YELLOW}""""""""""""""""""""/ |{Fore.RED}
|    !...._____      .="""=.   .[]    ____...!  |   
|   /               ! .g$p. !   .[]          :  |   
|  !               :  $$$$$  :  .[]          :  |   
|  !                ! 'T$P' !   .[]           '.|   
|   \\__              "=._.="   .()        __    |   
|.--'  '----._______________________.----'  '--.|
'._____________________________________________.{Style.RESET_ALL}'

      {Fore.CYAN}InSecCam - CCTV Scanner{Style.RESET_ALL}
    '''
    print(cctv_ascii)

def get_default_gateway():
    try:
        import netifaces
        gws = netifaces.gateways()
        default_gw = gws.get('default')
        if default_gw and netifaces.AF_INET in default_gw:
            return default_gw[netifaces.AF_INET][0]
    except ImportError:
        print(f"{Fore.YELLOW}[!] netifaces not installed. For more robust gateway detection, run: pip install netifaces{Style.RESET_ALL}")
    except Exception as e:
        print(f"[!] Error detecting default gateway with netifaces: {e}")
    system = platform.system().lower()
    try:
        if system == "windows":
            output = subprocess.run("ipconfig", capture_output=True, text=True).stdout
            gateways = re.findall(r"Default Gateway[ .:]*([\d\.]+)", output)
            for gw in gateways:
                if gw and gw != "0.0.0.0":
                    return gw
        else:
            output = subprocess.run("ip route", capture_output=True, text=True).stdout
            match = re.search(r"default via ([\d\.]+)", output)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"[!] Error detecting default gateway: {e}")
    return None

def get_protocol(port):
    return "https" if port in HTTPS_PORTS else "http"

def scan_ports(ip):
    print(f"{Fore.YELLOW}[🔍] Scanning common CCTV ports on IP: {ip}{Style.RESET_ALL}")
    open_ports = []
    lock = threading.Lock()

    def scan_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(PORT_SCAN_TIMEOUT)
            try:
                if sock.connect_ex((ip, port)) == 0:
                    with lock:
                        open_ports.append(port)
                        print(f"  {Fore.GREEN}✅ Port {port} OPEN{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.RED}❌ Port {port} closed{Style.RESET_ALL}")
            except:
                pass

    threads = []
    for port in COMMON_PORTS:
        t = threading.Thread(target=scan_port, args=(port,))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return sorted(open_ports)

def analyze_port(ip, port):
    protocol = get_protocol(port)
    base_url = f"{protocol}://{ip}:{port}"
    print(f"{Fore.YELLOW}[🔎] Analyzing port {port} ({protocol.upper()}){Style.RESET_ALL}")

    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        server = resp.headers.get('Server', 'N/A')
        content_type = resp.headers.get('Content-Type', 'N/A')
        status = resp.status_code

        print(f"  Status Code: {status}")
        print(f"  Server: {server}")
        print(f"  Content-Type: {content_type}")

        text = resp.text.lower()

        keywords = ['camera', 'hikvision', 'dahua', 'axis', 'surveillance', 'webcam', 'nvr', 'dvr']
        found_keywords = [k for k in keywords if k in text]
        if found_keywords:
            print(f"  🔥 CCTV Keywords found in page: {', '.join(found_keywords)}")

        for path in COMMON_PATHS:
            url = f"{base_url}{path}"
            try:
                head = requests.head(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
                if head.status_code in [200, 401, 403]:
                    print(f"  {Fore.CYAN}🔗 Found camera endpoint: {url} (HTTP {head.status_code}){Style.RESET_ALL}")
            except:
                continue

        if status == 401:
            auth = resp.headers.get('WWW-Authenticate', 'N/A')
            print(f"  🔐 Authentication required: {auth}")

    except requests.RequestException as e:
        print(f"  ❌ Request error: {e}")

def check_login_pages(ip, open_ports):
    print(f"{Fore.YELLOW}[🔍] Checking for login/auth pages on {ip}{Style.RESET_ALL}")

    def check_path(port, path):
        protocol = get_protocol(port)
        url = f"{protocol}://{ip}:{port}{path}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            if r.status_code in [200, 401, 403]:
                print(f"  {Fore.MAGENTA}🔑 Login page found: {url} (HTTP {r.status_code}){Style.RESET_ALL}")
                return True
        except:
            return False
        return False

    found_any = False
    for port in open_ports:
        for path in COMMON_PATHS:
            if check_path(port, path):
                found_any = True
    if not found_any:
        print(f"  {Fore.RED}❌ No login pages detected{Style.RESET_ALL}")

def main():
    print_banner()

    print("=== InSecCam CCTV Scanner ===")

    gw_ip = get_default_gateway()
    if not gw_ip:
        print("[!] Could not detect default gateway IP. You can manually specify target IP in the code.")
        return

    print(f"[*] Default gateway IP detected: {gw_ip}")

    open_ports = scan_ports(gw_ip)
    if not open_ports:
        print("[!] No open CCTV-related ports found on gateway.")
        return

    for port in open_ports:
        analyze_port(gw_ip, port)

    check_login_pages(gw_ip, open_ports)

if __name__ == "__main__":
    main()
