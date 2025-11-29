import os 
import matplotlib.pyplot as plt
import seaborn as sns

if not os.path.exists("../clustering/plots"):
    os.mkdir('../clustering/plots')

PLOT_PATH = '../clustering/plots'

def plot_cluster_bar(cluster_counts):
    plt.figure(figsize=(10,5))
    cluster_counts.plot(kind='bar')
    plt.title("Cluster Sizes (K-Means, k=18)")
    plt.xlabel("Cluster ID")
    plt.ylabel("Number of Items")
    plt.savefig(f'{PLOT_PATH}/cluster_bar.jpg')
    plt.clf()

def plot_elbow_curve(inertias, Ks):
    plt.figure(figsize=(10,5))
    plt.plot(Ks, inertias, marker="o")
    plt.title("Elbow Curve")
    plt.xlabel("K")
    plt.ylabel("Inertia")
    plt.grid()
    plt.savefig(f'{PLOT_PATH}/elbow_curve.jpg')
    plt.clf()

def plot_silhoute_score(scores):
    plt.plot(list(scores.keys()), list(scores.values()), marker='o')
    plt.title("Silhouette Score vs K")
    plt.xlabel("K")
    plt.ylabel("Silhouette Score")
    plt.grid()
    plt.savefig(f'{PLOT_PATH}/silhoutte_score.jpg')
    plt.clf()

def plot_tsne_clusters(X_emb, subset_labels):
    plt.figure(figsize=(10,8))
    sns.scatterplot(x=X_emb[:,0], y=X_emb[:,1], hue=subset_labels, palette='tab20', s=10)
    plt.title("t-SNE Visualization of Clusters (5000 samples)")
    plt.savefig(f'{PLOT_PATH}/tsne_clusters.jpg')
    plt.clf()

def plot_umap_kmeans(df):
    plt.figure(figsize=(10, 8))
    plt.scatter(
        df["umap_x"], df["umap_y"],
        c=df["cluster_kmeans"],
        cmap="tab20",
        s=7,
        alpha=0.75
    )
    plt.title("UMAP Visualization – KMeans Clusters")
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.savefig(f'{PLOT_PATH}/umap_kmeans.jpg')
    plt.clf()

def plot_umap_hac(df):
    plt.figure(figsize=(10, 8))
    plt.scatter(
        df["umap_x"], df["umap_y"],
        c=df["cluster_hac"],
        cmap="tab20",
        s=7,
        alpha=0.75
    )
    plt.title("UMAP Visualization – HAC Clusters")
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.colorbar(label="Cluster ID")
    plt.savefig(f'{PLOT_PATH}/umap_hac.jpg')
    plt.clf()