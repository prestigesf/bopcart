# Payment / Procurement Rail Boundary

The rail is deliberately dumb.

```
VERIFIED INSTRUCTION IN
        ↓
EXECUTE EXACTLY ONCE
        ↓
EXECUTION RESULT
```

## The Adapter Must Not

- choose product
- choose merchant
- calculate unit price, quantity, subtotal, tax, shipping, fees, or final total
- change budget
- infer authorization
- change cart
- substitute merchant or amount
- silently execute a new price
- execute twice on retry

## Execution-Time Price Check

Immediately before external execution, revalidate the live merchant total.  
If it differs from the authorized calculated total → HOLD and return to COMPUTE.

Stale authorization must not float across a price change.
