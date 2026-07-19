"""Unit tests for the football refresh_by_category maintenance job."""
from unittest.mock import MagicMock, patch

import pytest
from pywikibot.exceptions import TimeoutError as PwbTimeoutError

from maccabipediabot.maintenance.football import refresh_by_category


def _page(title: str) -> MagicMock:
    page = MagicMock()
    page.title.return_value = title
    return page


class TestCollectMembers:
    @patch("maccabipediabot.maintenance.football.refresh_by_category.pywikibot")
    def test_returns_article_members_without_recursing(self, mock_pw):
        members = [_page("אבי כהן"), _page("אורי מלמיליאן")]
        mock_pw.Category.return_value.articles.return_value = iter(members)

        result = refresh_by_category.collect_members(MagicMock(), "פרופילי כדורגל")

        assert result == members
        mock_pw.Category.return_value.articles.assert_called_once_with(recurse=False)


@patch("maccabipediabot.maintenance.football.refresh_by_category.get_site")
@patch("maccabipediabot.maintenance.football.refresh_by_category.setup_logging")
class TestMain:
    @patch("maccabipediabot.maintenance.football.refresh_by_category.purge_pages")
    @patch("maccabipediabot.maintenance.football.refresh_by_category.collect_members")
    def test_purges_collected_members_and_passes_dry_run(
        self, mock_collect, mock_purge, _setup_logging, _get_site
    ):
        members = [_page("אבי כהן"), _page("אורי מלמיליאן")]
        mock_collect.return_value = members
        mock_purge.return_value = len(members)

        rc = refresh_by_category.main(dry_run=True, category="פרופילי כדורגל")

        assert rc == 0
        mock_collect.assert_called_once()
        # dry_run must flow through, and the whole (single) batch passed as-is.
        assert mock_purge.call_args.kwargs["dry_run"] is True
        assert list(mock_purge.call_args.args[1]) == members

    @patch("maccabipediabot.maintenance.football.refresh_by_category.purge_pages")
    @patch("maccabipediabot.maintenance.football.refresh_by_category.collect_members")
    def test_splits_into_batches_covering_every_page(
        self, mock_collect, mock_purge, _setup_logging, _get_site
    ):
        # 25 pages at BATCH_SIZE=10 -> 3 batches (10/10/5), no page dropped.
        members = [_page(f"שחקן {i}") for i in range(25)]
        mock_collect.return_value = members
        mock_purge.side_effect = lambda _site, batch, **_kw: len(list(batch))

        rc = refresh_by_category.main(dry_run=False, category="פרופילי כדורגל")

        assert rc == 0
        assert mock_purge.call_count == 3
        batched = [p for call in mock_purge.call_args_list for p in call.args[1]]
        assert batched == members

    @patch("maccabipediabot.maintenance.football.refresh_by_category.purge_pages")
    @patch("maccabipediabot.maintenance.football.refresh_by_category.collect_members")
    def test_timeout_in_one_batch_does_not_abort_the_sweep(
        self, mock_collect, mock_purge, _setup_logging, _get_site
    ):
        members = [_page(f"שחקן {i}") for i in range(25)]
        mock_collect.return_value = members
        # First batch times out the way the live 801-page run did; rest succeed.
        mock_purge.side_effect = [
            PwbTimeoutError("Maximum retries attempted without success"),
            10,
            5,
        ]

        rc = refresh_by_category.main(dry_run=False, category="פרופילי כדורגל")

        # Remaining batches still ran, but the failure is surfaced via exit code.
        assert mock_purge.call_count == 3
        assert rc == 1

    @patch("maccabipediabot.maintenance.football.refresh_by_category.purge_pages")
    @patch("maccabipediabot.maintenance.football.refresh_by_category.collect_members")
    def test_unexpected_errors_still_propagate(
        self, mock_collect, mock_purge, _setup_logging, _get_site
    ):
        mock_collect.return_value = [_page("אבי כהן")]
        mock_purge.side_effect = ValueError("boom")

        # Only server/timeout errors are tolerated — real bugs must stay visible.
        with pytest.raises(ValueError):
            refresh_by_category.main(dry_run=False, category="פרופילי כדורגל")
