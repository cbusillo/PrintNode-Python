import pytest

from printnodeapi.computers import Computers
from printnodeapi.model import ModelFactory, Printer

from tests.test_model import computer_payload, printer_payload, printjob_payload


class FakeAuth:
    def __init__(self, get_responses=None):
        self.get_responses = get_responses or {}
        self.get_calls = []
        self.post_calls = []

    def get(self, url):
        self.get_calls.append(url)
        return self.get_responses[url]

    def post(self, url, fields=None):
        self.post_calls.append((url, fields))
        return 900


def make_computers(get_responses=None):
    auth = FakeAuth(get_responses)
    return Computers(auth, ModelFactory()), auth


def test_get_computers_lists_all_with_pagination():
    computers, auth = make_computers({
        '/computers?limit=10&after=20&dir=desc': [computer_payload()],
    })

    result = computers.get_computers(limit=10, after=20, dir='desc')

    assert auth.get_calls == ['/computers?limit=10&after=20&dir=desc']
    assert [computer.name for computer in result] == ['Office Computer']


def test_get_computers_filters_by_name_after_list_query():
    computers, auth = make_computers({
        '/computers': [
            computer_payload(id=100, name='Office Computer'),
            computer_payload(id=101, name='Warehouse Computer'),
        ],
    })

    result = computers.get_computers(computer='Warehouse Computer')

    assert auth.get_calls == ['/computers']
    assert [computer.id for computer in result] == [101]


def test_get_computer_by_id_returns_single_computer():
    computers, auth = make_computers({
        '/computers/100': [computer_payload(id=100)],
    })

    result = computers.get_computers(computer=100)

    assert auth.get_calls == ['/computers/100']
    assert result.id == 100


def test_get_computer_by_id_raises_when_not_found():
    computers, _auth = make_computers({'/computers/999': []})

    with pytest.raises(LookupError, match='computer not found with ID 999'):
        computers.get_computers(computer=999)


def test_get_printers_for_computer_builds_expected_url():
    computers, auth = make_computers({
        '/computers/100/printers?limit=5': [printer_payload()],
    })

    result = computers.get_printers(computer=100, limit=5)

    assert auth.get_calls == ['/computers/100/printers?limit=5']
    assert [printer.name for printer in result] == ['Shipping Printer']


def test_get_printer_by_id_returns_single_printer():
    computers, auth = make_computers({
        '/printers/200': [printer_payload(id=200)],
    })

    result = computers.get_printers(printer=200)

    assert auth.get_calls == ['/printers/200']
    assert result.id == 200


def test_get_printjobs_lists_all_with_title_filter():
    computers, auth = make_computers({
        '/printjobs': [
            printjob_payload(id=300, title='Packing Slip'),
            printjob_payload(id=301, title='Return Label'),
        ],
    })

    result = computers.get_printjobs(printjob='Return Label')

    assert auth.get_calls == ['/printjobs']
    assert [printjob.id for printjob in result] == [301]


def test_get_printjobs_for_computer_and_named_printer_builds_printer_query():
    computers, auth = make_computers({
        '/computers/100/printers': [printer_payload(id=200)],
        '/printers/200/printjobs?limit=3': [printjob_payload(id=300)],
    })

    result = computers.get_printjobs(
        computer=100,
        printer='Shipping Printer',
        limit=3)

    assert auth.get_calls == [
        '/computers/100/printers',
        '/printers/200/printjobs?limit=3',
    ]
    assert [printjob.id for printjob in result] == [300]


def test_get_printjob_by_id_returns_single_printjob():
    computers, auth = make_computers({
        '/printjobs/300': [printjob_payload(id=300)],
    })

    result = computers.get_printjobs(printjob=300)

    assert auth.get_calls == ['/printjobs/300']
    assert result.id == 300


def test_get_states_builds_global_and_printjob_specific_paths():
    computers, auth = make_computers({
        '/printjobs/states?limit=5': [[{
            'printJobId': 300,
            'state': 'new',
            'message': None,
            'data': {},
            'clientVersion': '1.0.0',
            'createTimestamp': '2026-04-26T00:00:00.000Z',
            'age': 0,
        }]],
        '/printjobs/300/states': [[{
            'printJobId': 300,
            'state': 'done',
            'message': None,
            'data': {},
            'clientVersion': '1.0.0',
            'createTimestamp': '2026-04-26T00:00:01.000Z',
            'age': 1,
        }]],
    })

    global_states = computers.get_states(limit=5)
    printjob_states = computers.get_states(pjob_set=300)

    assert auth.get_calls == [
        '/printjobs/states?limit=5',
        '/printjobs/300/states',
    ]
    assert global_states[0][0].state == 'new'
    assert printjob_states[0][0].state == 'done'


def test_submit_printjob_encodes_binary_content_and_posts_job():
    computers, auth = make_computers({
        '/printers/200': [printer_payload(id=200)],
    })

    printjob_id = computers.submit_printjob(
        printer=200,
        job_type='pdf',
        title='Packing Slip',
        qty=2,
        options={'paper': 'Letter'},
        binary=b'PDF')

    assert printjob_id == 900
    assert auth.post_calls == [('/printjobs', {
        'printerId': 200,
        'title': 'Packing Slip',
        'contentType': 'pdf_base64',
        'content': 'UERG',
        'source': 'PythonApiClient',
        'options': {'paper': 'Letter'},
        'qty': 2,
    })]


def test_submit_printjob_reports_multiple_matching_printer_ids():
    computers, _auth = make_computers({
        '/computers/100/printers': [
            printer_payload(id=200, name='Shipping Printer'),
            printer_payload(id=201, name='Shipping Printer'),
        ],
    })

    with pytest.raises(LookupError, match='200,201'):
        computers.submit_printjob(
            computer=100,
            printer='Shipping Printer',
            uri='https://example.com/file.pdf')


@pytest.mark.parametrize('kwargs,error', [
    ({'limit': '10'}, TypeError),
    ({'after': '20'}, TypeError),
    ({'dir': 'sideways'}, TypeError),
])
def test_pagination_params_validate_inputs(kwargs, error):
    computers, _auth = make_computers()

    with pytest.raises(error):
        computers.get_computers(**kwargs)


def test_get_printer_id_accepts_printer_model_instance():
    computers, _auth = make_computers()
    printer = ModelFactory().create_printer(printer_payload(id=200))

    assert isinstance(printer, Printer)
    assert computers._get_printer_id(printer) == 200
