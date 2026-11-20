import pytest

@pytest.fixture(autouse=True)
def isolate_engine_tests(request, monkeypatch):
    if request.node.path.name != "test_tool_auth.py":
        monkeypatch.setattr("app.tool_auth.verify_access", lambda _: (200, "authorized-test-fixture"))
