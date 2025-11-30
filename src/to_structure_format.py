import os
import json
from pathlib import Path

# 根据你的实际路径改，这里假设脚本在 D:/Morefixes 下面
DIFF_DIR = Path("D:/Morefixes/diffs")
OUT_FILE = "all_diffs_new.jsonl"   # 一行一个 JSON，更安全

MAX_SIZE = 2 * 1024 * 1024  # 超过 2MB 的 diff 就先跳过（可以再调）


def parse_diff(diff_text):
    """
    把 diff 解析成结构化格式：
    [
        {
            "file": "path/to/file",
            "changes": [
                {
                    "type": "add" / "delete" / "context",
                    "line": "... content ..."
                }
            ]
        },
        ...
    ]
    """
    results = []
    current_file = None
    current_changes = []

    for line in diff_text.splitlines():
        # 新文件块
        if line.startswith("diff --git"):
            if current_file:
                results.append({
                    "file": current_file,
                    "changes": current_changes
                })
            parts = line.split()
            if len(parts) >= 4:
                current_file = parts[3].replace("b/", "")
            else:
                current_file = None
            current_changes = []
            continue

        # 跳过 hunk 信息
        if line.startswith("@@"):
            continue

        # 具体行
        if line.startswith("+") and not line.startswith("+++"):
            current_changes.append({"type": "add", "line": line[1:].rstrip()})
        elif line.startswith("-") and not line.startswith("---"):
            current_changes.append({"type": "delete", "line": line[1:].rstrip()})
        else:
            # 其他全部当成上下文，包括空行 / index / --- / +++
            current_changes.append({"type": "context", "line": line.rstrip()})

    if current_file:
        results.append({
            "file": current_file,
            "changes": current_changes
        })

    return results


if __name__ == "__main__":
    print(f"Reading diffs from: {DIFF_DIR}")
    diff_files = sorted(DIFF_DIR.glob("*.diff"))
    print(f"Total diff files: {len(diff_files)}")

    with open(OUT_FILE, "w", encoding="utf-8") as out_f:
        for diff_file in diff_files:
            # 1) 跳过特别大的 diff（比如 linux 巨补丁）
            size = diff_file.stat().st_size
            if size > MAX_SIZE:
                print(f"[SKIP-BIG] {diff_file.name} ({size/1024:.1f} KB)")
                continue

            # 2) 如果你特别讨厌 linux，可以直接全跳了：
            # if diff_file.name.startswith("linux_"):
            #     print(f"[SKIP-LINUX] {diff_file.name}")
            #     continue

            try:
                text = diff_file.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"[ERROR-READ] {diff_file.name}: {e}")
                continue

            commit_id = diff_file.stem

            try:
                parsed = parse_diff(text)
            except Exception as e:
                print(f"[ERROR-PARSE] {diff_file.name}: {e}")
                continue

            record = {
                "commit": commit_id,
                "files": parsed
            }

            # 一行写一个 JSON，内存不会爆
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

            print(f"[OK] {diff_file.name}")

    print(f"[DONE] JSONL saved → {OUT_FILE}")
