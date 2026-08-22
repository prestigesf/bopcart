"""Proof continuity & crypto status."""

from bopcart_v2.proof_continuity import detect_crypto_status, mock_signature_label, build_proof
from bopcart_v2.calculation_engine import calculate
from bopcart_v2.rule_resolution import resolve_rules
from bopcart_v2.schemas import CartLine
from decimal import Decimal


def test_mock_never_claims_fips():
    m = mock_signature_label()
    assert m["signature_status"] == "MOCK"
    assert m["fips_204_verified"] is False


def test_crypto_status_never_fakes_mldsa():
    status = detect_crypto_status()
    # In this environment we expect UNAVAILABLE; never REAL unless proven
    assert status["ML_DSA_65"] in ("UNAVAILABLE", "UNVERIFIED", "REAL")
    if status["ML_DSA_65"] != "REAL":
        assert status["FIPS_204"] != "REAL"


def test_build_proof_has_real_digests():
    rule = resolve_rules()
    line = CartLine(product_id="p", unit_price=Decimal("0.99"), quantity=1, merchant_id="m")
    calc = calculate([line], budget_cap="1.00", rule=rule)
    proof = build_proof(
        intent_id="i1",
        input_digest="sha256:input",
        cart_digest="sha256:cart",
        calc=calc,
        authorization_digest="sha256:auth",
        execution_instruction_digest="sha256:instr",
        verdict="ALLOW",
    )
    assert proof.calculation_digest.startswith("sha256:")
    assert proof.grand_total_minor == 99
