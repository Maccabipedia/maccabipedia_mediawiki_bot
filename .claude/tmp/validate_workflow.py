"""Validate the new basketball workflow YAML."""
from pathlib import Path
import yaml

content = Path(".github/workflows/basketball_games_uploader.yaml").read_text()
parsed = yaml.safe_load(content)
assert parsed["name"] == "Upload Basketball Games To MaccabiPedia"
# YAML parses bare `on:` as the Python boolean True (the YAML 1.1 'on' alias).
on_block = parsed.get("on") if "on" in parsed else parsed.get(True)
assert on_block is not None, f"missing 'on' block; keys={list(parsed.keys())}"
assert "repository_dispatch" in on_block
assert on_block["repository_dispatch"]["types"] == ["zapier_trigger_basketball_upload_game"]
job = parsed["jobs"]["upload-basketball-games"]
assert len(job["steps"]) == 8, f"expected 8 steps, got {len(job['steps'])}"
print("workflow OK")
