from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config import Config
from .utils import parse_datetime, request_with_retries, split_keywords, sanitize_tag


_NEWS_PATH_RE = re.compile(r"^/\d{8}/.+\.html$")
_URL_DATE_RE = re.compile(r"/(\d{8})/")


def fetch_section_html(config: Config, url: str | None = None) -> str:
    target = url or config.section_url
    return request_with_retries(target, config)


def _normalize_news_url(href: str | None, config: Config) -> str | None:
    if not href:
        return None
    if href.startswith("//"):
        href = f"https:{href}"

    if href.startswith("http://") or href.startswith("https://"):
        if not href.startswith(config.base_url):
            return None
        path = urlparse(href).path
        if not _NEWS_PATH_RE.match(path):
            return None
        return href

    if not href.startswith("/"):
        return None
    if not _NEWS_PATH_RE.match(href):
        return None
    return urljoin(config.base_url, href)


def extract_news_urls(html: str, config: Config) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    urls: list[str] = []

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        url = _normalize_news_url(href, config)
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)

    return urls


def extract_url_date(url: str) -> datetime | None:
    path = urlparse(url).path
    match = _URL_DATE_RE.search(path)
    if not match:
        return None
    value = match.group(1)
    try:
        return datetime.strptime(value, "%Y%m%d")
    except ValueError:
        return None


def _first_text(soup: BeautifulSoup, selectors: Iterable[str]) -> str | None:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = node.get_text(" ", strip=True)
            if text:
                return text
    return None


def _extract_header(soup: BeautifulSoup) -> str | None:
    header = _first_text(soup, ["h1.article__title", "h1"])
    if header:
        return header
    return None


def _extract_date(soup: BeautifulSoup) -> str | None:
    time_node = soup.find("time", datetime=True)
    if time_node and time_node.get("datetime"):
        return time_node.get("datetime")

    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta and meta.get("content"):
        return meta.get("content")

    meta = soup.find("meta", attrs={"name": "pubdate"})
    if meta and meta.get("content"):
        return meta.get("content")

    time_node = soup.find("time")
    if time_node:
        text = time_node.get_text(" ", strip=True)
        if text:
            return text

    return None


def _extract_text(soup: BeautifulSoup) -> str:
    container = soup.select_one("div.article__body")
    if not container:
        container = soup.select_one("div.article__text")
    if not container:
        container = soup.find("article")

    paragraphs = []
    if container:
        for block in container.select('div.article__block[data-type="text"] div.article__text'):
            text = block.get_text(" ", strip=True)
            if not text:
                continue
            if "\u0427\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0430\u043a\u0436\u0435" in text:
                continue
            paragraphs.append(text)

        if not paragraphs:
            for block in container.select("div.article__text"):
                text = block.get_text(" ", strip=True)
                if not text:
                    continue
                if "\u0427\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0430\u043a\u0436\u0435" in text:
                    continue
                paragraphs.append(text)

        if not paragraphs:
            for paragraph in container.find_all("p"):
                text = paragraph.get_text(" ", strip=True)
                if not text:
                    continue
                if "\u0427\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0430\u043a\u0436\u0435" in text:
                    continue
                paragraphs.append(text)

    return "\n".join(paragraphs)


def _extract_tags(soup: BeautifulSoup) -> list[str]:
    tags: list[str] = []
    for selector in ["a.article__tags-item", "a.article__tags-item-link", "a.article__tags-link"]:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if text:
                tags.append(sanitize_tag(text))

    if tags:
        return tags

    meta = soup.find("meta", attrs={"name": "keywords"})
    if meta and meta.get("content"):
        return [sanitize_tag(item) for item in split_keywords(meta.get("content"))]

    meta = soup.find("meta", attrs={"name": "news_keywords"})
    if meta and meta.get("content"):
        return [sanitize_tag(item) for item in split_keywords(meta.get("content"))]

    return []


def parse_news(url: str, config: Config) -> dict | None:
    html = request_with_retries(url, config)
    soup = BeautifulSoup(html, "html.parser")

    header = _extract_header(soup)
    if not header:
        return None

    date_value = _extract_date(soup)
    parsed_date = parse_datetime(date_value)
    if not parsed_date:
        return None

    text = _extract_text(soup)
    tags = _extract_tags(soup)

    return {
        "header": header,
        "text": text,
        "date": parsed_date.isoformat(),
        "hashtags": tags,
        "source_name": config.source_name,
    }
