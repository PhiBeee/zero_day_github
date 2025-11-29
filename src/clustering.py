import pandas as pd 
import os
from plotting import plot_cluster_bar, plot_elbow_curve, plot_silhoute_score, plot_tsne_clusters, plot_umap_hac, plot_umap_kmeans

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import umap.umap_ as umap

DF_PATH = '../data/normalized_merged_df_score65.csv'

# Make sure we have all directories necessary for plots and data
if not os.path.exists("../clustering"):
    os.mkdir('../clustering')
if not os.path.exists('../clustering/hac_clustering'):
    os.mkdir('../clustering/hac_clustering')
if not os.path.exists('../clustering/kmeans_clustering'):
    os.mkdir('../clustering/kmeans_clustering')

def show_kmeans_cluster(df, cid, n=10):
    """
    Print n examples from a given KMeans cluster.
    cid : cluster id (0..17)

    """
    subset = df[df["cluster_kmeans"] == cid].head(n)
    total = len(df[df["cluster_kmeans"] == cid])
    print(f"=== KMeans Cluster {cid} (showing {len(subset)} of {total}) ===\n")
    for _, row in subset.iterrows():
        print("CVE:", row["cve_id"], "| Score:", row["score"])
        print("Repo:", row["repo_url"])
        print("File:", row["file"])
        print("--- DELETED ---")
        print(row.get("deleted_code", ""))
        print("--- ADDED ---")
        print(row.get("added_code", ""))
        print("=" * 80)

def show_hac_cluster(df, cid, n=10):
    """
    Print n examples from a given Agglomerative (HAC) cluster.
    """
    subset = df[df["cluster_hac"] == cid].head(n)
    total = len(df[df["cluster_hac"] == cid])
    print(f"=== HAC Cluster {cid} (showing {len(subset)} of {total}) ===\n")
    for _, row in subset.iterrows():
        print("CVE:", row["cve_id"], "| Score:", row["score"])
        print("Repo:", row["repo_url"])
        print("File:", row["file"])
        print("--- DELETED ---")
        print(row.get("deleted_code", ""))
        print("--- ADDED ---")
        print(row.get("added_code", ""))
        print("=" * 80)

def clustering():
    df = pd.read_csv(DF_PATH)

    vectorizer = TfidfVectorizer(
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 3)
    )

    X = vectorizer.fit_transform(df["text_norm"])

    K = 18

    kmeans = KMeans(
        n_clusters=K,
        random_state=0,
        n_init=10
    )

    df["cluster_kmeans"] = kmeans.fit_predict(X)
    cluster_counts = df['cluster_kmeans'].value_counts().sort_index()
    plot_cluster_bar(cluster_counts)

    Ks = list(range(5, 41))
    inertias = []

    for k in Ks:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        inertias.append(km.inertia_)

    plot_elbow_curve(inertias, Ks)

    scores = {}

    for k in [5, 10, 15, 18, 20, 25, 30, 35]:
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        labels = km.labels_
        score = silhouette_score(X, labels)
        scores[k] = score
        print(f"K={k}, Silhouette={score:.4f}")

    plot_silhoute_score(scores)

    subset = X[:5000]   # TSNE is heavy
    subset_labels = df['cluster_kmeans'][:5000]

    tsne = TSNE(n_components=2, perplexity=50, random_state=42)
    X_emb = tsne.fit_transform(subset.toarray())

    plot_tsne_clusters(X_emb, subset_labels)

    df_kmeans_sorted = df.sort_values("cluster_kmeans")
    df_kmeans_sorted.to_csv("../clustering/kmeans_clustering/kmeans_clusters_all.csv", index=False)
    print("Saved all KMeans clusters to kmeans_clusters_all.csv")

    unique_clusters = sorted(df["cluster_kmeans"].unique())

    for cid in unique_clusters:
        subset = df[df["cluster_kmeans"] == cid]
        fname = f"../clustering/kmeans_clustering/kmeans_cluster_{cid}.csv"
        subset.to_csv(fname, index=False)
        print(f"Saved {fname} with {len(subset)} rows")

    svd = TruncatedSVD(n_components=100, random_state=0)
    X_svd = svd.fit_transform(X)
    print("Shape after SVD:", X_svd.shape)

    hac = AgglomerativeClustering(
        n_clusters=18,
        linkage="ward",
        metric="euclidean"
    )

    df["cluster_hac"] = hac.fit_predict(X_svd)
    print(df["cluster_hac"].value_counts().sort_index())

    df_hac_sorted = df.sort_values("cluster_hac")
    df_hac_sorted.to_csv("../clustering/hac_clustering/hac_clusters_all.csv", index=False)
    print("Saved all HAC clusters to hac_clusters_all.csv")

    for cid in sorted(df["cluster_hac"].unique()):
        subset = df[df["cluster_hac"] == cid]
        fname = f"../clustering/hac_clustering/hac_cluster_{cid}.csv"
        subset.to_csv(fname, index=False)
        print(f"Saved {fname} with {len(subset)} rows")

    reducer = umap.UMAP(
        n_neighbors=25,
        min_dist=0.1,
        metric="euclidean",
        random_state=0
    )

    embedding = reducer.fit_transform(X_svd)

    df["umap_x"] = embedding[:, 0]
    df["umap_y"] = embedding[:, 1]

    print("UMAP embedding completed. Columns: umap_x, umap_y")
    plot_umap_kmeans(df)
    plot_umap_hac(df)

    cluster_stats_kmeans = (
        df.groupby("cluster_kmeans")
        .agg(
            n_snippets=("commit", "count"),
            n_commits=("hash_clean", "nunique"),
            n_cves=("cve_id", "nunique"),
            avg_score=("score", "mean")
        )
        .sort_index()
    )

    cluster_stats_kmeans
    cluster_stats_kmeans.to_csv("../clustering/cluster_stats_kmeans.csv")

    cluster_stats_hac = (
        df.groupby("cluster_hac")
        .agg(
            n_snippets=("commit", "count"),
            n_commits=("hash_clean", "nunique"),
            n_cves=("cve_id", "nunique"),
            avg_score=("score", "mean")
        )
        .sort_index()
    )

    cluster_stats_hac
    cluster_stats_hac.to_csv("../clustering/cluster_stats_hac.csv")


if __name__ == '__main__':
    clustering()