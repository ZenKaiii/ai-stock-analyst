from ai_stock_analyst.broker.ibkr import _extract_accounts_from_payload, _extract_positions_from_payload


def test_extract_accounts_from_list_payload():
    payload = [{"id": "DU123"}, {"accountId": "U456"}, "DU789"]
    assert _extract_accounts_from_payload(payload) == ["DU123", "U456", "DU789"]


def test_extract_accounts_from_dict_payload():
    payload = {"accounts": ["DU111", "DU222"]}
    assert _extract_accounts_from_payload(payload) == ["DU111", "DU222"]


def test_extract_positions_from_payload():
    assert _extract_positions_from_payload([{"ticker": "AAPL"}]) == [{"ticker": "AAPL"}]
    assert _extract_positions_from_payload({"positions": [{"ticker": "MSFT"}]}) == [{"ticker": "MSFT"}]
    assert _extract_positions_from_payload({"data": [{"ticker": "NVDA"}]}) == [{"ticker": "NVDA"}]
