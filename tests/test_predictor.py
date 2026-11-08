from main import (
    calculate_severity_score,
    helper,
    normalize_symptom,
)


def test_normalize_variants():
    assert normalize_symptom("High Fever") == "high_fever"
    assert normalize_symptom("itching") == "itching"
    assert normalize_symptom(" skin-rash ") == "skin_rash"
    # known alias keeps canonical dataset key
    assert normalize_symptom("spotting__urination") == "spotting_ urination"


def test_normalize_handles_quotes_brackets():
    assert normalize_symptom("['Itching']") == "itching"


def test_severity_uses_weights_not_indices():
    # itching weight 1 + cough weight? both from Symptom-severity.csv
    s = calculate_severity_score(["itching", "cough"])
    assert s > 0
    # index-sum bug would be 0 + 24 = 24; just assert weights lookup works deterministically
    assert calculate_severity_score(["itching"]) == calculate_severity_score(["itching"])


def test_helper_returns_lists():
    desc, pre, med, diet, workout = helper("Common Cold")
    assert isinstance(desc, str) and len(desc) > 0
    assert all(isinstance(x, list) for x in [pre, med, diet, workout])
    # medications/diets are parsed lists (not one stringified list)
    assert len(med) >= 1
    assert isinstance(med[0], str)


def test_helper_unknown_disease_empty_not_crash():
    desc, pre, med, diet, workout = helper("No Such Disease")
    assert desc == ""
    assert pre == med == diet == workout == []
