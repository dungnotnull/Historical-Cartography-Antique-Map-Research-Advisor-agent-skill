# Reference — Authentication & Professional-Referral Policy

> Distilled from IMCoS (2020) *Guidelines on Map Authentication and Valuation* and the standing disclaimer policy in `CLAUDE.md` / `PROJECT-detail.md` §4. Enforced by the always-on `AuthenticationReferralAdvisor`.

## Standing disclaimer (applies to EVERY substantive response)
> This analysis is general, educational, and analytical information about historical cartography; it is **not** a certified authentication, appraisal, or valuation. Formal authentication or valuation of a significant antique map must be verified by an **accredited map appraiser or cartographic-history specialist**. Do not make financial or collecting decisions solely on this output.

## When referral is REQUIRED (triggers)
The `AuthenticationReferralAdvisor` sets `requires_professional_referral = True` whenever the request shows:
- Authentication intent: "is it genuine / authentic / a forgery / real / original"
- Valuation intent: "value / worth / appraisal / insure / invest / sell"
- Certification intent: "certificate / certified / guaranteed"
- Significance markers: "significant / rare / expensive / museum / donate"

Even **without** such intent, the standing disclaimer still attaches to every substantive response.

## Strict-mode behaviour
In `strict_disclaimer_mode` (default `True`), a user request to *drop* the disclaimer is **refused** and recorded as a `DisclaimerViolation`; the disclaimer is still attached to the output. The guard is never silenced.

## What this skill CAN do vs what it CANNOT
- **Can**: research support, dating *aids* (technique, projection, toponymy, cartobibliography, provenance/materials), structured reasoning, methodology checklists.
- **Cannot**: authenticate, appraise, value, certify, or produce a definitive judgment about a specific map or named third party.

## Out of scope (guardrails)
- Never present output as a certified/professional determination.
- Do not produce a definitive judgment about a named individual.
- Always flag when an accredited professional must be consulted.
