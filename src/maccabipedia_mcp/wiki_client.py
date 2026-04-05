from __future__ import annotations

from typing import Any

import requests

from maccabipedia_mcp.config import Config


class WikiClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._session = requests.Session()
        self._csrf_token: str | None = None

    @property
    def _api(self) -> str:
        return self._config.api_url

    def _get(self, params: dict[str, Any]) -> requests.Response:
        params.setdefault("format", "json")
        return self._session.get(self._api, params=params)

    def _check_json(self, resp: requests.Response) -> dict | None:
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type and "text/json" not in content_type:
            return {
                "error": True,
                "code": "non_json",
                "message": f"Cargo returned non-JSON response (Content-Type: {content_type})",
            }
        return None

    # -- Cargo tools --

    def list_cargo_tables(self) -> list[str] | dict:
        resp = self._get({"action": "cargotables"})
        err = self._check_json(resp)
        if err:
            return err
        return resp.json()["cargotables"]

    def describe_cargo_table(self, table: str) -> list[dict[str, str]] | dict:
        resp = self._get({"action": "cargofields", "table": table})
        err = self._check_json(resp)
        if err:
            return err
        fields = resp.json()["cargofields"]
        return [{"name": name, "type": ftype} for name, ftype in fields.items()]

    def query_cargo(
        self,
        tables: str,
        fields: str,
        where: str | None = None,
        join_on: str | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict] | dict:
        params: dict[str, Any] = {
            "action": "cargoquery",
            "tables": tables,
            "fields": fields,
            "limit": limit,
            "offset": offset,
        }
        if where:
            params["where"] = where
        if join_on:
            params["join_on"] = join_on
        if group_by:
            params["group_by"] = group_by
        if having:
            params["having"] = having
        if order_by:
            params["order_by"] = order_by

        resp = self._get(params)
        err = self._check_json(resp)
        if err:
            return err

        data = resp.json()
        return [row["title"] for row in data.get("cargoquery", [])]

    # -- Page read tools --

    def get_page(self, title: str) -> dict:
        resp = self._get({
            "action": "query",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content",
            "redirects": "1",
        })
        data = resp.json()
        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "missing" in page:
            return {"exists": False, "title": title, "wikitext": "", "redirect_target": None}

        redirect_target = None
        redirects = data["query"].get("redirects", [])
        for r in redirects:
            if r["from"] == title:
                redirect_target = r["to"]
                break

        wikitext = page.get("revisions", [{}])[0].get("*", "")
        return {
            "exists": True,
            "title": page["title"],
            "wikitext": wikitext,
            "redirect_target": redirect_target,
        }

    def page_exists(self, title: str) -> dict:
        resp = self._get({"action": "query", "titles": title})
        pages = resp.json()["query"]["pages"]
        page = next(iter(pages.values()))
        exists = "missing" not in page
        redirect = "redirect" in page
        return {"exists": exists, "redirect": redirect}

    def search_pages(self, query: str, namespace: int | None = None, limit: int = 10) -> list[dict]:
        params: dict[str, Any] = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        }
        if namespace is not None:
            params["srnamespace"] = namespace
        resp = self._get(params)
        return [
            {"title": r["title"], "snippet": r["snippet"]}
            for r in resp.json()["query"]["search"]
        ]

    def list_category_pages(self, category: str, limit: int = 50) -> list[str]:
        if not category.startswith("קטגוריה:"):
            category = f"קטגוריה:{category}"
        resp = self._get({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": limit,
        })
        return [m["title"] for m in resp.json()["query"]["categorymembers"]]
