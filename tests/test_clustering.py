import numpy as np

from arch_audit.clustering import cluster_files


def test_cluster_files_handles_edge_cases() -> None:
    assert cluster_files(np.zeros((0, 0))) == []
    assert cluster_files(np.zeros((1, 1))) == [[0]]


def test_cluster_files_returns_deterministic_sorted_clusters() -> None:
    distance = np.array(
        [
            [0.0, 0.1, 0.9, 0.9],
            [0.1, 0.0, 0.9, 0.9],
            [0.9, 0.9, 0.0, 0.1],
            [0.9, 0.9, 0.1, 0.0],
        ]
    )
    file_names = ["z.ts", "y.ts", "a.ts", "b.ts"]

    clusters = cluster_files(distance, distance_threshold=0.5, file_names=file_names)

    # Two size-2 clusters, ordered lexicographically by mapped file names.
    assert clusters == [[2, 3], [0, 1]]
