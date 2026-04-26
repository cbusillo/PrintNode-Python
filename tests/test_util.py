import pytest

from printnode_api import util


@pytest.mark.parametrize('expected,input', [
    ('hello_world', 'HelloWorld')])
def test_camel_to_underscore(expected, input):
    assert expected == util.camel_to_underscore(input)
