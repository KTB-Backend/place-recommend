import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "dev",
    max_examples=50,
    deadline=None,
)
settings.register_profile(
    "ci",
    max_examples=200,
    deadline=500,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci" if os.getenv("CI") else "dev")
