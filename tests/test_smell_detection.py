import numpy as np

from smell_hunter.smell_detection import detect_smells


def test_detect_smells_flags_ccp_rep_and_crp() -> None:
    files = ["frontend/ui/A.tsx", "frontend/api/B.ts", "frontend/ui/C.tsx"]
    clusters = [[0, 1], [0, 2]]

    cochange = np.array(
        [
            [3.0, 2.0, 1.0],
            [2.0, 2.0, 0.0],
            [1.0, 0.0, 1.0],
        ]
    )
    similarity = np.array(
        [
            [1.0, 0.7, 0.1],
            [0.7, 1.0, 0.0],
            [0.1, 0.0, 1.0],
        ]
    )

    smells = detect_smells(
        clusters=clusters,
        files=files,
        cochange_matrix=cochange,
        similarity_matrix=similarity,
        rep_strong_coupling_threshold=2.0,
        crp_low_similarity_threshold=0.15,
    )

    assert len(smells["ccp"]) == 1
    assert smells["ccp"][0]["cluster_id"] == 1
    assert len(smells["rep"]) == 1
    assert smells["rep"][0]["cluster_id"] == 1
    assert len(smells["crp"]) == 1
    assert smells["crp"][0]["cluster_id"] == 2
