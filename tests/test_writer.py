import os
from app.storage.writer import write_snapshot

def test_write_snapshot(tmp_path):
    path = write_snapshot(str(tmp_path), "coingecko", {"bitcoin": 1.23}, {"http_status": 200, "latency_ms": 10, "attempts": 1})
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "bitcoin" in content
    assert "coingecko" in content
