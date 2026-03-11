from arch_audit.commit_parser import parse_commit_blocks


def test_parse_commit_blocks_handles_renames_and_filters() -> None:
    raw = "\n".join(
        [
            "M\tfrontend/ui/CheckoutButton.tsx",
            "M\tfrontend/api/PaymentAPI.ts",
            "M\tfrontend/ui/CheckoutButton.test.ts",
            "M\tfrontend/dist/bundle.js",
            "",
            "R100\tfrontend/legacy/CheckoutButton.tsx\tfrontend/ui/CheckoutButton.tsx",
            "M\tfrontend/api/PaymentAPI.ts",
            "",
            "M\tfrontend/legacy/CheckoutButton.tsx",
            "M\tfrontend/api/PaymentAPI.ts",
            "M\tfrontend/docs/readme.md",
            "",
        ]
    )

    commits = parse_commit_blocks(raw)

    assert commits == [
        ["frontend/ui/CheckoutButton.tsx", "frontend/api/PaymentAPI.ts"],
        ["frontend/ui/CheckoutButton.tsx", "frontend/api/PaymentAPI.ts"],
        ["frontend/ui/CheckoutButton.tsx", "frontend/api/PaymentAPI.ts"],
    ]


def test_parse_commit_blocks_ignores_large_commits() -> None:
    changed_files = [f"M\tfrontend/file_{i}.ts" for i in range(55)]
    raw = "\n".join(changed_files + ["", "M\tfrontend/kept.ts", "M\tfrontend/also_kept.ts", ""])

    commits = parse_commit_blocks(raw, max_files_per_commit=50)

    assert commits == [["frontend/kept.ts", "frontend/also_kept.ts"]]
