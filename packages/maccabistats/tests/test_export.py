"""Tests for ExportMaccabiGamesStats using synthetic fixture."""
import json


def test_export_players_events_json(tmp_path, maccabi_games):
    path = maccabi_games.export.export_players_events_json(folder_path=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text(encoding='utf8'))
    assert len(data) > 0


def test_export_games_data_json(tmp_path, maccabi_games):
    path = maccabi_games.export.export_games_data_json(folder_path=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text(encoding='utf8'))
    assert len(data) == 10


def test_export_players_events_csv(tmp_path, maccabi_games):
    path = maccabi_games.export.export_players_events_csv(folder_path=tmp_path)
    assert path.exists()
    lines = path.read_text(encoding='utf8').strip().split('\n')
    assert len(lines) > 1  # header + data


def test_export_games_data_csv(tmp_path, maccabi_games):
    path = maccabi_games.export.export_games_data_csv(folder_path=tmp_path)
    assert path.exists()
    lines = path.read_text(encoding='utf8').strip().split('\n')
    assert len(lines) == 11  # header + 10 games


def test_export_everything_json(tmp_path, maccabi_games):
    path = maccabi_games.export.export_everything_json(folder_path=tmp_path)
    assert path.exists()
    assert path.suffix == '.zip'


def test_export_everything_csv(tmp_path, maccabi_games):
    path = maccabi_games.export.export_everything_csv(folder_path=tmp_path)
    assert path.exists()
    assert path.suffix == '.zip'
