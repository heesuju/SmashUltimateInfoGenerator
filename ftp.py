import socket
import ipaddress
from ftplib import FTP
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

PORT = 5000
TIMEOUT = 0.5  # TCP connect timeout in seconds
MAX_CONCURRENT_UPLOADS = 5  # adjust for Wi-Fi performance
FILE_COUNT_THRESHOLD = 50   # files
LARGE_FILE_MB = 50          # MB

class SwitchFTP:
    def __init__(self, port: int = PORT):
        self.port = port
        self.ftp = None

    # ---------- Subnet Detection ----------
    @staticmethod
    def get_local_subnet() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        network = ipaddress.IPv4Network(local_ip + "/24", strict=False)
        return str(network)

    # ---------- LAN Scan for Switch ----------
    def find_switch(self, subnet: str, progress_callback: Callable[[str], None] = None) -> str:
        def check_ip(ip):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            try:
                sock.connect((str(ip), self.port))
                sock.close()
                # Try FTP login
                try:
                    ftp = FTP()
                    ftp.connect(str(ip), self.port, timeout=TIMEOUT)
                    ftp.login()
                    ftp.quit()
                    return str(ip)
                except:
                    return None
            except:
                return None

        net = ipaddress.IPv4Network(subnet)
        found_ip = None
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check_ip, ip): ip for ip in net.hosts()}
            for future in as_completed(futures):
                ip = future.result()
                if ip:
                    found_ip = ip
                    break
        if not found_ip:
            raise RuntimeError("No Switch with ftpd found on the network.")
        if progress_callback:
            progress_callback(f"Found Switch at {found_ip}")
        return found_ip

    # ---------- FTP Connect / Disconnect ----------
    def connect(self, ip: str):
        self.ftp = FTP()
        self.ftp.connect(ip, self.port, timeout=5)
        self.ftp.login()

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp = None

    # ---------- TITLEID Detection ----------
    @staticmethod
    def detect_titleid(export_dir: str) -> str:
        for item in os.listdir(export_dir):
            path = os.path.join(export_dir, item)
            if os.path.isdir(path) and item.startswith("01") and len(item) == 16:
                return path
        raise RuntimeError("No TITLEID folder found in export directory.")

    # ---------- Transfer Mode Decision ----------
    @staticmethod
    def decide_transfer_mode(local_dir: str) -> str:
        total_files = 0
        max_file_size = 0
        for root, _, files in os.walk(local_dir):
            total_files += len(files)
            for f in files:
                path = os.path.join(root, f)
                max_file_size = max(max_file_size, os.path.getsize(path))
        max_file_mb = max_file_size / (1024*1024)
        if total_files > FILE_COUNT_THRESHOLD and max_file_mb < LARGE_FILE_MB:
            return "concurrent"
        else:
            return "sequential"

    # ---------- File Upload Helpers ----------
    def upload_file_with_retry(self, local_path: str, remote_path: str, retries: int = 3):
        for attempt in range(1, retries + 1):
            try:
                with open(local_path, "rb") as f:
                    self.ftp.storbinary(f"STOR " + remote_path, f)
                return
            except Exception as e:
                if attempt == retries:
                    raise e
                import time
                time.sleep(0.5) # Wait a bit before retry

    def upload_dir_sequential(self, local_dir: str, remote_dir: str, progress_callback: Callable[[str], None] = None):
        for root, dirs, files in os.walk(local_dir):
            rel_path = os.path.relpath(root, local_dir).replace("\\", "/")
            ftp_path = f"{remote_dir}/{rel_path}" if rel_path != "." else remote_dir
            try:
                self.ftp.mkd(ftp_path)
            except:
                pass
            self.ftp.cwd(ftp_path)
            for file in files:
                local_file = os.path.join(root, file)
                if progress_callback:
                    progress_callback(f"Uploading {local_file} -> {ftp_path}/{file}")
                self.upload_file_with_retry(local_file, file)

    def upload_dir_parallel(self, local_dir: str, remote_dir: str, progress_callback: Callable[[str], None] = None):
        tasks = []

        def _enqueue_upload(local_path, remote_path):
            for root, dirs, files in os.walk(local_path):
                rel_path = os.path.relpath(root, local_path).replace("\\", "/")
                ftp_path = f"{remote_path}/{rel_path}" if rel_path != "." else remote_path
                try:
                    self.ftp.mkd(ftp_path)
                except:
                    pass
                self.ftp.cwd(ftp_path)
                for file in files:
                    full_local = os.path.join(root, file)
                    tasks.append((full_local, file, ftp_path))

        _enqueue_upload(local_dir, remote_dir)

        def worker(args):
            local_file, remote_file, ftp_path = args
            self.upload_file_with_retry(local_file, remote_file)
            if progress_callback:
                progress_callback(f"Uploaded {local_file} -> {ftp_path}/{remote_file}")

        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_UPLOADS) as executor:
            futures = [executor.submit(worker, task) for task in tasks]
            for future in as_completed(futures):
                future.result()

    # ---------- Directory Helpers ----------
    def ensure_remote_dir(self, remote_path: str):
        """
        Recursively ensure a directory exists on the remote server.
        """
        if remote_path == "/" or remote_path == "":
            return

        parts = [p for p in remote_path.split("/") if p]
        
        # Start from root
        try:
            self.ftp.cwd("/")
        except Exception as e:
            print(f"DEBUG: Failed to CWD to root: {e}")

        current_build = ""
        for part in parts:
            current_build = f"{current_build}/{part}"
            try:
                self.ftp.cwd(part)
            except Exception as cwd_err:
                print(f"DEBUG: CWD to {part} failed ({cwd_err}), trying MKD...")
                try:
                    self.ftp.mkd(part)
                    print(f"DEBUG: MKD {part} success")
                    self.ftp.cwd(part)
                except Exception as mkd_err:
                    print(f"DEBUG: MKD {part} failed: {mkd_err}")
                    try:
                        self.ftp.cwd(current_build)
                    except Exception as full_cwd_err:
                        print(f"DEBUG: Full path CWD {current_build} also failed: {full_cwd_err}")
                        pass

    # ---------- Sync Logic ----------
    def get_remote_files(self, remote_dir: str) -> dict:
        """
        Get list of files in remote directory with metadata.
        Returns dict: {filename: {'size': int, 'modify': str}}
        """
        files = {}
        try:
            for name, facts in self.ftp.mlsd(remote_dir):
                if facts.get('type') == 'file':
                    files[name] = {
                        'size': int(facts.get('size', 0)),
                        'modify': facts.get('modify', '')
                    }
        except Exception:
            # Fallback to NLST or LIST if MLSD fails (less reliable for timestamps)
            pass
        return files

    def parse_ftp_time(self, time_str: str) -> float:
        """Parse FTP modify timestamp (YYYYMMDDHHMMSS) to epoch."""
        import datetime
        try:
            dt = datetime.datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
            return dt.timestamp()
        except:
            return 0.0

    def sync_dir(self, local_dir: str, remote_dir: str, progress_callback: Callable[[str], None] = None):
        """
        Sync directory: Upload files if missing or newer on local.
        """
        # Ensure base directory exists (recursive)
        self.ensure_remote_dir(remote_dir)
            
        # Get remote state
        remote_files = self.get_remote_files(remote_dir)
        
        for root, dirs, files in os.walk(local_dir):
            rel_path = os.path.relpath(root, local_dir).replace("\\", "/")
            
            target_dir = f"{remote_dir}/{rel_path}" if rel_path != "." else remote_dir
            
            if rel_path != ".":
                 self.ensure_remote_dir(target_dir)
            
            current_remote_files = {}
            if rel_path != ".":
                current_remote_files = self.get_remote_files(target_dir)
            else:
                current_remote_files = remote_files

            for file in files:
                local_file_path = os.path.join(root, file)
                
                should_push = False
                if file not in current_remote_files:
                    should_push = True
                    reason = "Missing"
                else:
                    remote_info = current_remote_files[file]
                    remote_mtime = self.parse_ftp_time(remote_info.get('modify', ''))
                    local_mtime = os.path.getmtime(local_file_path)
                    
                    if local_mtime > remote_mtime + 2: 
                        should_push = True
                        reason = f"Newer (L:{local_mtime} > R:{remote_mtime})"
                    else:
                        reason = "Up to date"
                
                if should_push:
                    if progress_callback:
                        progress_callback(f"Syncing {file} ({reason})")
                    
                    # 1. CD to the target directory
                    # 2. Upload file just by filename
                    try:
                        self.ftp.cwd(target_dir)
                        self.upload_file_with_retry(local_file_path, file)
                    except Exception as e:
                         if progress_callback:
                            progress_callback(f"Error uploading {file}: {e}")
                else:
                    if progress_callback:
                        progress_callback(f"Skipped {file} ({reason})")

    def sync_mod_folders(self, folders: list[str], progress_callback: Callable[[str], None] = None):
        """
        Sync multiple mod folders to the Switch.
        Uploads to /ultimate/mods/ directory (ARCropolis).
        """
        for folder in folders:
            mod_name = os.path.basename(folder)
            remote_dir = f"/ultimate/mods/{mod_name}"
            
            if progress_callback:
                progress_callback(f"Syncing {mod_name} -> {remote_dir}")
                
            self.sync_dir(folder, remote_dir, progress_callback)
