"""Heuristic architectural smell detection for MVP reporting."""

from __future__ import annotations

from pathlib import PurePosixPath

import numpy as np

SmellFinding = dict[str, object]


def detect_smells(
    *,
    clusters: list[list[int]],
    files: list[str],
    cochange_matrix: np.ndarray,
    similarity_matrix: np.ndarray,
    rep_strong_coupling_threshold: float = 2.0,
    crp_low_similarity_threshold: float = 0.15,
) -> dict[str, list[SmellFinding]]:
    """Detect REP/CCP/CRP smells from clustered files and coupling matrices."""
    findings: dict[str, list[SmellFinding]] = {"rep": [], "ccp": [], "crp": []}

    for cluster_index, cluster in enumerate(clusters, start=1):
        if len(cluster) < 2:
            continue

        cluster_files = [files[idx] for idx in cluster]
        directories = {str(PurePosixPath(file_path).parent) for file_path in cluster_files}

        avg_cochange = _average_pair_value(cluster, cochange_matrix)
        max_cochange = _max_pair_value(cluster, cochange_matrix)
        avg_similarity = _average_pair_value(cluster, similarity_matrix)

        if len(directories) > 1 and avg_cochange >= 1.0:
            findings["ccp"].append(
                {
                    "cluster_id": cluster_index,
                    "files": cluster_files,
                    "message": (
                        "Files in this cluster change together but are spread across directories "
                        f"({', '.join(sorted(directories))})."
                    ),
                }
            )

        if len(directories) > 1 and max_cochange >= rep_strong_coupling_threshold:
            findings["rep"].append(
                {
                    "cluster_id": cluster_index,
                    "files": cluster_files,
                    "message": (
                        "Strong temporal coupling across separate directories suggests a packaging "
                        "(REP) risk."
                    ),
                }
            )

        if avg_similarity < crp_low_similarity_threshold:
            findings["crp"].append(
                {
                    "cluster_id": cluster_index,
                    "files": cluster_files,
                    "message": (
                        "Low internal similarity in this cluster suggests possible unnecessary "
                        "reuse/dependency coupling (CRP risk)."
                    ),
                }
            )

    return findings


def _average_pair_value(cluster: list[int], matrix: np.ndarray) -> float:
    values: list[float] = []
    for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
            values.append(float(matrix[cluster[i], cluster[j]]))
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _max_pair_value(cluster: list[int], matrix: np.ndarray) -> float:
    max_value = 0.0
    for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
            max_value = max(max_value, float(matrix[cluster[i], cluster[j]]))
    return max_value
