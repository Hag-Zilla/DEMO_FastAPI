"""Application bootstrap tests."""

from services.api import main as main_module


class TestSentrySetup:
    """Tests for conditional Sentry initialization."""

    def test_configure_sentry_skips_without_dsn(self, monkeypatch) -> None:
        """Sentry stays disabled when no DSN is configured."""
        called: dict[str, object] = {}

        def fake_init(*args, **kwargs) -> None:
            called["args"] = args
            called["kwargs"] = kwargs

        monkeypatch.setattr(main_module.sentry_sdk, "init", fake_init)
        monkeypatch.setattr(main_module.settings, "SENTRY_DSN", None)
        monkeypatch.setattr(main_module.settings, "ENVIRONMENT", "staging")

        assert main_module.configure_sentry() is False
        assert called == {}

    def test_configure_sentry_skips_in_local(self, monkeypatch) -> None:
        """Sentry stays disabled in the local environment."""
        called: dict[str, object] = {}

        def fake_init(*args, **kwargs) -> None:
            called["args"] = args
            called["kwargs"] = kwargs

        monkeypatch.setattr(main_module.sentry_sdk, "init", fake_init)
        monkeypatch.setattr(
            main_module.settings,
            "SENTRY_DSN",
            "https://public@example.ingest.sentry.io/123456",
        )
        monkeypatch.setattr(main_module.settings, "ENVIRONMENT", "local")

        assert main_module.configure_sentry() is False
        assert called == {}

    def test_configure_sentry_initializes_in_staging(self, monkeypatch) -> None:
        """Sentry initializes when DSN is set and env is non-local."""
        called: dict[str, object] = {}

        def fake_init(*args, **kwargs) -> None:
            called["args"] = args
            called["kwargs"] = kwargs

        dsn = "https://public@example.ingest.sentry.io/123456"
        monkeypatch.setattr(main_module.sentry_sdk, "init", fake_init)
        monkeypatch.setattr(main_module.settings, "SENTRY_DSN", dsn)
        monkeypatch.setattr(main_module.settings, "ENVIRONMENT", "staging")

        assert main_module.configure_sentry() is True
        assert called["args"] == ()
        assert called["kwargs"] == {
            "dsn": dsn,
            "enable_tracing": True,
            "environment": "staging",
        }
