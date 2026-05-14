# Budget 2026 Investor Action Matrix — Build Spec v2.1

**Status:** Handover draft for build agent (revised)
**Version:** 2.1 (v2 plus negative-gearing cutoff correction patch)
**Owner site:** https://factual-au.setiyaputra.me
**Companion app:** https://australia-cgt-reform-calculator.setiyaputra.me
**Deliverable:** Markdown content files + a JSON data file conforming to `schema.json`. No UI in this scope.

**Changes from v1:**
- Archetypes reduced from 6 to 4 (passive, property, active, founder)
- rentvester absorbed into `property`; trust-structure concerns moved into `active` via a per-cell flag; passive FIRE-style accumulators generally treated as `passive`
- Voter cohort tagging added to each cell via `salientFor.voterCohorts`
- Political actor axis dropped (party tactics deemed out of scope)
- Cell count: 180 → 120

---

## 1. Purpose

The Budget 2026 Claims Monitor scrutinises claims about negative gearing, CGT, and startup impacts against primary sources. This matrix extends the site from "is this claim supported?" to "given the claim is partly true, what should I actually do?"

For each combination of **investor archetype** and **life stage**, under each plausible **policy outcome**, the matrix gives the reader:

1. A recommended action
2. The expected payoff direction (qualitative)
3. The regret if the policy scenario flips to a different branch
4. The single key assumption the action depends on
5. A link to the CGT calculator scenario that pressure-tests it
6. Voter cohort salience tags — which slices of the electorate this cell is most relevant to (context only, not segmentation)

Tone: decision-support framed in primary-source-aware language, not financial advice.

---

## 2. Scope and non-goals

**In scope:**
- A 4 × 5 archetype-by-life-stage grid, replicated across 6 policy scenarios = 120 cells
- Markdown long-form for each archetype and each scenario
- A single `matrix.json` containing every cell's structured payload
- Voter cohort tagging on each cell (multi-dimensional taxonomy, §3.4)
- Cross-links into existing calculator scenarioIds

**Out of scope:**
- Visual UI, components, routing, deployment
- New CGT calculator scenarios
- Personalised financial recommendations or product picks
- Political-actor game theory (party / faction moves)
- Forecasting which scenario lands

---

## 3. Axes and tagging

### 3.1 Life stages (5)

| ID | Label | Definition |
|---|---|---|
| `early_career` | Early-career accumulator (20s) | Building first portfolio; little CGT history; may rent; pre-FHB. |
| `mid_career_fhb` | Mid-career builder (30s) | Often first-home buyer or recent buyer; growing portfolio; possibly young family. |
| `peak_earner` | Peak-earner (40s) | Top-bracket income common; portfolio compounding; super contributions material. |
| `pre_retiree_bridge` | Pre-retiree, bridge phase (50s) | Building non-super assets to bridge to preservation age; CGT realisation timing critical. |
| `retiree_decum` | Retiree, decumulation (60+) | Drawing down; pension-phase super possible; lower marginal rate windows. |

### 3.2 Archetypes (4)

| ID | Label | Definition |
|---|---|---|
| `passive` | Passive investor | Buy-and-hold index/ETF investor. No alpha-seeking. Long horizon. Returns track the market. |
| `property` | Property investor | Owns one or more investment properties. May be negatively geared, may use equity to grow portfolio. Rentvesters fall here. |
| `active` | Active investor | Returns depend materially on the investor's own decisions, turnover, concentration, or structure use. Includes frequent traders, options/concentrated bets, and self-managed structure users (SMSF, trusts) where the structure is the strategy. |
| `founder` | Founder / business owner | Material equity in a private operating business. Exit gain dominates lifetime wealth. Treated separately because Subdivision 152 and any founder-relief carve-out apply only here. |

**Migration note from v1:**
- `fire` → usually `passive` when the strategy is fundamentally buy-and-hold; only treat as `active` where execution, turnover, or structure is itself the edge
- `rentvester` → `property` (note dual ETF + IP balance sheet in the archetype brief)
- `trust_fo` → `active` (with `usesStructure: true` per-cell flag where the recommendation depends on a trust/company structure)

### 3.3 Policy scenarios (6)

| ID | Label | What it means for the planner |
|---|---|---|
| `s_announced` | Passes as announced | **From 1 Jul 2027:** 50% discount replaced by indexation + 30% minimum tax for all CGT assets; NG on established residential property purchased after 7:30 pm AEST 12 May 2026 is quarantined to residential property income/gains. **Grandfathering:** properties held or under exchanged contract before 7:30 pm AEST 12 May 2026 keep current NG and CGT discount treatment. **Grace window:** properties bought 13 May 2026 to 30 Jun 2027 can be negatively geared against any income during that window only. **New builds:** keep NG indefinitely and choose between the 50% discount or indexation at sale. **Existing CGT assets:** valuation cost-base reset at 1 Jul 2027. Super funds, widely held trusts, build-to-rent, and affordable-housing investors excluded from the NG change. |
| `s_delayed` | Delayed past 2027 election | Start date pushed back or paused; effectively reverts to status quo through the election cycle. |
| `s_repealed` | Repealed / not legislated | Package fails or is wound back. 50% discount and current NG persist. |
| `s_founder_relief` | Founder relief carve-out added | Package passes with QSBS/BADR-style relief for qualifying founders. |
| `s_floor_dropped` | 30% floor dropped, indexation kept | Minimum tax removed; inflation-indexed cost base remains. |
| `s_hybrid` | Indexation dropped, 50% discount + floor kept | No inflation indexation, but the 50% discount survives alongside a 30% minimum effective rate. |

### 3.4 Voter cohort taxonomy (tags, not axis)

Cells carry `salientFor.voterCohorts` — describing **which slices of the electorate the action is most relevant to**, not who the action is *for*. A FIRE realisation strategy might be most salient to inner-metro professional voters and pensioners, even though the action itself is archetype/life-stage driven.

Three dimensions. A cell can carry tags from any or all three.

**Demographic** (pick zero or more):
- `gen_z` (born ~1997–2012)
- `millennial` (~1981–1996)
- `gen_x` (~1965–1980)
- `boomer` (~1946–1964)
- `pensioner` (income-support recipient, age pension or DSP)

**Economic** (pick zero or more):
- `renter`
- `fhb_aspirant`
- `owner_occupier`
- `landlord`
- `asset_rich_retiree`

**Electoral** (pick zero or more):
- `inner_metro_progressive`
- `outer_suburb_mortgage_belt`
- `regional`
- `teal_seat`
- `safe_coalition`

**Editorial discipline:** tag sparingly. A cell salient to everyone is salient to no one. Aim for 2–5 tags total per cell across the three dimensions. If a cell genuinely cuts across all cohorts, keep the array short and say so in `cohortNote`.

---

## 4. Cell payload

Each cell: one (archetype × life_stage × scenario) tuple. 4 × 5 × 6 = 120.

| Field | Type | Notes |
|---|---|---|
| `cellId` | string | Slug: `{archetype}__{life_stage}__{scenario}` |
| `archetype` | enum | One of the 4 archetype IDs |
| `lifeStage` | enum | One of the 5 life stage IDs |
| `scenario` | enum | One of the 6 scenario IDs |
| `action` | string | Imperative phrasing. Max ~25 words. |
| `actionRationale` | string | 1–3 sentences. |
| `expectedPayoff` | enum | `strongly_positive` \| `positive` \| `neutral` \| `negative` \| `strongly_negative` |
| `payoffNarrative` | string | 1–2 sentences qualitative. |
| `regret` | object | What if the world flips. See 4.1. |
| `keyAssumption` | string | Single most load-bearing assumption. |
| `calculatorAnchor` | object \| null | CGT calculator scenarioId link. |
| `verdictTone` | enum | `confident` \| `hedged` \| `speculative` |
| `usesStructure` | boolean | True if action requires trust/company/SMSF. |
| `salientFor` | object | Voter cohort tagging. See §3.4 and §4.2. |
| `cohortNote` | string \| null | 1 sentence on political salience. Null if no tags. |
| `narrativesReferenced` | string[] | Optional. Dashboard narrative IDs. |

### 4.1 The `regret` object

```
regret: {
  ifScenario: "s_repealed",
  severity: "high",
  description: "If the package is repealed, locking in gains in FY26-27 crystallised tax that could have stayed deferred."
}
```

Populate the single most material regret, not all five counterfactuals.

### 4.2 The `salientFor` object

```
salientFor: {
  voterCohorts: {
    demographic: ["millennial", "gen_x"],
    economic: ["landlord", "owner_occupier"],
    electoral: ["outer_suburb_mortgage_belt"]
  }
}
```

Each sub-array may be empty. Use `cohortNote` to explain salience in one sentence.

### 4.3 Worked example

```
active__pre_retiree_bridge__s_announced
```

- **action:** "Bring forward partial CGT realisations on bridge-phase ETFs into FY26-27 to lock in the 50% discount on existing accrued gains."
- **actionRationale:** "Existing CGT assets get a market-value cost-base reset on 1 Jul 2027. Realising before applies the current 50% discount to gains accrued to date. Post-reset, only further gains face indexation plus the 30% floor."
- **expectedPayoff:** `positive`
- **payoffNarrative:** "Locks in the cheaper-of-two-regimes treatment for the pre-2027 portion of the gain."
- **regret:** `{ ifScenario: "s_repealed", severity: "medium", description: "If the package is repealed, the realisation crystallised tax that could have stayed deferred. Cost is the time-value of paid tax." }`
- **keyAssumption:** "The bridge-phase drawdown actually needs these specific parcels within 10–15 years; otherwise pre-2027 realisation is just early tax."
- **calculatorAnchor:** `{ scenarioId: "budget-2026-fire-bridge-phase-claim", label: "Open bridge-phase scenario" }`
- **verdictTone:** `hedged`
- **usesStructure:** `false`
- **salientFor:** `{ voterCohorts: { demographic: ["gen_x", "boomer"], economic: ["asset_rich_retiree"], electoral: ["inner_metro_progressive", "teal_seat"] } }`
- **cohortNote:** "Most relevant to professional-class pre-retirees in inner-metro and teal seats who hold material non-super ETF balances and read tax change as a personal-portfolio question."
- **narrativesReferenced:** `[]`

### 4.4 Corrected property worked example

```
property__mid_career_fhb__s_announced
```

- **action:** "If an established-property purchase still works once losses quarantine from 1 Jul 2027, complete it only for grace-window economics; otherwise switch the search to eligible new builds or stand down."
- **actionRationale:** "Budget night at 7:30 pm AEST on 12 May 2026 has already passed as the grandfathering cutoff. Properties bought from 13 May 2026 to 30 Jun 2027 get negative gearing against any income only during the grace window, then losses quarantine from 1 Jul 2027 onward. The strategic question is whether the property still works once those wage-tax offsets disappear."
- **expectedPayoff:** `neutral`
- **payoffNarrative:** "The grace-window negative-gearing benefit is real but short-lived. The action's payoff depends far more on whether the property still works once losses quarantine from 1 Jul 2027 than on capturing a temporary deduction."
- **regret:** `{ ifScenario: "s_repealed", severity: "low", description: "If the package is repealed, the property reverts to full negative-gearing treatment indefinitely, which is a windfall rather than a pure regret. The real regret risk is having paid too much for the asset because grace-window urgency distorted the purchase discipline." }`
- **keyAssumption:** "The property's after-tax cash flow remains sustainable once losses on established residential property are quarantined to residential property income and gains from 1 Jul 2027 onward. If the deal only works by offsetting wage tax indefinitely, the grace window does not rescue it."
- **calculatorAnchor:** `{ scenarioId: "housing-claim-negative-gearing", label: "Test post-cutoff NG mechanics" }`
- **verdictTone:** `speculative`
- **usesStructure:** `false`
- **salientFor:** `{ voterCohorts: { demographic: ["millennial", "gen_x"], economic: ["landlord", "fhb_aspirant"], electoral: ["outer_suburb_mortgage_belt"] } }`
- **cohortNote:** "Politically loudest cell in the matrix because aspiring and existing mortgage-belt landlords face the clearest behaviour change once the grace window replaces any hope of new grandfathering."

---

## 5. Calculator anchors — known scenarioIds

| scenarioId | Best fit for |
|---|---|
| `budget-2026-young-etf-home-deposit-claim` | ETF saving toward a deposit; first-home pathway |
| `budget-2026-zero-cost-base-business-claim` | Founder exits with no relief, top-rate, post-2027 |
| `budget-2026-fire-bridge-phase-claim` | Bridge-phase realisation timing |
| `budget-2026-young-founder-net-exit-claim` | Founder gross-to-net target with top-rate |
| `budget-2026-subdiv152-founder-relief-claim` | Founder exit with active-business relief |
| `budget-2026-pre-cgt-assets-claim` | Pre-1985 asset transition stress test |
| `budget-2026-family-home-distortion-claim` | Established-property post-cutoff cases |
| `budget-2026-cgt-founder-claim` | Generic top-rate founder exit |
| `budget-2026-capital-vs-labour-tax-claim` | Long-held discounted gain vs marginal labour tax |
| `housing-claim-negative-gearing` | Post-cutoff established-property with NG losses |

Set `calculatorAnchor: null` when no scenarioId cleanly fits. Do not stretch.

---

## 6. Editorial rules

1. **No financial advice voice.** "Rational move under this assumption" not "you should."
2. **Hedge proportionate to confidence.** Match the claims monitor's idiom.
3. **No dollar figures in JSON.** Direction and severity only.
4. **Pre-2027 vs post-2027 mechanics must be correct.** Pre-1 Jul 2027 gains via valuation reset → 50% discount. Post-reset gains under `s_announced` → indexation + 30% floor.
5. **Super is untouched by the CGT changes.**
6. **Main residence exemption stays.**
7. **Subdivision 152 (small business CGT) is preserved.** Founder actions flag eligibility as an assumption.
8. **Pre-1985 assets:** gains accruing from 1 Jul 2027 enter the CGT net under `s_announced`.
9. **Pensioners and income-support recipients** exempt from the 30% floor.
10. **No predictions about which scenario lands.**
11. **Voter cohort tags describe salience, not segmentation.** A `millennial` tag doesn't mean "for millennials only"; it means "politically charged for millennials."
12. **Cohort tags must be defensible.** If you can't write a one-sentence `cohortNote` justifying a tag, drop it.
13. **Three NG dates must be respected:** 7:30 pm AEST 12 May 2026 (grandfathering cutoff), the 13 May 2026 to 30 Jun 2027 grace window, and 1 Jul 2027 (commencement). Property cells must use the right date for the position they describe.
14. **NG changes apply to residential property only.** Share, ETF, and commercial-property cells must not import the housing-side NG restriction. Their CGT treatment may still change from 1 Jul 2027.
15. **Super funds and widely held trusts are excluded from the NG change.** Cells with `usesStructure: true` involving SMSF residential property must not import the housing-side restriction; where CGT treatment for super is unclear, hedge explicitly.
16. **The new-build carve-out is dual:** indefinite NG access plus a choice between the 50% discount and indexation at sale.

---

## 7. Content production sequence

1. Read https://factual-au.setiyaputra.me/dashboard for tone.
2. Read https://factual-au.setiyaputra.me/methodology for verdict taxonomy.
3. Write 4 archetype briefs. The `active` brief must enumerate the sub-types (FIRE, frequent trader, structure-driven) and how the matrix collapses them.
4. Write 6 scenario briefs.
5. Write `cohorts.md` documenting all 15 cohort tags.
6. Generate 120-cell `matrix.json` following `schema.json`. Order: by archetype, then by life stage, then by scenario.
7. **Differentiation check:** for each (archetype × life_stage), actions must differ across at least 4 of the 6 scenarios.
8. **Cohort tagging pass:** median cell should carry 2–4 tags total across all dimensions.
9. **Calculator anchor check:** verify every `scenarioId` exists in §5.
10. **Grace-window check:** property cells under `s_announced`, `s_delayed`, `s_hybrid`, `s_floor_dropped`, and `s_founder_relief` must distinguish grandfathered holders from grace-window or post-commencement buyers where that changes the action.

---

## 8. File layout

```
/matrix/
  SPEC.md
  schema.json
  matrix.json
  archetypes/
    passive.md
    property.md
    active.md
    founder.md
  scenarios/
    s_announced.md
    s_delayed.md
    s_repealed.md
    s_founder_relief.md
    s_floor_dropped.md
    s_hybrid.md
  life_stages/
    life_stages.md
  cohorts/
    cohorts.md
```

Each Markdown file: frontmatter with `id`, `label`, `summary` (≤ 240 chars), `lastReviewed` (ISO date).

---

## 9. Acceptance criteria

- [ ] `matrix.json` validates against `schema.json`
- [ ] Exactly 120 cells; every cellId unique
- [ ] Every `calculatorAnchor.scenarioId` referenced exists in §5
- [ ] All required fields populated (nullable: `calculatorAnchor`, `cohortNote`, `narrativesReferenced`)
- [ ] No cell contains a dollar figure
- [ ] No cell uses "you should" framing
- [ ] For each (archetype × life_stage), actions differ across ≥ 4 of 6 scenarios
- [ ] Median cell has 2–4 cohort tags total
- [ ] Every cell with cohort tags has `cohortNote`; every cell without has `cohortNote: null`
- [ ] All 4 archetype Markdown files exist
- [ ] All 6 scenario Markdown files exist
- [ ] `cohorts.md` exists documenting the 15 tags
- [ ] No `property` cell uses `1 Jul 2027` as the grandfathering purchase cutoff for negative gearing
- [ ] At least one cell per (`property` × life stage) explicitly references the grace window concept
- [ ] No cell suggests the reader can still act before Budget night unless framed retrospectively
- [ ] Cells with `usesStructure: true` involving SMSF residential property do not import the NG restriction
- [ ] New-build property cells reference both indefinite NG access and the 50%-discount-or-indexation choice

---

## 10. Open questions for srvzt

1. The `active` archetype is heterogeneous. Brief can flag sub-types, but cells must collapse them. Is there a sub-type whose action would *differ materially* from the collapsed answer that we should split out? (My instinct: no.)
2. Cohort tags lean political. Add a `cohortStakes` field to capture *why* the cohort cares (economic interest vs identity vs ideology)? Adds editorial overhead but makes political salience more legible.
3. `cohortNote` is one sentence by design, but cells like `property__mid_career_fhb__s_announced` are politically loudest. Allow up to 3 sentences when `verdictTone: speculative`?
4. The separate 30% minimum tax on discretionary trust distributions from 1 Jul 2028 affects `active` cells with `usesStructure: true`. Second regret object, or fold into `keyAssumption`?
5. The grace-window correction introduces an implicit investor-position distinction: grandfathered holder, grace-window buyer, post-commencement buyer, and new-build buyer. Keep that in prose for now, or promote it to a formal axis in a future v3 if user testing shows repeated misreads?

---

## 11. References

- Budget Paper 2, pp.21–22 — CGT and NG policy text
- Budget 2026 tax explainer — transition mechanics, pre-1985 asset treatment
- ATO: Small business CGT concessions (Subdiv 152)
- ATO: Main residence exemption
- ATO: Tax rates — Australian resident
