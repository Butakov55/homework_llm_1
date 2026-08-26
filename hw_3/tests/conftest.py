import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Базовый URL для всех тестов"""
    return "https://jsonplaceholder.typicode.com"

@pytest.fixture(scope="session")
def api_session():
    """Сессия requests для всех тестов"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'TestRunner/1.0'
    })
    return session