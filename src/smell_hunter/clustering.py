"""Agglomerative clustering for file groups."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from sklearn.cluster import AgglomerativeClustering


def cluster_files(
    distance_matrix: np.ndarray,
    distance_threshold: float = 0.7,
    *,
    file_names: list[str] | None = None,
) -> list[list[int]]:
    """Cluster file indexes using agglomerative clustering over distances."""
    if distance_matrix.ndim != 2 or distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError("distance_matrix must be a square matrix")
    if distance_threshold <= 0:
        raise ValueError("distance_threshold must be > 0")

    file_count = distance_matrix.shape[0]
    if file_count == 0:
        return []
    if file_count == 1:
        return [[0]]

    model = AgglomerativeClustering(
        metric="precomputed",
        linkage="average",
        distance_threshold=distance_threshold,
        n_clusters=None,
    )
    labels = model.fit_predict(distance_matrix)

    grouped: dict[int, list[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        grouped[int(label)].append(idx)

    clusters = [sorted(indices) for _, indices in sorted(grouped.items(), key=lambda item: item[0])]
    return _sort_clusters_deterministically(clusters, file_names)


def _sort_clusters_deterministically(
    clusters: list[list[int]],
    file_names: list[str] | None,
) -> list[list[int]]:
    def cluster_lex_key(cluster: list[int]) -> tuple[str, ...]:
        if file_names is None:
            return tuple(str(index) for index in cluster)
        return tuple(file_names[index] for index in cluster)

    return sorted(
        clusters,
        key=lambda cluster: (-len(cluster), cluster_lex_key(cluster)),
    )
