"""Similarity and distance computations."""

from __future__ import annotations

import numpy as np


def compute_jaccard_similarity(cochange_matrix: np.ndarray) -> np.ndarray:
    """Compute Jaccard similarity from a co-change matrix."""
    if cochange_matrix.ndim != 2 or cochange_matrix.shape[0] != cochange_matrix.shape[1]:
        raise ValueError("cochange_matrix must be a square matrix")

    file_count = cochange_matrix.shape[0]
    if file_count == 0:
        return np.zeros((0, 0), dtype=float)

    diagonal = np.diag(cochange_matrix)
    similarity = np.zeros_like(cochange_matrix, dtype=float)

    for i in range(file_count):
        similarity[i, i] = 1.0 if diagonal[i] > 0 else 0.0
        for j in range(i + 1, file_count):
            intersection = cochange_matrix[i, j]
            union = diagonal[i] + diagonal[j] - intersection
            score = 0.0 if union <= 0 else float(intersection / union)
            similarity[i, j] = score
            similarity[j, i] = score

    return similarity


def compute_distance_matrix(similarity_matrix: np.ndarray) -> np.ndarray:
    """Convert similarity to distance with clipping to [0, 1]."""
    if similarity_matrix.ndim != 2 or similarity_matrix.shape[0] != similarity_matrix.shape[1]:
        raise ValueError("similarity_matrix must be a square matrix")

    distance = 1.0 - similarity_matrix
    return np.clip(distance, 0.0, 1.0)
