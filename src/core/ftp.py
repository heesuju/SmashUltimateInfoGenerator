import socket
import ipaddress
from ftplib import FTP
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

PORT = 5000
TIMEOUT = 0.5  # TCP connect timeout in seconds

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



    # ---------- Connection Check ----------
    @staticmethod
    def is_reachable(ip: str, port: int = PORT, timeout: float = 1.0) -> bool:
        """Lightweight TCP connect check."""
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

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

    # ---------- Smart Sync Analysis ----------
    
    def get_all_remote_files_recursive(self, remote_root: str) -> dict:
        """
        Recursively map all files in a remote directory.
        Returns dict: {rel_path: {'size': int, 'modify': str}}
        """
        all_files = {}
        
        # Helper to walk remote tree
        def _walk(current_remote, rel_prefix):
            try:
                items = list(self.ftp.mlsd(current_remote))
            except:
                return # Directory might not exist or verify failed
                
            for name, facts in items:
                if name in [".", ".."]:
                    continue
                    
                rel_path = f"{rel_prefix}/{name}" if rel_prefix else name
                
                if facts.get('type') == 'dir':
                    _walk(f"{current_remote}/{name}", rel_path)
                elif facts.get('type') == 'file':
                    all_files[rel_path] = {
                        'size': int(facts.get('size', 0)),
                        'modify': facts.get('modify', '')
                    }
        
        _walk(remote_root, "")
        return all_files

    def scan_mod_diff(self, local_path: str, remote_root: str) -> str:
        """
        Compare a local mod folder with its remote counterpart.
        Returns a status string: 'MATCH', 'REPLACE', 'METADATA_ONLY', 'MISSING'
        """
        mod_name = os.path.basename(local_path)
        remote_mod_dir = f"{remote_root}/{mod_name}"
        
        # Check if remote exists
        try:
            self.ftp.cwd(remote_mod_dir)
        except:
            return "MISSING" # New mod, needs full upload
            
        # Get flattened maps of files
        # Local
        local_files = {}
        for root, _, files in os.walk(local_path):
            rel_root = os.path.relpath(root, local_path).replace("\\", "/")
            if rel_root == ".": rel_root = ""
            
            for f in files:
                full_local = os.path.join(root, f)
                rel_path = f"{rel_root}/{f}" if rel_root else f
                local_files[rel_path] = {
                    'size': os.path.getsize(full_local),
                    'mtime': os.path.getmtime(full_local)
                }
                
        # Remote
        remote_files = self.get_all_remote_files_recursive(remote_mod_dir)
        
        # Compare
        all_keys = set(local_files.keys()) | set(remote_files.keys())
        diffs = []
        
        for key in all_keys:
            if key not in local_files:
                diffs.append(key) # Remote has extra file
            elif key not in remote_files:
                diffs.append(key) # Remote missing file
            else:
                # Compare size/time
                l = local_files[key]
                r = remote_files[key]
                
                # Size check
                if l['size'] != r['size']:
                    diffs.append(key)
                    continue
                    
                # Time check (allow 2s buffer)
                r_time = self.parse_ftp_time(r.get('modify', ''))
                if abs(l['mtime'] - r_time) > 2.0:
                     if l['mtime'] > r_time + 2.0:
                         diffs.append(key)
        
        if not diffs:
            return "MATCH"
            
        # Check if only metadata changed
        metadata_files = {"preview.webp", "info.toml"}
        is_only_metadata = True
        for d in diffs:
            if d not in metadata_files:
                is_only_metadata = False
                break
        
        if is_only_metadata:
            return "METADATA_ONLY"
            
        return "REPLACE"

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

    def sync_mod_folders(self, folders: list[str], progress_callback: Callable[[str], None] = None) -> tuple[int, int]:
        """
        Sync multiple mod folders to the Switch.
        Uploads to /ultimate/mods/ directory (ARCropolis).
        Returns (success_count, fail_count)
        """
        success = 0
        fail = 0
        for folder in folders:
            try:
                mod_name = os.path.basename(folder)
                remote_dir = f"/ultimate/mods/{mod_name}"
                
                if progress_callback:
                    progress_callback(f"Syncing folder: {mod_name}")
                
                self.sync_dir(folder, remote_dir, progress_callback)
                success += 1
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Failed to sync {folder}: {e}")
                fail += 1
        return success, fail
                
    
    def delete_remote_dir(self, remote_dir: str):
        """Recursively delete a remote directory"""
        # CRITICAL SAFETY CHECK
        path = remote_dir.strip()
        
        # 1. Scope Constraint: Must be inside /ultimate
        if not path.startswith("/ultimate"):
            print(f"SAFETY ERROR: Attempted to delete outside /ultimate: {path}")
            return

        # 2. Protected Paths
        protected = ["/", "/ultimate", "/ultimate/mods", "/ultimate/mods/", ""]
        if path in protected:
            print(f"SAFETY ERROR: Attempted to delete protected path: {path}")
            return
            
        try:
            # Get list of items
            items = []
            try:
                items = list(self.ftp.mlsd(remote_dir))
            except:
                # Fallback to nlst if mlsd fails or dir empty
                try:
                    names = self.ftp.nlst(remote_dir)
                    # Fake mlsd structure
                    items = [(n, {'type': 'unknown'}) for n in names]
                except:
                     return # Dir likely gone
             
            for name, facts in items:
                if name in [".", ".."]: continue
                
                full_path = f"{remote_dir}/{name}"
                is_dir = facts.get('type') == 'dir'
                
                if facts.get('type') == 'unknown':
                    try:
                        self.ftp.cwd(full_path)
                        is_dir = True
                        self.ftp.cwd("..")
                    except:
                        is_dir = False
                
                if is_dir:
                    self.delete_remote_dir(full_path)
                else:
                    try:
                        self.ftp.delete(full_path)
                    except: pass
             
            try:
                self.ftp.rmd(remote_dir)
            except: pass
        except:
            pass
    def find_acropolis_config_dir(self) -> str:
        """Find the first valid numeric-based config directory for ARCropolis."""
        # Try both spellings just to be safe, but prioritize acropolis
        base = "/ultimate/arcropolis/config"
        
        try:
            parent = os.path.dirname(base)
            base_name = os.path.basename(base)
            try:
                items = list(self.ftp.mlsd(parent))
            except:
                return None

            exists = False
            for name, facts in items:
                if name == base_name:
                    exists = True
                    break
            
            if not exists: return None

            # Look for first numeric dir
            items = list(self.ftp.mlsd(base))
            for name, facts in items:
                if facts.get('type') == 'dir' and name.isdigit():
                    # Go one level deeper
                    sub_path = f"{base}/{name}"
                    sub_items = list(self.ftp.mlsd(sub_path))
                    for sub_name, sub_facts in sub_items:
                        if sub_facts.get('type') == 'dir' and sub_name.isdigit():
                            return f"{sub_path}/{sub_name}"
        except:
            return None

    def sync_config_files(self, local_cache_dir: str, remote_config_dir: str, progress_callback: Callable[[str], None] = None):
        """Upload workspace, workspace_list and preset files to remote config dir."""
        files_to_sync = ["workspace", "workspace_list"]
        
        if not os.path.exists(local_cache_dir):
            return

        # Also find all preset files
        for f in os.listdir(local_cache_dir):
            if "_preset" in f or f == "presets":
                files_to_sync.append(f)
        
        try:
            self.ftp.cwd(remote_config_dir)
            for filename in files_to_sync:
                local_path = os.path.join(local_cache_dir, filename)
                if os.path.exists(local_path) and os.path.isfile(local_path):
                    if progress_callback:
                        progress_callback(f"Syncing config: {filename}")
                    self.upload_file_with_retry(local_path, filename)
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error syncing configs: {e}")
            raise e
