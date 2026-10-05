from app.services.risk_engine import RiskEngine

def test_signal_classification_levels():
    cls_map = RiskEngine.SIGNAL_CLASSIFICATION

    assert cls_map["CANVAS"]["level"] == "HIGH"
    assert cls_map["WEBGL"]["level"] == "HIGH"
    assert cls_map["AUDIO"]["level"] == "HIGH"

    assert cls_map["FONTS"]["level"] == "MEDIUM"
    assert cls_map["MEDIA_DEVICES"]["level"] == "MEDIUM"
    assert cls_map["HARDWARE"]["level"] == "MEDIUM"
    assert cls_map["NAVIGATOR"]["level"] == "MEDIUM"

    assert cls_map["SCREEN"]["level"] == "LOW"
    assert cls_map["TIMEZONE"]["level"] == "LOW"

    for signal_name, conf in cls_map.items():
        assert "reason" in conf
        assert len(conf["reason"]) > 10
        assert conf["max_impact"] > 0
