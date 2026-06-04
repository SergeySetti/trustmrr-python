from unittest.mock import MagicMock, patch

import pytest

from trustmrr import TrustMRRClient, TrustMRRError

SAMPLE_STARTUP = {
    "data": {
        "name": "Acme",
        "slug": "acme",
        "icon": None,
        "description": "An example startup",
        "website": "https://acme.example",
        "country": "US",
        "foundedDate": "2023-01-15",
        "category": "SaaS",
        "revenue": {"last30Days": 42500, "mrr": 35000, "total": 1000000},
        "growth30d": 0.12,
        "growthMRR30d": 0.08,
        "rank": 17,
        "profitMarginLast30Days": 42.5,
        "customers": 120,
        "activeSubscriptions": 80,
        "visitorsLast30Days": 9000,
        "xFollowerCount": 1234,
        "techStack": [{"name": "Stripe"}],
        "cofounders": [{"xHandle": "acmehq", "xName": "Acme Founder"}],
        "isMerchantOfRecord": False,
        "onSale": True,
    }
}


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.ok = 200 <= status_code < 300
    return resp


@pytest.fixture
def client():
    return TrustMRRClient(api_key="tmrr_test_key")


def test_get_startup_uses_correct_url_and_method(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_STARTUP)) as req:
        client.get_startup("acme")
        kwargs = req.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://trustmrr.com/api/v1/startups/acme"
        assert kwargs["params"] == {}


def test_get_startup_sends_bearer_auth(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_STARTUP)) as req:
        client.get_startup("acme")
        assert req.call_args.kwargs["headers"]["Authorization"] == "Bearer tmrr_test_key"


def test_get_startup_returns_parsed_payload(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_STARTUP)):
        result = client.get_startup("acme")
    assert result["data"]["slug"] == "acme"
    assert result["data"]["revenue"]["mrr"] == 35000
    assert result["data"]["cofounders"][0]["xHandle"] == "acmehq"


def test_get_startup_empty_slug_raises(client):
    with pytest.raises(ValueError):
        client.get_startup("")


def test_get_startup_non_string_slug_raises(client):
    with pytest.raises(ValueError):
        client.get_startup(None)  # type: ignore[arg-type]


def test_get_startup_404_raises_trustmrr_error(client):
    err_resp = _mock_response({"error": "not found"}, status_code=404)
    with patch.object(client._session, "request", return_value=err_resp):
        with pytest.raises(TrustMRRError) as exc:
            client.get_startup("missing")
        assert exc.value.status_code == 404
