from dataclasses import dataclass

from app.core.logging import get_logger


@dataclass(frozen=True)
class IncidentNotifierResult:
    provider: str
    delivered: bool
    skipped: bool = False
    message: str | None = None


class IncidentNotifierAdapter:
    provider_name: str

    def notify(self, title: str, message: str, severity: str = "warning") -> IncidentNotifierResult:
        raise NotImplementedError


class LogIncidentNotifier(IncidentNotifierAdapter):
    provider_name = "LOG"

    def __init__(self) -> None:
        self.logger = get_logger("ops.incident")

    def notify(self, title: str, message: str, severity: str = "warning") -> IncidentNotifierResult:
        self.logger.warning("incident severity=%s title=%s message=%s", severity, title, message)
        return IncidentNotifierResult(
            provider=self.provider_name,
            delivered=True,
            message="Incident was written to application log.",
        )


class SlackIncidentNotifier(IncidentNotifierAdapter):
    provider_name = "SLACK"

    def notify(self, title: str, message: str, severity: str = "warning") -> IncidentNotifierResult:
        return IncidentNotifierResult(
            provider=self.provider_name,
            delivered=False,
            skipped=True,
            message="Slack incident notifier is designed but not configured in this MVP phase.",
        )


class SentryIncidentNotifier(IncidentNotifierAdapter):
    provider_name = "SENTRY"

    def notify(self, title: str, message: str, severity: str = "warning") -> IncidentNotifierResult:
        return IncidentNotifierResult(
            provider=self.provider_name,
            delivered=False,
            skipped=True,
            message="Sentry incident notifier is designed but not configured in this MVP phase.",
        )
