"""Local filesystem implementation of the PDF storage protocol."""

from __future__ import annotations

from pathlib import Path


class LocalFileStorage:
    """Store PDFs on the local filesystem under a fixed root directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"Storage key escapes root: {key!r}")
        return path

    def put(self, publication_id: str, filename: str, data: bytes) -> str:
        key = f"{publication_id}/{filename}"
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def delete(self, key: str) -> None:
        path = self._path(key)
        path.unlink(missing_ok=True)
        parent = path.parent
        if parent != self.root and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()

    def get_path(self, key: str) -> Path:
        """Return the absolute filesystem path for a stored key."""
        return self._path(key)
