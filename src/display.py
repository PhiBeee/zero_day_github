def show_cluster(cid, clusters, max_items=10):
    items = clusters[cid][:max_items]
    for s in items:
        print("=== Commit:", s["commit"])
        print("File:", s["file"])
        print("Text:", s["text"][:300])  # print first 300 chars
        print("-" * 60)

def show_cluster_with_raw(cid, clusters, snippets, max_items=5):
    print(f"=== Cluster {cid} ===")
    for ns in clusters[cid][:max_items]:
        orig = snippets[ns["idx"]]
        print("Commit:", orig["commit"])
        print("File  :", orig["file"])
        print("DELETES:")
        for l in orig["dels"]:
            print("  ", l)
        print("ADDS:")
        for l in orig["adds"]:
            print("  ", l)
        print("-" * 60)