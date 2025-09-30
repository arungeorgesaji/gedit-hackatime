import os
import time
import subprocess
import tempfile
import re
from pathlib import Path
from gi.repository import Gedit, GObject, Gio

class HackaTimeUtils:
    @staticmethod
    def get_lines(document):
        if document:
            return document.get_n_lines()
        return 0

    @staticmethod
    def get_cursor_pos(document):
        if document and document.get_insert():
            iter_pos = document.get_iter_at_mark(document.get_insert())
            return iter_pos.get_offset()
        return 1

    @staticmethod
    def get_machine_id():
        try:
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
            
            elif os.uname().sysname == "Darwin":
                result = subprocess.run([
                    "ioreg", "-d2", "-c", "IOPlatformExpertDevice"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'IOPlatformUUID' in line:
                            match = re.search(r'"([^"]+)"', line)
                            if match:
                                return match.group(1)
            
            elif os.name == 'nt':
                result = subprocess.run([
                    "wmic", "csproduct", "get", "UUID", "/format:value"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('UUID='):
                            return line.split('=', 1)[1].strip()
        
        except Exception as e:
            print(f"Error getting machine ID: {e}")
        
        return "unknown"

    @staticmethod
    def get_time():
        return int(time.time())

    @staticmethod
    def get_category():
        return "coding"

    @staticmethod
    def get_entity(document):
        if document and document.get_file():
            location = document.get_file().get_location()
            if location:
                return location.get_basename()
        return "untitled"

    @staticmethod
    def get_language(document):
        lang_map = {
            "python": "python",
            "javascript": "javascript",
            "js": "javascript",
            "html": "html",
            "css": "css",
            "java": "java",
            "c++": "cpp",
            "c": "c",
            "go": "go",
            "ruby": "ruby",
            "php": "php",
            "swift": "swift",
            "typescript": "typescript",
            "markdown": "markdown",
            "bash": "bash",
            "sh": "bash",
            "json": "json",
            "yaml": "yaml",
            "toml": "toml",
            "ini": "ini",
            "xml": "xml",
            "csv": "csv",
            "tsv": "tsv",
            "text": "text"
        }
        
        if document and document.get_language():
            lang_id = document.get_language().get_id()
            return lang_map.get(lang_id, "unknown")
        
        return "unknown"

    @staticmethod
    def get_type():
        return HackaTimeUtils.get_category()

    @staticmethod
    def get_user_agent():
        return "gedit-hackatime/1.0"

    @staticmethod
    def get_editor():
        return "Gedit"

    @staticmethod
    @staticmethod
    def get_project(document):
        if not document or not document.get_file():
            return "unknown"
        
        location = document.get_file().get_location()
        if not location:
            return "unknown"
        
        file_path = location.get_path()
        current_dir = os.path.dirname(file_path)
        
        while current_dir and current_dir != os.path.dirname(current_dir):
            git_dir = os.path.join(current_dir, ".git")
            if os.path.exists(git_dir):
                return os.path.basename(current_dir)
            current_dir = os.path.dirname(current_dir)
        
        parent = location.get_parent()
        if parent:
            return parent.get_basename()
        
        return "unknown"

    @staticmethod
    def get_project_root_count(document):
        try:
            if document and document.get_file():
                location = document.get_file().get_location()
                if location:
                    file_path = location.get_path()
                    current_dir = os.path.dirname(file_path)
                    
                    result = subprocess.run(
                        ["git", "rev-parse", "--git-dir"],
                        cwd=current_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        result = subprocess.run(
                            ["git", "submodule", "status", "--quiet"],
                            cwd=current_dir,
                            capture_output=True,
                            text=True
                        )
                        submodule_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                        return 1 + submodule_count
        except Exception:
            pass
        
        return 1

    @staticmethod
    def get_is_write(document):
        return document and document.get_modified()

    @staticmethod
    def get_operating_system():
        import platform
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    @staticmethod
    def get_lineno(document):
        if document and document.get_insert():
            iter_pos = document.get_iter_at_mark(document.get_insert())
            return iter_pos.get_line() + 1  
        return 1

    @staticmethod
    def get_branch(document):
        default_branch = "main"
        
        try:
            if document and document.get_file():
                location = document.get_file().get_location()
                if location:
                    file_path = location.get_path()
                    current_dir = os.path.dirname(file_path)
                    
                    result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=current_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        branch = result.stdout.strip()
                        return branch if branch else default_branch
        except Exception:
            pass
        
        return default_branch

    @staticmethod
    def save_current_state(document):
        if not document or not document.get_file():
            return (0, 0)
        
        try:
            location = document.get_file().get_location()
            if not location:
                return (0, 0)
                
            file_path = location.get_path()
            filename = os.path.basename(file_path)
            
            cache_dir = Path.home() / "gedit-hackatime-cache"
            cache_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            save_filename = f"{timestamp}-{filename}"
            save_path = cache_dir / save_filename
            
            line_changes = HackaTimeUtils.get_line_changes(filename, str(cache_dir))
            
            start_iter = document.get_start_iter()
            end_iter = document.get_end_iter()
            content = document.get_text(start_iter, end_iter, False)
            
            with open(save_path, 'w') as f:
                f.write(content)
            
            print(f"Saved state to: {save_path}")
            
            HackaTimeUtils.clean_old_files(str(cache_dir), filename)
            
            return line_changes
            
        except Exception as e:
            print(f"Failed to save state: {e}")
            return (0, 0)

    @staticmethod
    def clean_old_files(cache_dir=None, current_filename=None):
        try:
            if cache_dir is None:
                cache_dir = str(Path.home() / "gedit-hackatime-cache")
            
            cache_path = Path(cache_dir)
            if not cache_path.exists():
                return
            
            current_time = time.time()
            all_files = list(cache_path.glob("*"))
            
            if current_filename:
                current_files = [f for f in all_files if f.name.endswith(f"-{current_filename}")]
                sorted_files = sorted(current_files, key=os.path.getmtime, reverse=True)
                
                if len(sorted_files) > 2:
                    for old_file in sorted_files[2:]:
                        old_file.unlink()
                        print(f"Deleted old version: {old_file.name}")
            
            for file_path in all_files:
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 86400:  
                        file_path.unlink()
                        print(f"Deleted old file: {file_path.name}")
                        
        except Exception as e:
            print(f"Error cleaning old files: {e}")

    @staticmethod
    def get_line_changes(filename=None, cache_dir=None):
        additions = 0
        deletions = 0
        
        try:
            if cache_dir is None:
                cache_dir = str(Path.home() / "gedit-hackatime-cache")
            
            cache_path = Path(cache_dir)
            if not cache_path.exists() or not filename:
                return (additions, deletions)
            
            files = list(cache_path.glob(f"*-{filename}"))
            sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
            
            print(f"Found {len(sorted_files)} cache files for {filename}")
            
            if len(sorted_files) >= 1:
                previous_file = sorted_files[0]
                
                with tempfile.NamedTemporaryFile(mode='w', suffix=f'-{filename}', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    result = subprocess.run(
                        ["diff", "-u", str(previous_file), temp_path],
                        capture_output=True,
                        text=True
                    )
                    
                    diff_output = result.stdout
                    print(f"Diff output length: {len(diff_output)} chars")
                    
                    for line in diff_output.split('\n'):
                        if line.startswith('+') and not line.startswith('++'):
                            additions += 1
                        elif line.startswith('-') and not line.startswith('--'):
                            deletions += 1
                    
                    print(f"Calculated changes: +{additions} -{deletions}")
                    
                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
        except Exception as e:
            print(f"Error calculating line changes: {e}")
        
        return (additions, deletions)

    @staticmethod
    def message(format_str, *args):
        print(format_str % args)
