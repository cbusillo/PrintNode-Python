def test_gateway_imports_from_single_namespace():
    from printnode_api import Gateway
    from printnode_api.gateway import Gateway as GatewayFromModule

    assert Gateway is GatewayFromModule


def test_submodules_export_expected_objects():
    from printnode_api.auth import Unauthorized
    from printnode_api.model import ModelFactory
    from printnode_api.util import camel_to_underscore

    assert Unauthorized.__name__ == 'Unauthorized'
    assert ModelFactory.__name__ == 'ModelFactory'
    assert camel_to_underscore('HelloWorld') == 'hello_world'
