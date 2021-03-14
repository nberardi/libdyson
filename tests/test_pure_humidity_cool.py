"""Tests for Dyson Pure Humidity+Cool device."""

import pytest

from libdyson import (
    DEVICE_TYPE_PURE_HUMIDITY_COOL,
    DysonPureHumidityCool,
    HumidityOscillationMode,
    WaterHardness,
)

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command
from .test_pure_cool_link import ENVIRONMENTAL_DATA  # noqa: F401

DEVICE_TYPE = DEVICE_TYPE_PURE_HUMIDITY_COOL

STATUS = {
    "product-state": {
        "oson": "ON",
        "ancp": "BRZE",
        "hume": "HUMD",
        "haut": "ON",
        "humt": "0050",
        "rect": "0080",
        "wath": "2025",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Hot+Cool Link."""
    device = DysonPureHumidityCool(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    assert device.oscillation is True
    assert device.oscillation_angle == HumidityOscillationMode.BREEZE
    assert device.humidification is True
    assert device.humidification_auto_mode is True
    assert device.humidity_target == 50
    assert device.auto_humidity_target == 80
    assert device.water_hardness == WaterHardness.SOFT

    new_status = {
        "product-state": {
            "oson": ["ON", "OFF"],
            "ancp": ["BRZE", "0045"],
            "hume": ["HUMD", "OFF"],
            "haut": ["ON", "OFF"],
            "humt": ["0050", "0030"],
            "rect": ["0080", "0050"],
            "wath": ["2025", "0675"],
        }
    }
    mqtt_client.state_change(new_status)
    assert device.oscillation is False
    assert device.oscillation_angle == HumidityOscillationMode.DEGREE_45
    assert device.humidification is False
    assert device.humidification_auto_mode is False
    assert device.humidity_target == 30
    assert device.auto_humidity_target == 50
    assert device.water_hardness == WaterHardness.HARD


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("enable_oscillation", [], {"oson": "ON", "fpwr": "ON", "ancp": "BRZE"}),
        (
            "enable_oscillation",
            [HumidityOscillationMode.DEGREE_45],
            {"oson": "ON", "fpwr": "ON", "ancp": "0045"},
        ),
        (
            "enable_oscillation",
            [HumidityOscillationMode.DEGREE_90],
            {"oson": "ON", "fpwr": "ON", "ancp": "0090"},
        ),
        (
            "enable_oscillation",
            [HumidityOscillationMode.BREEZE],
            {"oson": "ON", "fpwr": "ON", "ancp": "BRZE"},
        ),
        ("disable_oscillation", [], {"oson": "OFF"}),
        ("enable_humidification", [], {"hume": "HUMD"}),
        ("disable_humidification", [], {"hume": "OFF"}),
        ("enable_humidification_auto_mode", [], {"haut": "ON"}),
        ("disable_humidification_auto_mode", [], {"haut": "OFF"}),
        ("set_humidity_target", [50], {"humt": "0050"}),
        ("set_water_hardness", [WaterHardness.SOFT], {"wath": "2025"}),
        ("set_water_hardness", [WaterHardness.MEDIUM], {"wath": "1350"}),
        ("set_water_hardness", [WaterHardness.HARD], {"wath": "0675"}),
    ],
)
def test_command(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of Pure Hot+Cool Link."""
    assert_command(
        DysonPureHumidityCool(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )