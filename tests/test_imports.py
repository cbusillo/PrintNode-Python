def test_preferred_and_legacy_gateway_imports_match():
    from printnode_api import Gateway
    from printnode_api.gateway import Gateway as GatewayFromPreferredModule
    from printnodeapi import Gateway as LegacyGateway
    from printnodeapi.gateway import Gateway as GatewayFromLegacyModule

    assert Gateway is GatewayFromPreferredModule
    assert Gateway is LegacyGateway
    assert Gateway is GatewayFromLegacyModule


def test_preferred_submodules_reexport_legacy_objects():
    from printnode_api.auth import Unauthorized
    from printnode_api.model import ModelFactory
    from printnode_api.util import camel_to_underscore
    from printnodeapi.auth import Unauthorized as LegacyUnauthorized
    from printnodeapi.model import ModelFactory as LegacyModelFactory
    from printnodeapi.util import camel_to_underscore as legacy_camel_to_underscore

    assert Unauthorized is LegacyUnauthorized
    assert ModelFactory is LegacyModelFactory
    assert camel_to_underscore is legacy_camel_to_underscore
