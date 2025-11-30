import csv
import subprocess
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

CSV_FILE = "fixes_score_65.csv"
TOPFILE = "top500_repos.txt"

REPO_ROOT = Path("D:/Morefixes/repos")
DIFF_ROOT = Path("D:/Morefixes/diffs")
DIFF_ROOT.mkdir(exist_ok=True, parents=True)

# ---- load top500 repo urls ----
TOP500 = set(
    line.strip().rstrip("/").replace(".git", "")
    for line in open(TOPFILE, encoding="utf-8")
    if line.strip()
)

# global lock to avoid printing collision
print_lock = threading.Lock()


def run(cmd, cwd=None, timeout=25):
    """Run a git command safely with timeout."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, timeout=timeout, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.TimeoutExpired:
        return False, "[TIMEOUT]"

    if result.returncode != 0:
        return False, result.stderr.decode(errors="ignore")
    return True, result.stdout.decode(errors="ignore")


def get_diff(repo_dir, commit):
    """Attempt git show, and auto-fetch if missing."""
    ok, out = run(f"git show {commit} --patch --no-color", cwd=repo_dir)
    if ok:
        return out

    # fetch missing commit
    run(f"git fetch origin {commit} --depth=1", cwd=repo_dir)

    # retry
    ok2, out2 = run(f"git show {commit} --patch --no-color", cwd=repo_dir)
    if ok2:
        return out2

    return ""


def worker(task):
    """Process one diff extraction job."""
    repo_name, repo_dir, commit = task
    out_path = DIFF_ROOT / f"{repo_name}_{commit}.diff"

    if out_path.exists():
        return f"[SKIP] {repo_name}_{commit}.diff"

    if not repo_dir.exists():
        return f"[MISS] Repo not found: {repo_name}"

    for attempt in range(3):
        diff = get_diff(repo_dir, commit)
        if diff:
            out_path.write_text(diff, encoding="utf-8")
            return f"[OK] {repo_name} {commit}"
        time.sleep(1)

    return f"[FAIL] {repo_name} {commit}"


if __name__ == "__main__":
    print("\n=== Building task list ===")

    tasks = []
    with open(CSV_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            url = row["repo_url"].strip().rstrip("/").replace(".git", "")
            commit = row["hash"].strip()

            if url not in TOP500:
                continue

            repo_name = url.split("/")[-1]
            repo_dir = REPO_ROOT / repo_name

            tasks.append((repo_name, repo_dir, commit))

    print(f"Total commits to process: {len(tasks)}")

    # pick a safe number of threads (I/O bound → 8–16 is ideal)
    MAX_THREADS = 12
    print(f"Using {MAX_THREADS} threads...\n")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(worker, t): t for t in tasks}

        for future in as_completed(futures):
            result = future.result()
            with print_lock:
                print(result)
