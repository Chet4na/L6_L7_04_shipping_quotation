
import pytest
from shipping_quote import process_shipments, monitor_container_pressures


def test_empty_shipments():
    assert process_shipments([], 10) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_invalid_shipments_type():
    with pytest.raises(ValueError):
        process_shipments("invalid", 10)


def test_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -1)


def test_unapproved_manifest():
    shipments = [{"manifest_approved": False}]
    assert process_shipments(shipments, 10)["status"] == "NO_CARGO"


def test_ground_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 10}]
    }]
    result = process_shipments(shipments, 10)
    assert result["total_quote"] == 50.0
    assert result["status"] == "CLEARED"


def test_air_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "air",
        "packages": [{"weight_kg": 2}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 34.0


def test_invalid_transport_mode():
    shipments = [{
        "manifest_approved": True,
        "mode": "sea",
        "packages": []
    }]
    assert process_shipments(shipments, 10)["status"] == "NO_CARGO"


def test_empty_packages():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": []
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 10.0


def test_zero_and_negative_weights():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0},
            {"weight_kg": -5}
        ]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 10.0


def test_normal_weight():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 10}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 50.0


def test_weight_exactly_30():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 30}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 130.0


def test_heavy_weight_above_30():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 31}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 196.0


def test_non_fragile_hazmat():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": False,
        "packages": [{"weight_kg": 5, "is_hazmat": True}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 60.0


def test_fragile_hazmat():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": True,
        "packages": [{"weight_kg": 5, "is_hazmat": True}]
    }]
    assert process_shipments(shipments, 10)["status"] == "NO_CARGO"


def test_express_priority_enabled():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": True,
        "packages": [{"weight_kg": 10}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 62.5


def test_express_priority_disabled():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": False,
        "packages": [{"weight_kg": 10}]
    }]
    assert process_shipments(shipments, 10)["total_quote"] == 50.0


def test_exactly_three_rejected_parcels():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 0}] * 3
    }]
    assert process_shipments(shipments, 10)["status"] == "CLEARED"


def test_more_than_three_rejected_parcels():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 0}] * 4
    }]
    assert process_shipments(shipments, 10)["status"] == "FLAGGED_REVIEW"


def test_empty_pressure_logs():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_empty_container():
    assert monitor_container_pressures([[]]) == "STABLE"


def test_single_safe_pressure():
    assert monitor_container_pressures([[15.0]]) == "STABLE"


def test_pressure_recovery_resets_streak():
    assert monitor_container_pressures([[13.0, 15.0, 13.0]]) == "STABLE"


def test_leak_detected():
    assert monitor_container_pressures([[13.0, 12.0]]) == "LEAK_DETECTED"


def test_separate_containers():
    assert monitor_container_pressures([[13.0], [12.0]]) == "STABLE"
