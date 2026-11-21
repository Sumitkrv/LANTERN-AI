ALLOWED_STATUSES = {"429", "500", "502", "503"}


class InvalidSimulation(ValueError):
    pass


def simulated_failures(header: str | None, enabled: bool, key_count: int) -> dict[str, int]:
    if header is None or not enabled:
        return {}

    allowed_ids = {"*", *(f"key_{index}" for index in range(1, key_count + 1))}
    failures = {}
    for pair in header.split(","):
        key_id, _, status = (item.strip() for item in pair.partition("="))
        if key_id not in allowed_ids or status not in ALLOWED_STATUSES or key_id in failures:
            raise InvalidSimulation
        failures[key_id] = int(status)
    return failures
