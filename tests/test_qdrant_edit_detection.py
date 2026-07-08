from pathlib import Path

from transit_reader.utils.qdrant_setup import Setup


class _FakeRecord:
    def __init__(self, payload):
        self.payload = payload


class _FakeQdrantClient:
    def __init__(self, existing_hash):
        self.existing_hash = existing_hash
        self.deleted_filters = []

    def scroll(self, collection_name, scroll_filter, limit, with_payload):
        return ([_FakeRecord({"content_hash": self.existing_hash})], None)

    def delete(self, collection_name, points_selector):
        self.deleted_filters.append(points_selector)


def test_compute_content_hash_is_stable(tmp_path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("hello world")

    hash1 = Setup._compute_content_hash(file_path)
    hash2 = Setup._compute_content_hash(file_path)

    assert hash1 == hash2
    assert len(hash1) == 64  # sha256 hex digest length


def test_compute_content_hash_changes_with_content(tmp_path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("version one")
    hash1 = Setup._compute_content_hash(file_path)

    file_path.write_text("version two")
    hash2 = Setup._compute_content_hash(file_path)

    assert hash1 != hash2


def test_get_existing_content_hash_returns_stored_hash():
    setup = Setup.__new__(Setup)
    setup.qdrant_client = _FakeQdrantClient(existing_hash="abc123")
    setup.collection_name = "test_collection"

    result = setup._get_existing_content_hash("doc.md")

    assert result == "abc123"
