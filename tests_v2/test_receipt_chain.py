"""Receipt chain integrity."""

from bopcart_v2.receipt import create_receipt, verify_chain


def test_chain_intact():
    r1 = create_receipt(
        intent_id="i1",
        rule_pack_id="R",
        rule_pack_version="2",
        input_digest="sha256:a",
        cart_digest="sha256:b",
        calculation_digest="sha256:c",
        authorization_digest="sha256:d",
        execution_instruction_digest="sha256:e",
        external_transaction_reference="tx1",
        execution_status="SUCCESS",
        currency="USD",
        grand_total_minor=99,
    )
    r2 = create_receipt(
        intent_id="i1",
        rule_pack_id="R",
        rule_pack_version="2",
        input_digest="sha256:a",
        cart_digest="sha256:b",
        calculation_digest="sha256:c",
        authorization_digest="sha256:d",
        execution_instruction_digest="sha256:e",
        external_transaction_reference="tx2",
        execution_status="SUCCESS",
        currency="USD",
        grand_total_minor=99,
        previous_receipt_digest=r1.receipt_digest,
    )
    assert verify_chain([r1, r2]) is None


def test_tampered_receipt_breaks_chain():
    r1 = create_receipt(
        intent_id="i1",
        rule_pack_id="R",
        rule_pack_version="2",
        input_digest="sha256:a",
        cart_digest="sha256:b",
        calculation_digest="sha256:c",
        authorization_digest="sha256:d",
        execution_instruction_digest="sha256:e",
        external_transaction_reference="tx1",
        execution_status="SUCCESS",
        currency="USD",
        grand_total_minor=99,
    )
    # Tamper by changing digest after creation
    r1_tampered = r1.model_copy(update={"receipt_digest": "sha256:deadbeef"})
    assert verify_chain([r1_tampered]) == 0
