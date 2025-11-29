import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def get_code_snippets(commits):
    snippets = []
    for c in commits:
        cid = c["commit"]
        for f in c.get("files", []):
            file_path = f.get("file")
            adds, dels = [], []

            for ch in f.get("changes", []):
                t = ch.get("type")
                line = ch.get("line", "")
                if t == "add":
                    adds.append(line)
                elif t == "delete":
                    dels.append(line)

            # only keeping entries with only one add/del
            if adds or dels:
                snippets.append(
                    {
                        "commit": cid,
                        "file": file_path,
                        "added_code": "\n".join(adds),
                        "deleted_code": "\n".join(dels),
                    }
                )

    print("Total snippets:", len(snippets))
    print("Example snippet:")

    return snippets

def normalize_line(line):
    line = line.strip()
    # dropping the common comments
    line = re.sub(r"//.*", "", line)
    line = re.sub(r"#.*", "", line)
    line = re.sub(r"/\*.*?\*/", "", line)
    # collaps or removing whitespace
    line = re.sub(r"\s+", " ", line)
    # very simple identifier abstraction
    line = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "VAR", line)
    return line

def normalize_block(block: str) -> str:
    if not isinstance(block, str):
        return ""
    lines = block.splitlines()
    return " ".join(
        normalize_line(l) for l in lines
        if l.strip()
    )

def normalize_snippets(snippets):
    n_s = []

    for idx, s in enumerate(snippets):
        norm_adds = [normalize_line(l) for l in s['adds']]
        norm_dels = [normalize_line(l) for l in s['dels']]

        n_s.append({
            'idx': idx,
            'commit': s['commit'],
            'file': s['file'],
            'text': ''.join(norm_adds+norm_dels)
        })

    return n_s

def get_clusters(normalized_snippets):
    # Vectorize our data
    corpus = [s['text'] for s in normalize_snippets]

    vectorizer = TfidfVectorizer(
        min_df = 2,          # Ignorepatterns that only appear once
        max_df = .8,         # Ignore common things
        ngram_range = (1, 3) # Up to trigrams
    )

    X = vectorizer.fit_transform(corpus)

    # Predict clusters using Kmeans 

    k = 18
    kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
    labels = kmeans.fit_predict(X)

    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(normalized_snippets[i])

    return clusters 