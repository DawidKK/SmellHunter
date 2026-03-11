"""Co-change matrix and graph construction."""

from __future__ import annotations

from itertools import combinations

import networkx as nx
import numpy as np


def build_cochange_matrix(
    commits: list[list[str]],
    *,
    min_cochange: int = 1,
) -> tuple[list[str], np.ndarray, nx.Graph]:
    """Build file index, co-change matrix, and weighted co-change graph."""
    if min_cochange < 1:
        raise ValueError("min_cochange must be >= 1")

    files = sorted({file_path for commit in commits for file_path in commit})
    file_count = len(files)
    index_by_file = {file_path: idx for idx, file_path in enumerate(files)}

    matrix = np.zeros((file_count, file_count), dtype=float)
    for commit in commits:
        unique_files = sorted(set(commit))
        if not unique_files:
            continue

        indices = [index_by_file[file_path] for file_path in unique_files]
        for idx in indices:
            matrix[idx, idx] += 1.0

        for left_idx, right_idx in combinations(indices, 2):
            matrix[left_idx, right_idx] += 1.0
            matrix[right_idx, left_idx] += 1.0

    if file_count > 1:
        off_diagonal = ~np.eye(file_count, dtype=bool)
        matrix[np.logical_and(off_diagonal, matrix < float(min_cochange))] = 0.0

    graph = nx.Graph()
    graph.add_nodes_from(files)
    for i, left_file in enumerate(files):
        for j in range(i + 1, file_count):
            weight = matrix[i, j]
            if weight >= float(min_cochange):
                graph.add_edge(left_file, files[j], weight=weight)

    return files, matrix, graph
