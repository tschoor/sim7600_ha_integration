"""Configuration for pytest."""
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield
