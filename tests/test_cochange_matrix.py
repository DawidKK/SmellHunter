import numpy as np

from smell_hunter.cochange_matrix import build_cochange_matrix


def test_build_cochange_matrix_counts_and_graph_edges() -> None:
    commits = [
        ["a.ts", "b.ts"],
        ["a.ts", "c.ts"],
        ["a.ts", "b.ts", "c.ts"],
    ]

    files, matrix, graph = build_cochange_matrix(commits, min_cochange=1)

    assert files == ["a.ts", "b.ts", "c.ts"]
    assert np.array_equal(
        matrix,
        np.array(
            [
                [3.0, 2.0, 2.0],
                [2.0, 2.0, 1.0],
                [2.0, 1.0, 2.0],
            ]
        ),
    )
    assert graph.has_edge("a.ts", "b.ts")
    assert graph["a.ts"]["b.ts"]["weight"] == 2.0


def test_build_cochange_matrix_applies_min_cochange_threshold() -> None:
    commits = [["a.ts", "b.ts"], ["a.ts", "c.ts"]]

    files, matrix, graph = build_cochange_matrix(commits, min_cochange=2)

    assert files == ["a.ts", "b.ts", "c.ts"]
    # a<->b and a<->c were only 1, so both are pruned.
    assert matrix[0, 1] == 0.0
    assert matrix[0, 2] == 0.0
    assert matrix[0, 0] == 2.0
    assert graph.number_of_edges() == 0
