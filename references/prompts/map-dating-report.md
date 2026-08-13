# Prompt Template — Map-Dating Research Report

> Used by sub-advisors when synthesising a map-dating report. Fill the bracketed fields from tool outputs and advisor findings. Always append the standing disclaimer and, when triggered, the referral block.

## Template

```
# Map-Dating Research Report

**Request ID:** {request_id}
**Disclaimer:** {disclaimer}

## 1. Subject & observed evidence
- **Observed technique cues:** {technique_cues}
- **Observed visual features:** {observed_features}
- **Projection stated/inferred:** {projection}
- **Place-names on map:** {toponyms}
- **Watermark/material notes:** {watermark}, {material_notes}
- **Imprint/maker cues:** {maker_cues}

## 2. Dating axes (each named with its methodology)

### 2.1 Print-technique dating [methodology: print-technique dating]
- Technique: {technique} — dominant window {date_range}
- Terminus post quem: {tpq_technique}
- Confidence: {confidence_technique}

### 2.2 Projection history [methodology: history of map projections]
- Projection: {projection} — invented {invented} by {inventor}
- Terminus post quem: {tpq_projection}
- Year consistency check: {consistency}
- Confidence: {confidence_projection}

### 2.3 Toponymy / boundary history [methodology: historical toponymy]
- Dated toponym signals: {toponym_signals}
- Terminus post quem / ante quem: {tpq_toponym}
- Confidence: {confidence_toponym}

### 2.4 Cartobibliography [methodology: cartobibliography]
- Maker/edition candidate: {maker} (active {active})
- State/edition note: {state_edition_note}
- Confidence: {confidence_carto}

### 2.5 Provenance / materials [methodology: provenance + material analysis]
- Watermark: {watermark} — {wm_date_range} ({wm_origin})
- Paper fibre/type: {paper_type}
- Confidence: {confidence_provenance}

## 3. Convergent date estimate
- **Earliest possible (most restrictive TPQ):** {earliest}
- **Latest possible (TAQ / dominance window end):** {latest}
- **Most likely window:** {likely_window}
- **Confidence:** {overall_confidence} (low | medium | high)

## 4. Methodologies applied
{methodologies_list}

## 5. References used
{references_list}

## 6. Professional referral
{referral_block_or_none}
```

## Rules for use
- Name the methodology in every section header (auditable reasoning, not just conclusions).
- State TPQ/TAQ explicitly per axis; combine to a convergent window.
- Never omit the disclaimer; append the referral block whenever `requires_professional_referral` is true.
- Confidence = low/medium/high based on number of agreeing axes.
