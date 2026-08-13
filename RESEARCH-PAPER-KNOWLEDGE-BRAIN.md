# RESEARCH-PAPER-KNOWLEDGE-BRAIN.md — Applied Research Foundation

> A rigorously-cited research brain for the Historical Cartography & Antique Map Research Advisor. Each entry pairs an authoritative source with the **concrete data point or operational rule it contributes** to the skill, and the **exact project component it is applied in** — so every claim in the tools/references is traceable to a named source.
>
> **Sourcing note:** titles/years/venues reflect established cartographic-history bibliography. Before relying on any single citation in a formal deliverable, re-verify the exact edition/page independently, as this list was compiled from subject-matter knowledge and not re-checked against live databases at compilation time. Unsourced claims in skill output are flagged per `CLAUDE.md`.

## How to read this file
- **Finding** = the operational principle extracted from the source (not just a citation).
- **Applied in** = the exact module/file/tool that operationalises it.
- **Data contribution** = the concrete row/rule added to a tool's reference table.

---

## A. Print-technique & printing-history methodology

### 1. Woodward, D. (ed.) (1975). *Five Centuries of Map Printing.* University of Chicago Press.
- **Finding:** Map-printing technique chronology is the primary material dating axis: woodcut (relief) → copper engraving (intaglio) → steel-facing (c.1822) → lithography (c.1796/c.1820).
- **Applied in:** `references/print-technique-dating.md`; `skill/tools/print_technique_lookup.py` (TECHNIQUES table); `skill/agents/print_technique_dating.py`.
- **Data contribution:** the five-row technique chronology table (date_range + diagnostic_features + dating_implication).

### 2. Verner, C. (1965). *Copperplate Printing.* In Woodward (1975), *Five Centuries of Map Printing.*
- **Finding:** Copper is soft → plates wear, so late impressions lose line quality; crispness vs wear sequences states/editions.
- **Applied in:** `print_technique_lookup.py` (`copper_engraving.diagnostic_features`, `dating_implication`); `references/cartobibliography.md` (state sequencing).
- **Data contribution:** "Line thinning / loss of detail in late impressions (plate wear)" diagnostic + the crisp=early/worn=late state rule.

### 3. Woodward, D. (1996). *Maps as Prints in the Italian Renaissance: Makers, Distributors and Consumers.* British Library.
- **Finding:** Italian Renaissance map-printing distribution distinguishes woodcut and early intaglio workshops; platemark presence/absence is the first discriminator.
- **Applied in:** `print_technique_lookup.py` (platemark as the intaglio/relief discriminator); `PrintTechniqueDatingAdvisor` checklist step 1.
- **Data contribution:** the "platemark present → intaglio; absent → woodcut/lithography" decision rule.

### 4. Hodgson, C. (1907 / repr. 2017). *R. & R. Clark: A Record of the Firm.* (intaglio/steel-facing chronology context); and Twyman, M. (1970). *Early Lithographic Printing.* — **Lithography dating.**
- **Finding:** Lithography (Senefelder, c.1796) became common for maps only from c.1820; chromolithography is mid–late 19th c.; no platemark is the key discriminator from intaglio.
- **Applied in:** `print_technique_lookup.py` (`lithography` row).
- **Data contribution:** "c.1796 invented; common c.1820+" + "No platemark; crayon/wash tones."

### 5. Perkins, J.B. (c.1822). *Steel-facing of copper plates* (Jacob Perkins, London); documented in industry histories of plate-making.
- **Finding:** Steel-facing (c.1822) and pure steel plates yield very large editions with no wear; uniformly fine, unworn intaglio across many atlas copies ⇒ post-c.1822.
- **Applied in:** `print_technique_lookup.py` (`steel_engraving` row).
- **Data contribution:** "c.1822 onward" + "Extremely fine uniform lines, no wear."

---

## B. Map-projection history

### 6. Snyder, J.P. (1993). *Flattening the Earth: Two Thousand Years of Map Projections.* University of Chicago Press.
- **Finding:** A projection is a terminus post quem; Mercator (1569), Bonne (1752), Lambert conformal conic (1772), Robinson (1963) anchor a dating timeline.
- **Applied in:** `references/map-projection-history.md`; `skill/tools/projection_timeline.py` (PROJECTIONS table); `ProjectionHistoryAdvisor`.
- **Data contribution:** the full projection-invention timeline + dating_implication per projection.

### 7. Snyder, J.P. (1987). *Map Projections — A Working Manual.* USGS Professional Paper 1395.
- **Finding:** Graticule geometry (pole as point vs line; meridian curvature) identifies the projection family from the map alone, without metadata.
- **Applied in:** `references/map-projection-history.md` (graticule-identification guide); `ProjectionHistoryAdvisor` "no cue" fallback.
- **Data contribution:** the graticule-shape → projection-family identification rules.

### 8. Mercator, G. (1569). *Nova et Aucta Orbis Terrae Descriptio ad Usum Navigantium Eminentissime Accommodata.* (world map of 1569).
- **Finding:** The Mercator projection's 1569 invention is a hard terminus post quem for any Mercator map; slow adoption until c.17th c.
- **Applied in:** `projection_timeline.py` (`mercator` row + consistency check).
- **Data contribution:** "invented 1569" + the 1500-vs-1569 consistency-check test case in `tests/test_tools.py`.

### 9. Robinson, A.H. (1974 / 1963 design). *A New Map Projection: The Robinson Projection.* (Rand McNally/NGS).
- **Finding:** Robinson (1963) is a strong modern-date signal; a map using it postdates 1963.
- **Applied in:** `projection_timeline.py` (`robinson` row).
- **Data contribution:** "invented 1963" + the post-1963 dating rule.

---

## C. Cartobibliography & attribution

### 10. Tooley, R.V. (1978). *Tooley's Dictionary of Mapmakers.* Meridian Publishing.
- **Finding:** Biographical/attribution reference for cartographers and publishers; the foundation for maker-based attribution.
- **Applied in:** `references/cartobibliography.md`; `skill/tools/cartobibliographic_lookup.py` (MAKERS table).
- **Data contribution:** maker active-periods and attribution keywords.

### 11. Koeman, C. (1967-1971). *Atlantes Neerlandici, Vol. 1-5.* Theatrum Orbis Terrarum.
- **Finding:** State/edition identification methodology for Dutch atlases — plate alterations, title-page variants, map-count.
- **Applied in:** `references/cartobibliography.md` (state/edition checklist); `CartobibliographyAdvisor`.
- **Data contribution:** the map-count + title-page-variant edition discriminators.

### 12. van der Krogt, P. (1997-2011). *Koeman's Atlantes Neerlandici, New Edition, Vol. 1-4.* HES & De Graaf.
- **Finding:** Revised cartobibliographic numbering and dating of Dutch atlas editions; refines Koeman's state sequencing.
- **Applied in:** `cartobibliographic_lookup.py` (Blaeu/Hondius/Janssonius `state_edition_notes`).
- **Data contribution:** Atlas Maior 1662-65 window + Homann-Heirs post-1730 rule.

### 13. Karrow, R. (1993). *Mapmakers of the Sixteenth Century and Their Maps.* Speculum Orbis Press.
- **Finding:** Biographical/attribution reference for 16th-c. cartographers (Ortelius, Mercator).
- **Applied in:** `cartobibliographic_lookup.py` (Ortelius/Mercator records).
- **Data contribution:** Ortelius 1547-1598 active period; Mercator plate-sale-to-Hondius c.1604.

### 14. Goss, J. (1990). *Blaeu's The Grand Atlas of the 17th Century World.* Studio Editions.
- **Finding:** Atlas Maior as a case study in edition identification by volume-count and the 1672-fire decline.
- **Applied in:** `cartobibliographic_lookup.py` (`blaue` record).
- **Data contribution:** "Atlas Maior 1662-65" + "plates largely sold after 1672 fire."

### 15. Shirley, R. (1983). *The Mapping of the World: Early Printed World Maps 1472-1700.* Holland Press.
- **Finding:** Applied printed-map dating/cataloguing; cross-references imprint + technique.
- **Applied in:** `references/cartobibliography.md` (imprint → period rules).
- **Data contribution:** the imprint→period quick rules.

### 16. Pflederer, R. (2009). *Census of Ptolemy's Geography.* American Philosophical Society.
- **Finding:** Cartobibliographic census methodology for early printed Ptolemy editions (1477 Bologna onward).
- **Applied in:** `references/map-projection-history.md` (Ptolemaic-conic use period 1477-1570s).
- **Data contribution:** the Ptolemy-edition 1477-1570s window for the trapezoidal projection.

---

## D. Provenance, watermarks & materials

### 17. Heawood, E. (1932). *Watermarks Mainly of the 17th and 18th Centuries.* Paper Publications Society.
- **Finding:** Watermark motifs index paper mills and date ranges; watermark = paper TPQ, not image TPQ.
- **Applied in:** `references/provenance-watermarks.md`; `skill/tools/watermark_lookup.py` (WATERMARKS table); `ProvenanceMaterialsAdvisor`.
- **Data contribution:** the motif → (mills, date_range, provenance) table (posthorn, foolscap, crowned GR, arms of Amsterdam, etc.).

### 18. Briquet, C.M. (1907). *Les Filigranes: Filigranes des manuscrits et imprimés du XIVe au XVIIe siècle.*
- **Finding:** Foundational 14th–17th-c. watermark dictionary; extends watermark dating earlier than Heawood's 17th–18th-c. focus.
- **Applied in:** `watermark_lookup.py` (added `anchor_in_circle` and `bulls_head` 16th-c. motifs); `references/provenance-watermarks.md`.
- **Data contribution:** anchor-in-a-circle (c.1540-1600, Southern European paper) and bull's-head (c.1470-1600, German/Swiss) entries.

### 19. Hunter, D. (1978). *Papermaking: The History and Technique of an Ancient Craft.* Dover.
- **Finding:** Wood-pulp paper becomes common only from c.1850; rag (linen/cotton) paper predominates before — a fast material TPQ.
- **Applied in:** `references/paper-ink-material-analysis.md`; `skill/tools/material_analysis_lookup.py` (PAPER_FIBRE table).
- **Data contribution:** rag → pre-c.1850 / wood-pulp → post-c.1850 fibre bracket.

### 20. Whatman, J. (1757 onward). *Wove paper* introduction (England); documented in paper-conservation literature.
- **Finding:** Wove paper (smooth, no chain lines) common from c.1757 onward; laid paper dominant before c.1800.
- **Applied in:** `material_analysis_lookup.py` (PAPER_TYPE table); `references/paper-ink-material-analysis.md`.
- **Data contribution:** laid → pre-c.1800 / wove → c.1757+ rule.

### 21. Gettens, R.J. & Stout, G.L. (1966). *Painting Materials: A Short Encyclopaedia.* Dover.
- **Finding:** Pigment chronology is a TPQ for hand-colouring: Prussian blue (c.1704), synthetic ultramarine (1828), chrome yellow (c.1797).
- **Applied in:** `material_analysis_lookup.py` (PIGMENT table); `references/paper-ink-material-analysis.md`.
- **Data contribution:** pigment → introduction-year table; "colour may postdate the print by decades."

### 22. IMCoS (2020). *Guidelines on Map Authentication and Valuation.* International Map Collectors' Society.
- **Finding:** Professional standard: formal authentication/valuation must be performed by an accredited specialist; research support ≠ certification.
- **Applied in:** `references/authentication-referral.md`; `skill/agents/authentication_referral.py` (guard triggers).
- **Data contribution:** the referral-trigger taxonomy and can/cannot scope.

---

## E. Historical content, toponymy & boundary history

### 23. Edney, M.H. (1997). *Mapping an Empire: The Geographical Construction of British India, 1765-1843.* University of Chicago Press.
- **Finding:** Political-boundary history and colonial toponymy are dating aids; a colony's dated existence brackets the map.
- **Applied in:** `references/toponymy-boundary-history.md`; `ToponymyBoundaryAdvisor`.
- **Data contribution:** the political-status dating rule (e.g. colony vs independent state).

### 24. Barber, P. & Harper, T. (2010). *Magnificent Maps: Power, Propaganda and Art.* British Library.
- **Finding:** Historical-content and political-context analysis as a dating/attribution aid.
- **Applied in:** `references/toponymy-boundary-history.md`.
- **Data contribution:** the "latest-datable toponym + boundary consistency" rule.

### 25. Barber, P. (ed.) (2005). *The Map Book.* Walker & Company.
- **Finding:** Comprehensive applied reference spanning periods/techniques; cross-checks technique + content + projection.
- **Applied in:** all five methodology advisors (cross-axis convergence).
- **Data contribution:** the convergent-TPQ/TAQ synthesis rule in `references/prompts/map-dating-report.md`.

---

## Supplementary authoritative sources (applied, not enumerated above)

| # | Source | Applied in |
|---|---|---|
| 26 | Campbell, T. (1987). *Early Maps.* Abbeville Press. | `references/authentication-referral.md` (authentication basics) |
| 27 | Thrower, N.J.W. (1996). *Maps & Civilization.* Univ. of Chicago Press. | projection/projection-history cross-reference |
| 28 | Harley, J.B. & Woodward, D. (1987). *History of Cartography, Vol. 1.* Univ. of Chicago Press. | pre-modern cartography grounding |
| 29 | Buisseret, D. (2003). *The Mapmakers' Quest.* Oxford Univ. Press. | early-modern map context |
| 30 | Robinson, A.H. (1982). *Early Thematic Mapping in the Age of Staadt.* Univ. of Chicago Press. | thematic-content dating support |

---

## Application summary (source → component → data)

| Source class | Tool(s) enriched | Advisor(s) | Reference doc |
|---|---|---|---|
| Print technique (1-5) | `print_technique_lookup` | `PrintTechniqueDatingAdvisor` | `print-technique-dating.md` |
| Projections (6-9) | `projection_timeline` | `ProjectionHistoryAdvisor` | `map-projection-history.md` |
| Cartobibliography (10-16) | `cartobibliographic_lookup` | `CartobibliographyAdvisor` | `cartobibliography.md` |
| Provenance/materials (17-22) | `watermark_lookup` + `material_analysis_lookup` (NEW) | `ProvenanceMaterialsAdvisor` | `provenance-watermarks.md` + `paper-ink-material-analysis.md` |
| Toponymy/boundaries (23-25) | `toponym_lookup` | `ToponymyBoundaryAdvisor` | `toponymy-boundary-history.md` |
| Authentication (22, 26) | — | `AuthenticationReferralAdvisor` | `authentication-referral.md` |

## Traceability invariant
Every `AdvisorResult.references_used` entry and every tool-table row MUST trace to a source listed here. New data added during maintenance must append a source entry to this file before (or alongside) the tool-table change, so the "no unsourced claims" guarantee in `CLAUDE.md` holds.
