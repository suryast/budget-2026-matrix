---
id: "active"
label: "Active investor"
summary: "Returns depend on own decisions or deliberate structure use. Includes frequent traders, concentrated bets, and trust-led strategies."
lastReviewed: "2026-06-18"
---

The active archetype is intentionally narrower than a generic 'engaged investor' label. It is for people whose returns depend materially on turnover, concentrated position-taking, derivatives, or structure-driven execution using trusts or SMSFs as part of the strategy. They are grouped here because tax timing is part of the return engine rather than a background detail.

Bridge-phase drawdown questions can still matter here, but passive FIRE accumulators are generally better read as passive investors unless their edge really comes from active execution. Frequent traders care about whether higher turnover loses more after tax. Structure-driven investors care about whether the recommendation quietly assumes a trust or company. Cells set `usesStructure: true` only when the action materially depends on that extra layer.

The trust patch adds a second date to watch for structure-driven active investors: 1 Jul 2028 for the discretionary-trust minimum tax. Peak-earner trust users are most exposed where bucket companies are part of the execution logic. Pre-retiree bridge users are more often exposed through low-rate or franked-income streaming. Where trust exposure is real, the sidecar field records whether the better move is to restructure during the 1 Jul 2027 to 30 Jun 2030 Federal rollover window, while still warning that State duty can remain material.
