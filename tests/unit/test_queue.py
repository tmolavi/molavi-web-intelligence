from mwie.crawler.queue import RequestQueue


def test_queue_deduplication_and_depth():
    q = RequestQueue(max_pages=5, max_depth=2)

    assert q.push("https://molavi.pro/page1", depth=0) is True
    # Duplicate push
    assert q.push("https://molavi.pro/page1/", depth=0) is False
    assert q.push("https://molavi.pro/page2", depth=1) is True
    assert q.push("https://molavi.pro/page3", depth=3) is False  # Exceeds max depth 2

    assert q.remaining() == 2
    item1 = q.pop()
    assert item1.url == "https://molavi.pro/page1"
    assert item1.depth == 0
