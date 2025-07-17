"""
Test configuration for ADITIM Monitor
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = MagicMock()
    config.monitoring.collection_interval = 1
    config.monitoring.max_workers = 2
    return config


@pytest.fixture
def mock_collector():
    """Mock collector for testing."""
    collector = AsyncMock()
    collector.name = "test_collector"
    collector.collect.return_value = []
    return collector
