import pytest

from printnodeapi.accounts import Accounts
from printnodeapi.model import ModelFactory


class FakeAuth:
    def __init__(self, get_responses=None):
        self.get_responses = get_responses or {}
        self.get_calls = []
        self.post_calls = []
        self.patch_calls = []
        self.delete_calls = []

    def get(self, url, request_headers=None):
        self.get_calls.append((url, request_headers))
        return self.get_responses[url]

    def post(self, url, fields=None):
        self.post_calls.append((url, fields))
        return 123

    def patch(self, url, fields=None):
        self.patch_calls.append((url, fields))
        return 123

    def delete(self, url):
        self.delete_calls.append(url)
        return True


def make_accounts(get_responses=None):
    auth = FakeAuth(get_responses)
    return Accounts(auth, ModelFactory()), auth


def client_payload(**overrides):
    payload = {
        'id': 10,
        'enabled': True,
        'edition': 'stable',
        'version': '1.2.3',
        'os': 'windows',
        'filename': 'printnode.exe',
        'filesize': 1234,
        'sha1': 'abc123',
        'releaseTimestamp': '2026-04-26T00:00:00.000Z',
        'url': 'https://example.com/printnode.exe',
    }
    payload.update(overrides)
    return payload


def test_get_clients_lists_all_clients():
    accounts, auth = make_accounts({
        '/download/clients/': [client_payload(id=10)],
    })

    clients = accounts.get_clients()

    assert auth.get_calls == [('/download/clients/', None)]
    assert clients[0].id == 10
    assert clients[0].sha_1 == 'abc123'


def test_get_clients_fetches_latest_download_for_os():
    accounts, auth = make_accounts({
        '/download/client/windows': client_payload(),
    })

    download = accounts.get_clients(os='windows')

    assert auth.get_calls == [('/download/client/windows', None)]
    assert download.os == 'windows'


def test_modify_client_downloads_requires_bool_enabled():
    accounts, _auth = make_accounts()

    with pytest.raises(ValueError, match='enabled'):
        accounts.modify_client_downloads(client_ids=10, enabled='yes')


def test_modify_client_downloads_patches_enabled_flag():
    accounts, auth = make_accounts()

    assert accounts.modify_client_downloads(client_ids=10, enabled=False) == 123
    assert auth.patch_calls == [('/download/clients/10', {'enabled': False})]


def test_create_account_posts_required_and_optional_fields():
    accounts, auth = make_accounts()

    account_id = accounts.create_account(
        firstname='Ada',
        lastname='Lovelace',
        email='ada@example.com',
        password='secret',
        creator_ref='ada-ref',
        api_keys=['key'],
        tags={'team': 'ops'},
    )

    assert account_id == 123
    assert auth.post_calls == [('/account', {
        'Account': {
            'firstname': 'Ada',
            'lastname': 'Lovelace',
            'email': 'ada@example.com',
            'password': 'secret',
            'creatorRef': 'ada-ref',
        },
        'ApiKeys': ['key'],
        'Tags': {'team': 'ops'},
    })]


def test_modify_account_requires_at_least_one_field():
    accounts, _auth = make_accounts()

    with pytest.raises(ValueError, match='No fields selected'):
        accounts.modify_account()


def test_modify_account_patches_selected_fields():
    accounts, auth = make_accounts()

    account_id = accounts.modify_account(firstname='Ada', creator_ref='ada-ref')

    assert account_id == 123
    assert auth.patch_calls == [('/account', {
        'firstname': 'Ada',
        'creatorRef': 'ada-ref',
    })]


def test_tag_and_api_key_helpers_build_expected_paths():
    accounts, auth = make_accounts({
        'account/tag/team': 'ops',
        '/account/apikey/key': {'key': 'key'},
        '/client/key/uuid?edition=stable&version=1.2.3': 'client-key',
    })

    assert accounts.get_tag('team') == 'ops'
    assert accounts.modify_tag('team', 'ops') == 123
    assert accounts.delete_tag('team') is True
    assert accounts.get_api_key('key') == {'key': 'key'}
    assert accounts.create_api_key('key') == 123
    assert accounts.delete_api_key('key') is True
    assert accounts.get_clientkey(
        uuid='uuid',
        version='1.2.3',
        edition='stable') == 'client-key'

    assert auth.get_calls == [
        ('account/tag/team', None),
        ('/account/apikey/key', None),
        (
            '/client/key/uuid?edition=stable&version=1.2.3',
            {'Content-Type': 'application/json'},
        ),
    ]
    assert auth.post_calls == [
        ('account/tag/team', 'ops'),
        ('/account/apikey/key', None),
    ]
    assert auth.delete_calls == [
        'account/tag/team',
        'account/apikey/key',
    ]
