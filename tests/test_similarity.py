import numpy as np

from arch_audit.similarity import compute_distance_matrix, compute_jaccard_similarity


def test_compute_jaccard_similarity_from_cochange_matrix() -> None:
    cochange = np.array(
        [
            [3.0, 2.0, 1.0],
            [2.0, 2.0, 1.0],
            [1.0, 1.0, 1.0],
        ]
    )

    similarity = compute_jaccard_similarity(cochange)

    # a<->b = 2 / (3 + 2 - 2) = 2/3
    assert np.isclose(similarity[0, 1], 2.0 / 3.0)
    # a<->c = 1 / (3 + 1 - 1) = 1/3
    assert np.isclose(similarity[0, 2], 1.0 / 3.0)
    assert np.allclose(np.diag(similarity), np.array([1.0, 1.0, 1.0]))


def test_compute_distance_matrix() -> None:
    similarity = np.array(
        [
            [1.0, 0.75],
            [0.75, 1.0],
        ]
    )

    distance = compute_distance_matrix(similarity)

    assert np.allclose(distance, np.array([[0.0, 0.25], [0.25, 0.0]]))
