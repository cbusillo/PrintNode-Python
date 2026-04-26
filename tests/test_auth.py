import pytest

from printnodeapi.gateway import Gateway, Unauthorized

API_ADDRESS = 'https://api.printnode.com'
API_KEY = 'test-api-key'


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.headers = {'content-type': 'application/json'}

    def json(self):
        return self._payload


def test_gateway(monkeypatch):
    def fake_get(url, auth, headers, **kwargs):
        assert url == API_ADDRESS + '/whoami'
        assert auth == (API_KEY, '')
        assert headers == {}
        assert kwargs == {}
        return FakeResponse(200, {
            'id': 123,
            'firstname': 'Ada',
            'lastname': 'Lovelace',
            'email': 'ada@example.com',
            'canCreateSubAccounts': False,
            'creatorEmail': None,
            'creatorRef': None,
            'childAccounts': [],
            'credits': 0,
            'numComputers': 0,
            'totalPrints': 0,
            'versions': [],
            'connected': False,
            'tags': {},
            'state': 'active',
        })

    monkeypatch.setattr('printnodeapi.auth.requests.get', fake_get)

    gateway = Gateway(url=API_ADDRESS, apikey=API_KEY)
    assert gateway.account.firstname == 'Ada'


def test_gateway_handles_unauthentication(monkeypatch):
    def fake_get(url, auth, headers, **kwargs):
        return FakeResponse(401, {
            'code': 'BadRequest',
            'message': 'API Key not found',
        })

    monkeypatch.setattr('printnodeapi.auth.requests.get', fake_get)

    gateway = Gateway(
        url=API_ADDRESS,
        email='fake@omlet.co.uk',
        password='helloworld')
    with pytest.raises(Unauthorized):
        gateway.account
