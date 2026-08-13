# Prompt Template — Authentication-Referral Memo

> Emitted by the `AuthenticationReferralAdvisor` guard whenever `requires_professional_referral` is true, or appended as a standing reminder otherwise.

```
# Authentication & Referral Memo

**Request ID:** {request_id}

## Standing disclaimer
{disclaimer}

## Referral required: {yes_no}

## Triggers detected
{triggers_list_or_none}

## Action required
Consult an **accredited map appraiser or cartographic-history specialist** before treating
this map as authenticated or valued. Indicators triggering this referral are listed above.

## What this skill can / cannot do
- CAN: provide research support and dating aids (technique, projection, toponymy,
  cartobibliography, provenance/materials).
- CANNOT: authenticate, appraise, value, certify, or issue a definitive judgment about
  this map or any named individual.

## Recommended next steps for the user
1. Engage an accredited map appraiser / cartographic-history specialist.
2. Supply the specialist with the evidence gathered in this report (technique,
   projection, toponyms, watermark, provenance chain).
3. Request laboratory paper/ink examination if authentication is required.
```

## Rules
- The memo is appended unconditionally by the router guard; it is never silent.
- In strict mode, a request to drop the disclaimer is refused and recorded.
