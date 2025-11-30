import subprocess
from pathlib import Path
import time
import re

TOP500 = "top500_repos.txt"
ROOT = Path("D:/Morefixes/repos")
ROOT.mkdir(parents=True, exist_ok=True)

# ---- 清洗 Windows 不允许的路径字符 ----
def sanitize(name: str) -> str:
    name = name.strip()
    # 替换非法字符: < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # 去掉不可见字符，如 \r \n \t 等
    name = "".join(c for c in name if c.isprintable())
    return name


# ---- 运行命令（带 timeout） ----
def run(cmd, cwd=None, timeout=600):
    print(">>", cmd)
    try:
        result = subprocess.run(
            cmd, cwd=cwd, timeout=timeout, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] Git clone stalled, killed:", cmd)
        return False


if __name__ == "__main__":
    for line in open(TOP500, encoding="utf-8"):
        url = line.strip().rstrip("/").replace(".git", "")
        if not url:
            continue

        repo_name = sanitize(url.split("/")[-1])
        repo_dir = ROOT / repo_name

        # ---- 关键：自动跳过已 clone 的仓库 ----
        if repo_dir.exists():
            print(f"[SKIP] Already cloned → {repo_name}")
            continue

        print(f"\n[Clone] {repo_name} from {url}")

        cmd = f"git clone --depth 1 --filter=blob:none {url} {repo_dir}"

        # ---- 自动重试三次 ----
        success = False
        for attempt in range(3):
            print(f"    Attempt {attempt+1}/3")
            if run(cmd):
                success = True
                break
            time.sleep(3)

        if not success:
            print(f"[FAIL] Could not clone {repo_name} after 3 attempts.\n")
        else:
            print(f"[OK] Cloned {repo_name}\n")
