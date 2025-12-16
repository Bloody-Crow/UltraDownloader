import os
import yt_dlp
import shutil
import sys
import time
import urllib.request
import socket

# === VARIABLES ===
FIXED_TOTAL_SIZE = 0
stats_tracker = None

class SmoothStats:
    def __init__(self):
        self.speed_history = []
        self.window_size = 15
    def get_smooth_speed(self, current_speed):
        if not current_speed: return 0
        self.speed_history.append(current_speed)
        if len(self.speed_history) > self.window_size:
            self.speed_history.pop(0)
        return sum(self.speed_history) / len(self.speed_history)

class QuietLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg):
        if "n challenge" in msg: return
    def error(self, msg):
        print(f"\nERROR: {msg}")

# === UI HELPERS ===
def print_centered(text):
    cols = shutil.get_terminal_size().columns
    print(text.center(cols))

def format_size(bytes_val):
    if not bytes_val or bytes_val <= 0: return "Unknown"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

def format_time(seconds):
    if seconds is None or seconds < 0: return "00:00"
    try:
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0: return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
    except: return "00:00"

# === PROXY ===
def find_best_proxy():
    print_centered("🕵️  Scanning for Proxies...")
    sys_proxies = urllib.request.getproxies()
    if 'http' in sys_proxies:
        p = sys_proxies['http']
        print_centered(f"✅ Found System Proxy: {p}")
        return p
    if 'https' in sys_proxies:
        p = sys_proxies['https']
        print_centered(f"✅ Found System Proxy: {p}")
        return p

    common_ports = [1080, 10808, 10809, 7890, 7891, 2080, 2081, 9050]
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            proxy_url = f"http://127.0.0.1:{port}"
            print_centered(f"✅ Found Active Local Proxy: {proxy_url}")
            return proxy_url
    print_centered("❌ No Proxy Found (Direct Connection)")
    return None

# === PROGRESS BAR ===
def progress_hook(d):
    global stats_tracker
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            
            if FIXED_TOTAL_SIZE > 0:
                total = FIXED_TOTAL_SIZE
            
            if total:
                percent = downloaded / total * 100
                if percent > 100: percent = 100
                
                raw_speed = d.get('speed')
                avg_speed = stats_tracker.get_smooth_speed(raw_speed)
                
                if avg_speed > 0:
                    eta_seconds = (total - downloaded) / avg_speed
                else:
                    eta_seconds = 0
                
                bar_len = 25
                filled = int(bar_len * percent // 100)
                bar = '█' * filled + '-' * (bar_len - filled)
                
                size_str = f"{format_size(downloaded):>9} / {format_size(total):<9}"
                speed_str = f"{format_size(avg_speed):>9}/s"
                eta_str = f"ETA: {format_time(eta_seconds)}"
                
                info = f"[{bar}] {percent:5.1f}% | {size_str} | {speed_str} | {eta_str}"
                
                cols = shutil.get_terminal_size().columns
                pad = max(0, (cols - len(info)) // 2)
                sys.stdout.write('\r' + ' ' * cols + '\r') 
                sys.stdout.write(' ' * pad + info)
                sys.stdout.flush()
        except Exception:
            pass
    elif d['status'] == 'finished':
        pass 

# === LOGIC ===
def calculate_size_math(tbr, duration):
    if not tbr or not duration: return 0
    return (tbr * 1000 * duration) / 8

def get_video_options(info):
    formats = info.get('formats', [])
    duration = info.get('duration')
    uniques = {}

    for f in formats:
        h = f.get('height')
        # Skip generic none streams, but KEEP audio-only if that's all there is? 
        # For now we stick to Video logic to keep it simple.
        if not h or f.get('vcodec') == 'none': continue
        
        size = f.get('filesize') or f.get('filesize_approx')
        tbr = f.get('tbr')
        if (not size) and tbr and duration:
            size = calculate_size_math(tbr, duration)
            
        if h not in uniques:
            uniques[h] = {'res': h, 'size': size}
        else:
            current = uniques[h]
            new_has_size = size is not None and size > 0
            curr_has_size = current['size'] is not None and current['size'] > 0
            
            if new_has_size and not curr_has_size:
                uniques[h] = {'res': h, 'size': size}
            elif new_has_size and curr_has_size and size > current['size']:
                uniques[h] = {'res': h, 'size': size}
    
    # Fallback for sites like Twitch/Twitter/Soundcloud if resolution data is missing
    if not uniques and formats:
        return [{'res': 'Best', 'size': 0}]

    return sorted(list(uniques.values()), key=lambda x: x['res'] if isinstance(x['res'], int) else 0, reverse=True)

def main():
    global FIXED_TOTAL_SIZE, stats_tracker
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    os.system('clear')
    print("\n" * 2)
    print_centered("--- ULTRA DOWNLOADER v1.0 (Universal) ---")
    
    proxy_url = find_best_proxy()
    
    print("\n" * 1)
    print_centered("Choose Browser for Login (Bypasses Age/Login Walls):")
    print_centered("[1] Firefox   [2] Chrome   [3] Chromium   [4] Brave")
    
    cols = shutil.get_terminal_size().columns
    raw_choice = input(f"{' ' * ((cols//2)-4)}: ").strip()
    b_map = {'1': 'firefox', '2': 'chrome', '3': 'chromium', '4': 'brave'}
    browser = b_map.get(raw_choice, 'firefox')

    while True:
        stats_tracker = SmoothStats() 
        FIXED_TOTAL_SIZE = 0
        
        os.system('clear')
        print("\n" * 2)
        print_centered("--- PASTE ANY VIDEO LINK ---")
        print_centered("(YouTube, Insta, TikTok, Twitter, Twitch, Reddit, Vimeo, etc)")
        if proxy_url: print_centered(f"(Proxy Active: {proxy_url})")
        print("\n")

        try:
            link = input("Paste Link Here > ").strip()
            if not link: continue
            
            print("\n")
            print_centered("🔍  Analyzing metadata...")

            ydl_opts_base = {
                'cookiesfrombrowser': (browser,),
                'quiet': True,
                'no_warnings': True,
                'logger': QuietLogger(),
            }
            if proxy_url: ydl_opts_base['proxy'] = proxy_url

            try:
                with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
                    info = ydl.extract_info(link, download=False)
                    title = info.get('title', 'Unknown Video')
            except Exception as e:
                print_centered(f"Link Error: {e}")
                input("Press Enter...")
                continue

            options = get_video_options(info)
            if not options:
                print_centered("No compatible streams found.")
                time.sleep(2)
                continue

            # === AUTO-SELECT LOGIC ===
            if len(options) == 1:
                target = options[0]
                print("\n")
                print_centered(f"🎬  {title}")
                print_centered(f"🚀  Single/Best quality found. Auto-starting...")
            else:
                print("\n")
                print_centered(f"🎬  {title}")
                print_centered("-" * 60) 
                
                for i, opt in enumerate(options):
                    idx = f"[{i+1}]"
                    res = f"{opt['res']}p" if isinstance(opt['res'], int) else opt['res']
                    sz = f"~{format_size(opt['size'])}"
                    line = f"{idx:>4} | {res:<10} | Size: {sz:>12}"
                    print_centered(line)
                    
                print_centered("-" * 60)

                print("\n")
                sel = input("Select Quality > ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(options):
                    target = options[0]
                else:
                    target = options[int(sel)-1]

            FIXED_TOTAL_SIZE = target['size']

            # DOWNLOAD
            print("\n")
            # Handle display text for non-integer resolutions
            res_display = f"{target['res']}p" if isinstance(target['res'], int) else target['res']
            print_centered(f"⬇️   Downloading ({res_display})...")
            
            # Format Logic
            if target['res'] == 'Best':
                fmt = 'bestvideo+bestaudio/best'
                # Clean filename for generic sites
                out_tmpl = os.path.join(desktop_path, '%(title)s.%(ext)s')
            else:
                fmt = f'bestvideo[height={target["res"]}]+bestaudio/best[height={target["res"]}]/best'
                # Detailed filename for sites with resolution options
                out_tmpl = os.path.join(desktop_path, '%(title)s_%(height)sp.%(ext)s')
            
            dl_opts = ydl_opts_base.copy()
            dl_opts.update({
                'outtmpl': out_tmpl,
                'format': fmt,
                'progress_hooks': [progress_hook],
                'noprogress': True
            })

            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.download([link])
            
            print("\n\n")
            print_centered("✅  DONE! Saved to Desktop.")
            print("\n")
            
            input("Press Enter to download another...")

        except KeyboardInterrupt:
            print("\n\n")
            print_centered("Thanks For Trying Me! Do It Again If you Will.")
            print("\n")
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter...")

if __name__ == "__main__":
    main()
