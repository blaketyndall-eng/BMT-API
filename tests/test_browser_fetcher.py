from packages.connectors.browser_fetcher import extract_title, html_to_text


def test_extract_title_returns_clean_title() -> None:
    html = "<html><head><title>  Example Product | Docs  </title></head></html>"
    assert extract_title(html) == "Example Product | Docs"


def test_html_to_text_removes_tags_and_scripts() -> None:
    html = "<html><head><script>ignore()</script></head><body><h1>Hello</h1><p>World</p></body></html>"
    assert html_to_text(html) == "Hello World"
