"""The tests for the Ring switch platform."""
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN

from .common import setup_platform

from tests.common import load_fixture


async def test_entity_registry(hass, requests_mock):
    """Tests that the devices are registed in the entity registry."""
    await setup_platform(hass, SWITCH_DOMAIN)
    entity_registry = await hass.helpers.entity_registry.async_get_registry()

    entry = entity_registry.async_get("switch.front_siren")
    assert entry.unique_id == "aacdef123-siren"

    entry = entity_registry.async_get("switch.internal_siren")
    assert entry.unique_id == "aacdef124-siren"


async def test_siren_off_reports_correctly(hass, requests_mock):
    """Tests that the initial state of a device that should be off is correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get("switch.front_siren")
    assert state.state == "off"
    assert state.attributes.get("friendly_name") == "Front siren"


async def test_siren_on_reports_correctly(hass, requests_mock):
    """Tests that the initial state of a device that should be on is correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get("switch.internal_siren")
    assert state.state == "on"
    assert state.attributes.get("friendly_name") == "Internal siren"
    assert state.attributes.get("icon") == "mdi:alarm-bell"


async def test_siren_can_be_turned_on(hass, requests_mock):
    """Tests the siren turns on correctly."""
    await setup_platform(hass, SWITCH_DOMAIN)

    # Mocks the response for turning a siren on
    requests_mock.put(
        "https://api.ring.com/clients_api/doorbots/987652/siren_on",
        text=load_fixture("ring_doorbot_siren_on_response.json"),
    )

    state = hass.states.get("switch.front_siren")
    assert state.state == "off"

    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": "switch.front_siren"}, blocking=True
    )

    await hass.async_block_till_done()
    state = hass.states.get("switch.front_siren")
    assert state.state == "on"


async def test_updates_work(hass, requests_mock):
    """Tests the update service works correctly."""
    await setup_platform(hass, SWITCH_DOMAIN)
    state = hass.states.get("switch.front_siren")
    assert state.state == "off"
    # Changes the return to indicate that the siren is now on.
    requests_mock.get(
        "https://api.ring.com/clients_api/ring_devices",
        text=load_fixture("ring_devices_updated.json"),
    )

    await hass.services.async_call("ring", "update", {}, blocking=True)

    await hass.async_block_till_done()

    state = hass.states.get("switch.front_siren")
    assert state.state == "on"
