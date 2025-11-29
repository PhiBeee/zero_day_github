import json

def load_diffs(filename):
    commits = []
    with open(f'../data/{filename}', "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            commits.append(obj)

    print("Total commits loaded:", len(commits))
    print("Example keys:", commits[0].keys())
    
    return commits