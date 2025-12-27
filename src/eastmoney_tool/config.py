from dataclasses import dataclass

@dataclass(frozen=True)
class EastMoneyConfig:
    """Runtime config.
    Note: for datacenter-web endpoints, we usually don't need cookies/tokens.
    """
    base_url: str = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    timeout_s: int = 15
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
    # Add proxy or headers here if needed later.
