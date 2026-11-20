import io
import json
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.tool_auth import protect_api, verify_access, TOOL_KEY


def response(payload):
    return io.BytesIO(json.dumps(payload).encode())


@pytest.mark.parametrize('header', [None, '', 'Basic abc', 'Bearer '])
def test_missing_bearer_never_calls_authority(header):
    with patch('app.tool_auth.urlopen') as call:
        assert verify_access(header)[0] == 401
        call.assert_not_called()


def test_only_exact_tool_scoped_grant_is_accepted():
    for payload, status in [({'active': True, 'tool': TOOL_KEY}, 200),
                            ({'active': True, 'tool': 'another_tool'}, 403),
                            ({'active': False, 'tool': TOOL_KEY}, 403),
                            ({'active': 'true', 'tool': TOOL_KEY}, 403)]:
        with patch('app.tool_auth.urlopen', return_value=response(payload)):
            assert verify_access('Bearer user-session')[0] == status


@pytest.mark.parametrize('status', [401, 403, 500])
def test_authority_denial_is_preserved_and_failure_is_closed(status):
    with patch('app.tool_auth.urlopen', side_effect=HTTPError('https://authority', status, '', {}, None)):
        assert verify_access('Bearer invalid-or-expired')[0] == (status if status in (401, 403) else 503)


def test_unavailable_authority_does_not_grant_access():
    with patch('app.tool_auth.urlopen', side_effect=URLError('unavailable')):
        assert verify_access('Bearer user-session')[0] == 503


def test_middleware_blocks_all_direct_api_routes_before_handler():
    app = FastAPI()
    app.middleware('http')(protect_api)
    reached = []

    @app.api_route('/api/v1/{path:path}', methods=['GET', 'POST'])
    def execute(path: str):
        reached.append(path)
        return {'ok': True}

    client = TestClient(app)
    for path in ['calculations', 'reports/preview', 'reports/pdf', 'catalog/options', 'capabilities']:
        assert client.post('/api/v1/' + path).status_code == 401
        assert client.get('/api/v1/' + path).status_code == 401
    assert reached == []
    with patch('app.tool_auth.urlopen', return_value=response({'active': True, 'tool': TOOL_KEY})):
        result = client.post('/api/v1/calculations', headers={'Authorization': 'Bearer verified'})
    assert result.status_code == 200
    assert result.headers['cache-control'] == 'private, no-store'
    assert reached == ['calculations']
