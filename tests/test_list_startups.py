from unittest.mock import MagicMock, patch

import pytest

from trustmrr import TrustMRRClient, TrustMRRError


SAMPLE_RESPONSE = {
    "data": [
        {
            "name": "Acme",
            "slug": "acme",
            "icon": None,
            "description": "An example startup",
            "website": "https://acme.example",
            "country": "US",
            "foundedDate": "2023-01-15",
            "category": "SaaS",
            "paymentProvider": "stripe",
            "targetAudience": "developers",
            "revenue": {"last30Days": 42500, "mrr": 35000, "total": 1000000},
            "customers": 120,
            "activeSubscriptions": 80,
            "askingPrice": 5000000,
            "profitMarginLast30Days": 42.5,
            "growth30d": 0.12,
            "growthMRR30d": 0.08,
            "multiple": 3.2,
            "rank": 17,
            "visitorsLast30Days": 9000,
            "googleSearchImpressionsLast30Days": 23000,
            "revenuePerVisitor": 4.72,
            "onSale": True,
            "firstListedForSaleAt": "2024-09-01",
            "xHandle": "acmehq",
        }
    ],
    "meta": {"total": 1, "page": 1, "limit": 10, "hasMore": False},
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


def test_client_requires_api_key():
    with pytest.raises(ValueError):
        TrustMRRClient(api_key="")


def test_list_startups_sends_bearer_auth(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        client.list_startups()
        kwargs = req.call_args.kwargs
        assert kwargs["headers"]["Authorization"] == "Bearer tmrr_test_key"


def test_list_startups_uses_correct_url_and_method(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        client.list_startups()
        args, kwargs = req.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://trustmrr.com/api/v1/startups"


def test_list_startups_returns_parsed_payload(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)):
        result = client.list_startups()
    assert result["meta"]["total"] == 1
    assert result["data"][0]["slug"] == "acme"
    assert result["data"][0]["revenue"]["mrr"] == 35000


def test_list_startups_omits_none_params(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        client.list_startups()
        params = req.call_args.kwargs["params"]
        assert params == {}


def test_list_startups_passes_all_supported_params(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        client.list_startups(
            page=2,
            limit=25,
            sort="best-deal",
            on_sale=True,
            category="SaaS",
            x_handle="acmehq",
            min_revenue=10000,
            max_revenue=500000,
            min_mrr=1000,
            max_mrr=100000,
            min_growth=0.1,
            max_growth=0.9,
            min_price=100000,
            max_price=10000000,
        )
        params = req.call_args.kwargs["params"]
        assert params == {
            "page": 2,
            "limit": 25,
            "sort": "best-deal",
            "onSale": "true",
            "category": "SaaS",
            "xHandle": "acmehq",
            "minRevenue": 10000,
            "maxRevenue": 500000,
            "minMrr": 1000,
            "maxMrr": 100000,
            "minGrowth": 0.1,
            "maxGrowth": 0.9,
            "minPrice": 100000,
            "maxPrice": 10000000,
        }


def test_on_sale_false_serialises_as_string(client):
    with patch.object(client._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        client.list_startups(on_sale=False)
        assert req.call_args.kwargs["params"]["onSale"] == "false"


def test_limit_out_of_range_raises(client):
    with pytest.raises(ValueError):
        client.list_startups(limit=0)
    with pytest.raises(ValueError):
        client.list_startups(limit=51)


def test_page_must_be_positive(client):
    with pytest.raises(ValueError):
        client.list_startups(page=0)


def test_invalid_sort_raises(client):
    with pytest.raises(ValueError):
        client.list_startups(sort="bogus")


def test_http_error_raises_trustmrr_error(client):
    err_resp = _mock_response({"error": "unauthorized"}, status_code=401)
    with patch.object(client._session, "request", return_value=err_resp):
        with pytest.raises(TrustMRRError) as exc:
            client.list_startups()
        assert exc.value.status_code == 401


def test_iter_startups_paginates(client):
    page1 = {
        "data": [{"slug": "a"}, {"slug": "b"}],
        "meta": {"total": 3, "page": 1, "limit": 2, "hasMore": True},
    }
    page2 = {
        "data": [{"slug": "c"}],
        "meta": {"total": 3, "page": 2, "limit": 2, "hasMore": False},
    }
    responses = [_mock_response(page1), _mock_response(page2)]
    with patch.object(client._session, "request", side_effect=responses) as req:
        slugs = [s["slug"] for s in client.iter_startups(limit=2)]
    assert slugs == ["a", "b", "c"]
    assert req.call_count == 2
    assert req.call_args_list[1].kwargs["params"]["page"] == 2


def test_custom_base_url():
    c = TrustMRRClient(api_key="k", base_url="https://staging.trustmrr.com/api/v1/")
    with patch.object(c._session, "request", return_value=_mock_response(SAMPLE_RESPONSE)) as req:
        c.list_startups()
        assert req.call_args.kwargs["url"] == "https://staging.trustmrr.com/api/v1/startups"
