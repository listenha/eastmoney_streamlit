from eastmoney_tool.datacenter import EastMoneyDataCenter


def test_jsonp_parse():
    s = "jQuery123({\"a\": 1, \"result\": {\"data\": []}})"
    out = EastMoneyDataCenter._loads_json_or_jsonp(s)
    assert out["a"] == 1
