def test_gateway_imports_from_single_namespace():
    from printnode_community import Gateway
    from printnode_community.gateway import Gateway as GatewayFromModule

    assert Gateway is GatewayFromModule


def test_submodules_export_expected_objects():
    from printnode_community.auth import Unauthorized
    from printnode_community.model import ModelFactory
    from printnode_community.util import camel_to_underscore

    assert Unauthorized.__name__ == 'Unauthorized'
    assert ModelFactory.__name__ == 'ModelFactory'
    assert camel_to_underscore('HelloWorld') == 'hello_world'
