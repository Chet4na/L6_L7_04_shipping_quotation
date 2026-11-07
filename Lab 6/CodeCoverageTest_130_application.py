
import pytest
from shipping_quote import process_shipments, monitor_container_pressures


def test_ground_shipment():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 10}]}]
    result = process_shipments(shipments, 20)
    assert result == {"total_quote": 60.0, "status": "CLEARED"}


def test_air_shipment():
    shipments = [{"manifest_approved": True, "mode": "air",
                  "packages": [{"weight_kg": 2}]}]
    result = process_shipments(shipments, 10)
    assert result["total_quote"] == 34.0


def test_unapproved_manifest():
    shipments = [{"manifest_approved": False}]
    result = process_shipments(shipments, 20)
    assert result["status"] == "NO_CARGO"


def test_invalid_shipments():
    with pytest.raises(ValueError):
        process_shipments("invalid", 10)


def test_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -1)


def test_invalid_transport_mode():
    shipments = [{"manifest_approved": True, "mode": "sea",
                  "packages": []}]
    result = process_shipments(shipments, 10)
    assert result["status"] == "NO_CARGO"


def test_invalid_package_weight():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 0}, {"weight_kg": -5}]}]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 20.0


def test_hazmat_package():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 5, "is_hazmat": True}]}]
    result = process_shipments(shipments, 10)
    assert result["total_quote"] == 60.0


def test_fragile_hazmat_package():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "is_fragile": True,
                  "packages": [{"weight_kg": 5, "is_hazmat": True}]}]
    result = process_shipments(shipments, 20)
    assert result["status"] == "NO_CARGO"


def test_heavy_package():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 31}]}]
    result = process_shipments(shipments, 10)
    assert result["total_quote"] == 196.0


def test_express_priority():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "express_priority": True,
                  "packages": [{"weight_kg": 10}]}]
    result = process_shipments(shipments, 10)
    assert result["total_quote"] == 62.5


def test_flagged_review():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 0}] * 4}]
    result = process_shipments(shipments, 20)
    assert result["status"] == "FLAGGED_REVIEW"


def test_empty_pressure_logs():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_leak_detected():
    assert monitor_container_pressures([[15.0, 13.0, 12.0]]) == "LEAK_DETECTED"


def test_stable_pressure():
    assert monitor_container_pressures([[15.0, 13.0, 15.0]]) == "STABLE"
