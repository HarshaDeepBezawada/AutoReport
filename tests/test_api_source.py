"""The REST adapter is tested with a stubbed `requests.get` (no network needed)."""

import pytest
import requests

from autoreport.ingestion import APISource, DataSourceError, get_source


class _Resp:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


def test_url_selects_api_adapter():
    assert isinstance(get_source("https://example.com/data"), APISource)


def test_api_list_and_wrapped_payloads(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp([{"a": 1}, {"a": 2}]))
    assert get_source("https://x.test/api").load()["a"].tolist() == [1, 2]
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp({"count": 2, "items": [{"b": 5}]}))
    assert get_source("https://x.test/api").load()["b"].tolist() == [5]


def test_api_http_error_is_wrapped(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp({}, status=500))
    with pytest.raises(DataSourceError, match="Failed to read"):
        get_source("https://x.test/api").load()
