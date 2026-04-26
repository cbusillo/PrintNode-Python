from printnode_community.model import (
    Account,
    Capabilities,
    Computer,
    ModelFactory,
    PrintJob,
    safe_tuple_populate,
)


def computer_payload(**overrides):
    payload = {
        'id': 100,
        'name': 'Office Computer',
        'inet': '192.0.2.1',
        'inet6': '2001:db8::1',
        'hostname': 'office-host',
        'version': '1.0.0',
        'createTimestamp': '2026-04-26T00:00:00.000Z',
        'state': 'connected',
        'jre': 'ignored by model',
        'unexpected': 'ignored',
    }
    payload.update(overrides)
    return payload


def printer_payload(**overrides):
    payload = {
        'id': 200,
        'computer': computer_payload(),
        'name': 'Shipping Printer',
        'description': 'Thermal label printer',
        'capabilities': {
            'bins': [],
            'collate': True,
            'copies': 99,
            'color': False,
            'dpis': [203],
            'duplex': False,
            'extent': [],
            'medias': [],
            'nup': [],
            'papers': [],
            'printrate': None,
            'supportsCustomPaperSize': True,
        },
        'default': True,
        'createTimestamp': '2026-04-26T00:00:00.000Z',
        'state': 'online',
    }
    payload.update(overrides)
    return payload


def printjob_payload(**overrides):
    payload = {
        'id': 300,
        'printer': printer_payload(),
        'title': 'Packing Slip',
        'contentType': 'pdf_uri',
        'source': 'PythonApiClient',
        'expireAt': None,
        'createTimestamp': '2026-04-26T00:00:00.000Z',
        'state': 'new',
    }
    payload.update(overrides)
    return payload


def test_safe_tuple_populate_ignores_extra_fields_and_defaults_missing_fields():
    fields = {
        'id': 123,
        'firstname': 'Ada',
        'lastname': 'Lovelace',
        'email': 'ada@example.com',
        'extra': 'ignored',
    }

    account = safe_tuple_populate(Account, fields, defaults={
        'can_create_sub_accounts': False,
        'creator_email': None,
        'creator_ref': None,
        'child_accounts': [],
        'credits': 0,
        'num_computers': 0,
        'total_prints': 0,
        'versions': [],
        'connected': False,
        'tags': {},
        'state': 'active',
        'api_keys': [],
        'permissions': [],
    })

    assert account.firstname == 'Ada'
    assert account.can_create_sub_accounts is False
    assert not hasattr(account, 'extra')


def test_create_account_defaults_optional_collections():
    account = ModelFactory().create_account({
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

    assert account.api_keys == []
    assert account.permissions == []


def test_create_computer_maps_camel_case_and_ignores_jre():
    computer = ModelFactory().create_computer(computer_payload())

    assert isinstance(computer, Computer)
    assert computer.create_timestamp == '2026-04-26T00:00:00.000Z'
    assert computer.inet6 == '2001:db8::1'
    assert not hasattr(computer, 'jre')


def test_create_computer_defaults_missing_optional_network_fields():
    payload = computer_payload()
    del payload['jre']
    del payload['inet6']

    computer = ModelFactory().create_computer(payload)

    assert isinstance(computer, Computer)
    assert computer.inet6 is None


def test_create_printer_builds_nested_computer_and_capabilities():
    printer = ModelFactory().create_printer(printer_payload())

    assert printer.computer.name == 'Office Computer'
    assert isinstance(printer.capabilities, Capabilities)
    assert printer.capabilities.supports_custom_paper_size is True


def test_create_printer_defaults_missing_optional_nested_fields():
    payload = printer_payload()
    del payload['computer']
    del payload['capabilities']

    printer = ModelFactory().create_printer(payload)

    assert printer.computer is None
    assert printer.capabilities is None


def test_create_printer_preserves_null_nested_fields():
    printer = ModelFactory().create_printer(printer_payload(
        computer=None,
        capabilities=None,
    ))

    assert printer.computer is None
    assert printer.capabilities is None


def test_create_printjob_defaults_optional_fields():
    printjob = ModelFactory().create_printjob(printjob_payload())

    assert isinstance(printjob, PrintJob)
    assert printjob.content is None
    assert printjob.pages is None
    assert printjob.qty == 1
    assert printjob.options == {}


def test_create_printjob_defaults_missing_printer():
    payload = printjob_payload()
    del payload['printer']

    printjob = ModelFactory().create_printjob(payload)

    assert printjob.printer is None


def test_create_printjob_preserves_server_supplied_optional_fields():
    printjob = ModelFactory().create_printjob(printjob_payload(
        content='https://example.com/file.pdf',
        pages=4,
        qty=2,
        options={'paper': 'Letter'},
    ))

    assert printjob.content == 'https://example.com/file.pdf'
    assert printjob.pages == 4
    assert printjob.qty == 2
    assert printjob.options == {'paper': 'Letter'}
