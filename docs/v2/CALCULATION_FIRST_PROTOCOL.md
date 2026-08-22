# Calculation-First Protocol

## Rule

**NEVER ATTEST UNTIL THE CALCULATION PATH IS PROVEN.**

## Authoritative Money

- Representation: `decimal.Decimal`
- Never Python `float` for settlement
- Explicit scale (USD = 2)
- Explicit rounding mode (default `ROUND_HALF_EVEN`)
- All intermediate results quantized before use in further arithmetic

## Canonical Equations

```
line_subtotal   = Σ quantize(unit_price × quantity)
pre_tax_total   = line_subtotal − discount + shipping + fees
grand_total     = pre_tax_total + tax
remaining_budget = budget_cap − grand_total
```

## Fail-Closed Inputs

Reject / HOLD on:

- negative unit prices or quantities
- NaN / Infinity
- malformed decimal strings
- unsupported currency
- missing required inputs
- non-finite values
- arithmetic inconsistencies
- budget overrun (policy may DENY or HOLD)
- merchant total mismatch (default tolerance = 0)
- unresolved material rule

Unknown values remain `UNKNOWN`. Never guess.

## Minor Units for Execution

Final amounts are converted to integer minor units before the rail:

```
$0.99 USD → 99
$14.25 USD → 1425
```

The execution instruction carries `grand_total_minor` and `currency`, never a float.
