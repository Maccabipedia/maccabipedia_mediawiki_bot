"""Detect normalization collisions in translations dicts only for the dicts
that actually go through `_normalize_keys`."""
import re
import ast

src = open('packages/maccabipediabot/src/maccabipediabot/basketball/translations.py').read()
tree = ast.parse(src)

# Only the dicts that actually get normalized at module load:
NORMALIZED = {"_TEAM_NAMES", "_PERSON_NAMES", "_STADIUM_NAMES", "_PLAYER_NAME_NORMALIZE"}

for node in tree.body:
    if (isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id in NORMALIZED
            and isinstance(node.value, ast.Dict)):
        name = node.target.id
        seen = {}
        for k_node, v_node in zip(node.value.keys, node.value.values):
            if not isinstance(k_node, ast.Constant):
                continue
            k = k_node.value
            v = v_node.value if isinstance(v_node, ast.Constant) else '?'
            norm = re.sub(r"\s+", " ", k).strip() if k else k
            if norm in seen:
                print(f"COLLISION in {name}:")
                print(f"  key1={seen[norm][0]!r} -> {seen[norm][1]!r}")
                print(f"  key2={k!r} -> {v!r}")
                if seen[norm][1] != v:
                    print("  *** VALUES DIFFER — second overwrites first! ***")
            seen[norm] = (k, v)
print("done")
