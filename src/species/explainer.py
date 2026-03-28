from __future__ import annotations

from .models import RuleOrigin, ValidationError, ValidationReport


def error(
    *,
    code: str,
    message: str,
    measure: int,
    beat: int,
    origin: RuleOrigin,
    evidence: dict | None = None,
) -> ValidationError:
    return ValidationError(
        code=code,
        message=message,
        measure=measure,
        beat=beat,
        origin=origin,
        evidence=evidence or {},
    )


def report(errors: list[ValidationError], trace: list[dict] | None = None) -> ValidationReport:
    return ValidationReport(valid=not errors, errors=errors, trace=trace or [])
