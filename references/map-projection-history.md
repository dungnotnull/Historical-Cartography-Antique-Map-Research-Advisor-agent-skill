# Reference — History of Map Projections (dating aid)

> Distilled from Snyder (1993) *Flattening the Earth*; Woodward (ed.) *History of Cartography* Vol. 1–6. Operationalised by the `projection_timeline` tool and the `ProjectionHistoryAdvisor`.

## Core principle
A map **cannot use a projection invented after it was made** — a projection is a *terminus post quem*. Combined with other axes, projection choice narrows the date and sometimes the school/region of cartography.

## Projection timeline (key entries)

| Projection | Invented | Inventor | Dating implication |
|---|---|---|---|
| Ptolemaic conic / trapezoidal | c.150 AD | Ptolemy | Printed Ptolemy tradition 1477–1570s |
| Stereographic (azimuthal) | Antiquity | Hipparchus/Ptolemy | Weak axis; common for polar/star maps |
| Orthographic (perspective) | Antiquity | Ptolemy | Decorative world maps 16th–17th c. |
| **Mercator** (cylindrical conformal) | **1569** | Gerardus Mercator | **Cannot predate 1569**; nav. use from c.17th c. |
| Sinusoidal (Sanson-Flamsteed) | c.1570 | Cini / Sanson | 17th–18th c., French school |
| Bonne (pseudoconic equal-area) | 1752 | Rigobert Bonne | Post-1752; late-18th-c. French atlases |
| Lambert conformal conic | 1772 | J.H. Lambert | Post-1772; modern state surveys |
| Robinson (compromise) | 1963 | A.H. Robinson | Post-1963 — strong modern signal |

## How to identify a projection from the graticule
- **Meridians straight & parallel, parallels straight & spacing-increasing poleward** → Mercator.
- **Meridians curved (sine), parallels straight** → sinusoidal.
- **Parallels concentric arcs, meridians curved converging** → conic/Bonne.
- **Pole as a point** → azimuthal family; **pole as a line** → cylindrical/pseudocylindrical family.
- **Trapezoidal straight meridians, curved parallels** → Ptolemaic conic (early printed Ptolemies).

## Guardrail
A projection date is necessary but not sufficient — old projections are re-used long after invention. Use as one of several axes.
