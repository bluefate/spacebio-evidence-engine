"""Scaffold smoke tests until implementation lands."""


def test_package_version() -> None:
    from spacebio_evidence_engine import __version__

    assert __version__ == "0.1.0"
