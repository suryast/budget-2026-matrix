#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAST_REVIEWED = "2026-05-14"


ARCHETYPES = [
    {
        "id": "passive",
        "label": "Passive investor",
        "summary": "Buy-and-hold index and ETF investor. No alpha-seeking. Long horizon.",
        "markdownPath": "archetypes/passive.md",
    },
    {
        "id": "property",
        "label": "Property investor",
        "summary": "Owns one or more investment properties. May be negatively geared. Rentvesters fall here.",
        "markdownPath": "archetypes/property.md",
    },
    {
        "id": "active",
        "label": "Active investor",
        "summary": "Returns depend on own decisions or deliberate structure use. Includes frequent traders, concentrated bets, and trust-led strategies.",
        "markdownPath": "archetypes/active.md",
    },
    {
        "id": "founder",
        "label": "Founder / business owner",
        "summary": "Material equity in a private operating business. Exit gain dominates lifetime wealth.",
        "markdownPath": "archetypes/founder.md",
    },
]

LIFE_STAGES = [
    {
        "id": "early_career",
        "label": "Early-career accumulator (20s)",
        "summary": "Building first portfolio; little CGT history; may rent; pre-FHB.",
        "markdownPath": "life_stages/life_stages.md",
    },
    {
        "id": "mid_career_fhb",
        "label": "Mid-career builder (30s)",
        "summary": "Often first-home buyer or recent buyer; growing portfolio; possibly young family.",
        "markdownPath": "life_stages/life_stages.md",
    },
    {
        "id": "peak_earner",
        "label": "Peak-earner (40s)",
        "summary": "Top-bracket income common; portfolio compounding; super contributions material.",
        "markdownPath": "life_stages/life_stages.md",
    },
    {
        "id": "pre_retiree_bridge",
        "label": "Pre-retiree, bridge phase (50s)",
        "summary": "Building non-super assets to bridge to preservation age; CGT timing matters.",
        "markdownPath": "life_stages/life_stages.md",
    },
    {
        "id": "retiree_decum",
        "label": "Retiree, decumulation (60+)",
        "summary": "Drawing down; pension-phase super possible; lower marginal-rate windows matter.",
        "markdownPath": "life_stages/life_stages.md",
    },
]

SCENARIOS = [
    {
        "id": "s_announced",
        "label": "Passes as announced",
        "summary": "From 1 Jul 2027 the CGT discount is replaced by indexation plus a 30 percent floor; established residential property bought after Budget night faces quarantined negative gearing, with a grace window through 30 Jun 2027 and a stronger new-build carve-out.",
        "markdownPath": "scenarios/s_announced.md",
    },
    {
        "id": "s_delayed",
        "label": "Delayed past 2027 election",
        "summary": "Start date pushed back or paused; status quo survives through the election cycle.",
        "markdownPath": "scenarios/s_delayed.md",
    },
    {
        "id": "s_repealed",
        "label": "Repealed or not legislated",
        "summary": "Package fails or is wound back. Current CGT discount and negative gearing persist.",
        "markdownPath": "scenarios/s_repealed.md",
    },
    {
        "id": "s_founder_relief",
        "label": "Founder relief carve-out added",
        "summary": "Package passes with founder-specific relief for qualifying private-business gains.",
        "markdownPath": "scenarios/s_founder_relief.md",
    },
    {
        "id": "s_floor_dropped",
        "label": "30 percent floor dropped, indexation kept",
        "summary": "Minimum tax removed; inflation-indexed cost base remains.",
        "markdownPath": "scenarios/s_floor_dropped.md",
    },
    {
        "id": "s_hybrid",
        "label": "Indexation dropped, discount plus floor kept",
        "summary": "No indexation, but the discount survives alongside a minimum effective rate.",
        "markdownPath": "scenarios/s_hybrid.md",
    },
]

COHORT_DIMENSIONS = {
    "demographic": [
        {"id": "gen_z", "label": "Gen Z", "summary": "Born approximately 1997 to 2012."},
        {"id": "millennial", "label": "Millennial", "summary": "Born approximately 1981 to 1996."},
        {"id": "gen_x", "label": "Gen X", "summary": "Born approximately 1965 to 1980."},
        {"id": "boomer", "label": "Boomer", "summary": "Born approximately 1946 to 1964."},
        {"id": "pensioner", "label": "Pensioner", "summary": "Income-support recipient, including age pension or DSP."},
    ],
    "economic": [
        {"id": "renter", "label": "Renter", "summary": "Rents primary residence."},
        {"id": "fhb_aspirant", "label": "First-home buyer aspirant", "summary": "Saving toward a first-home deposit."},
        {"id": "owner_occupier", "label": "Owner-occupier", "summary": "Owns primary residence and reads policy through household cash flow."},
        {"id": "landlord", "label": "Landlord", "summary": "Holds investment property and cares about deduction treatment."},
        {"id": "asset_rich_retiree", "label": "Asset-rich retiree", "summary": "Material non-super assets and drawdown exposure."},
    ],
    "electoral": [
        {"id": "inner_metro_progressive", "label": "Inner-metro progressive", "summary": "Inner-city Labor or Greens seats with large professional class exposure."},
        {"id": "outer_suburb_mortgage_belt", "label": "Outer-suburb mortgage belt", "summary": "Marginal outer-suburb seats shaped by mortgage stress and household cash flow."},
        {"id": "regional", "label": "Regional", "summary": "Non-metropolitan seats with different business and housing exposures."},
        {"id": "teal_seat", "label": "Teal seat", "summary": "Independent-held former Liberal seats with high professional investor exposure."},
        {"id": "safe_coalition", "label": "Safe Coalition", "summary": "Safe Liberal or Nationals seats where landlord and small-business narratives travel well."},
    ],
}

CALCULATOR_ANCHORS = {
    ("passive", "early_career"): ("budget-2026-young-etf-home-deposit-claim", "Open ETF saver scenario"),
    ("passive", "mid_career_fhb"): ("budget-2026-young-etf-home-deposit-claim", "Open deposit saver scenario"),
    ("passive", "peak_earner"): ("budget-2026-capital-vs-labour-tax-claim", "Compare capital and labour treatment"),
    ("passive", "pre_retiree_bridge"): ("budget-2026-fire-bridge-phase-claim", "Open bridge-phase scenario"),
    ("passive", "retiree_decum"): ("budget-2026-fire-bridge-phase-claim", "Stress-test decumulation timing"),
    ("property", "early_career"): ("housing-claim-negative-gearing", "Test established-property scenario"),
    ("property", "mid_career_fhb"): ("housing-claim-negative-gearing", "Test post-cutoff NG mechanics"),
    ("property", "peak_earner"): ("housing-claim-negative-gearing", "Test grace-window geared-property case"),
    ("property", "pre_retiree_bridge"): ("budget-2026-family-home-distortion-claim", "Check property versus other assets"),
    ("property", "retiree_decum"): ("budget-2026-family-home-distortion-claim", "Check post-cutoff property case"),
    ("active", "early_career"): ("budget-2026-young-etf-home-deposit-claim", "Open active accumulation scenario"),
    ("active", "mid_career_fhb"): ("budget-2026-young-etf-home-deposit-claim", "Open active saver scenario"),
    ("active", "peak_earner"): ("budget-2026-capital-vs-labour-tax-claim", "Compare tax-rate exposure"),
    ("active", "pre_retiree_bridge"): ("budget-2026-fire-bridge-phase-claim", "Open bridge-phase scenario"),
    ("active", "retiree_decum"): ("budget-2026-fire-bridge-phase-claim", "Stress-test drawdown scenario"),
    ("founder", "early_career"): ("budget-2026-cgt-founder-claim", "Open founder exit scenario"),
    ("founder", "mid_career_fhb"): ("budget-2026-young-founder-net-exit-claim", "Open founder net-target scenario"),
    ("founder", "peak_earner"): ("budget-2026-zero-cost-base-business-claim", "Model no-relief founder exit"),
    ("founder", "pre_retiree_bridge"): ("budget-2026-subdiv152-founder-relief-claim", "Check founder relief scenario"),
    ("founder", "retiree_decum"): ("budget-2026-subdiv152-founder-relief-claim", "Check relief-heavy founder scenario"),
}

NARRATIVES = {
    "passive": ["cluster-long-term-etf-planning"],
    "property": ["cluster-negative-gearing-grandfathering", "cluster-young-people-rentvesting-tax-grab"],
    "active": ["cluster-long-term-etf-planning"],
    "founder": ["cluster-founder-capital-flight", "cluster-zero-cost-base-business-exit"],
}

ACTION_BASE = {
    "passive": {
        "s_announced": "Stage pre-2027 parcel sales only where they serve a real near-term goal, and keep fresh savings on the long-horizon plan rather than abandoning equities.",
        "s_delayed": "Avoid irreversible pre-emptive sales and keep building under the current rules while preserving records for a possible later transition.",
        "s_repealed": "Drop tax-driven timing trades and return to the simplest low-turnover accumulation plan the portfolio can actually hold through volatility.",
        "s_founder_relief": "Treat the founder carve-out as noise for a passive portfolio and stay focused on low-turnover accumulation and contribution discipline.",
        "s_floor_dropped": "Prefer deferral over early realisation, but reassess low-bracket sale windows because indexation without the floor softens long-hold outcomes.",
        "s_hybrid": "Keep long holds, but stop relying on inflation uplift and compare every planned sale against the surviving discount plus floor combination.",
    },
    "property": {
        "s_announced": "Base property decisions on whether the holding still works once losses quarantine from 1 Jul 2027, and treat the grace window as a short-term bonus rather than the reason to buy.",
        "s_delayed": "Use the delay to model the grace-window economics more carefully, but do not treat it as a chance to recover full grandfathering on established property.",
        "s_repealed": "Run the property strategy on rental yield, leverage resilience, and vacancy risk rather than on a reform scare that no longer changes the rule set.",
        "s_founder_relief": "Keep property decisions anchored to grace-window and post-2027 housing economics, because founder relief does not change the residential negative-gearing rules.",
        "s_floor_dropped": "Treat the grace-window and post-2027 housing rules as unchanged, and only then ask whether the softer CGT branch improves the property case enough to matter.",
        "s_hybrid": "Treat the grace-window and post-2027 housing rules as unchanged, then test whether the softer CGT side is enough to justify holdings that still need quarantined-loss tolerance.",
    },
    "active": {
        "s_announced": "Map planned realisations and structure-dependent moves before 1 Jul 2027, because active strategies suffer most when tax timing becomes part of the return engine.",
        "s_delayed": "Keep the strategy live but hold off on large one-way tax trades until the implementation window is real rather than hypothetical.",
        "s_repealed": "Simplify where possible and stop paying turnover costs to defend against a tax regime that never arrives.",
        "s_founder_relief": "Separate private-business exposure from the rest of the active book and avoid letting founder headlines drive unnecessary portfolio churn elsewhere.",
        "s_floor_dropped": "Lean into lower-rate realisation windows and inflation-sensitive assets, because indexation without the floor materially softens the tax drag on active compounding.",
        "s_hybrid": "Assume turnover still hurts, but the surviving discount keeps some old optimisation logic alive; emphasise discipline over heroic tax engineering.",
    },
    "founder": {
        "s_announced": "Delay non-essential exit timing decisions until the cap table, relief eligibility, and post-2027 exposure are modelled explicitly rather than argued from slogans.",
        "s_delayed": "Preserve flexibility and avoid forcing an exit into a temporary calm, because the economic value of waiting may exceed the value of guessing the next start date.",
        "s_repealed": "Stop building around a founder-tax shock that never lands and refocus on operating value, pricing power, and succession or exit readiness.",
        "s_founder_relief": "Hold the exit path open long enough to qualify for the carve-out, and structure the sale around the relief conditions instead of generic founder outrage.",
        "s_floor_dropped": "Re-run exit timing with indexation-only logic and test whether the case for rushing, relocating, or restructuring still survives without the floor.",
        "s_hybrid": "Model the surviving discount carefully and do not assume the founder problem disappears just because indexation falls away.",
    },
}

REGRET_TARGET = {
    "s_announced": ("s_repealed", "medium"),
    "s_delayed": ("s_announced", "medium"),
    "s_repealed": ("s_announced", "low"),
    "s_founder_relief": ("s_announced", "high"),
    "s_floor_dropped": ("s_hybrid", "medium"),
    "s_hybrid": ("s_floor_dropped", "medium"),
}

TONE_MAP = {
    "s_announced": "hedged",
    "s_delayed": "hedged",
    "s_repealed": "confident",
    "s_founder_relief": "speculative",
    "s_floor_dropped": "hedged",
    "s_hybrid": "speculative",
}

PAYOFF_MATRIX = {
    "passive": {
        "early_career": {
            "s_announced": "neutral",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "neutral",
        },
        "mid_career_fhb": {
            "s_announced": "neutral",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "neutral",
        },
        "peak_earner": {
            "s_announced": "negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "negative",
        },
        "pre_retiree_bridge": {
            "s_announced": "positive",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "strongly_positive",
            "s_hybrid": "neutral",
        },
        "retiree_decum": {
            "s_announced": "positive",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "strongly_positive",
            "s_hybrid": "positive",
        },
    },
    "property": {
        "early_career": {
            "s_announced": "negative",
            "s_delayed": "negative",
            "s_repealed": "positive",
            "s_founder_relief": "negative",
            "s_floor_dropped": "negative",
            "s_hybrid": "negative",
        },
        "mid_career_fhb": {
            "s_announced": "neutral",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "negative",
            "s_floor_dropped": "negative",
            "s_hybrid": "negative",
        },
        "peak_earner": {
            "s_announced": "strongly_negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "negative",
            "s_floor_dropped": "negative",
            "s_hybrid": "strongly_negative",
        },
        "pre_retiree_bridge": {
            "s_announced": "strongly_negative",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "negative",
            "s_floor_dropped": "negative",
            "s_hybrid": "strongly_negative",
        },
        "retiree_decum": {
            "s_announced": "negative",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "negative",
            "s_floor_dropped": "neutral",
            "s_hybrid": "negative",
        },
    },
    "active": {
        "early_career": {
            "s_announced": "negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "negative",
        },
        "mid_career_fhb": {
            "s_announced": "neutral",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "neutral",
        },
        "peak_earner": {
            "s_announced": "negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "strongly_positive",
            "s_hybrid": "negative",
        },
        "pre_retiree_bridge": {
            "s_announced": "positive",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "strongly_positive",
            "s_hybrid": "neutral",
        },
        "retiree_decum": {
            "s_announced": "neutral",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "neutral",
            "s_floor_dropped": "positive",
            "s_hybrid": "neutral",
        },
    },
    "founder": {
        "early_career": {
            "s_announced": "negative",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "positive",
            "s_floor_dropped": "neutral",
            "s_hybrid": "negative",
        },
        "mid_career_fhb": {
            "s_announced": "negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "strongly_positive",
            "s_floor_dropped": "neutral",
            "s_hybrid": "negative",
        },
        "peak_earner": {
            "s_announced": "strongly_negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "positive",
            "s_floor_dropped": "negative",
            "s_hybrid": "strongly_negative",
        },
        "pre_retiree_bridge": {
            "s_announced": "negative",
            "s_delayed": "neutral",
            "s_repealed": "positive",
            "s_founder_relief": "strongly_positive",
            "s_floor_dropped": "positive",
            "s_hybrid": "negative",
        },
        "retiree_decum": {
            "s_announced": "neutral",
            "s_delayed": "positive",
            "s_repealed": "positive",
            "s_founder_relief": "strongly_positive",
            "s_floor_dropped": "positive",
            "s_hybrid": "neutral",
        },
    },
}


def expected_payoff(archetype: str, stage: str, scenario: str) -> str:
    """
    The payoff reflects the practical result of following the recommended action
    in that cell, not a one-size-fits-all judgement about the scenario itself.
    It is intentionally life-stage sensitive, because the same scenario creates
    different decision quality for accumulators, bridge-phase households, and
    retirees even within the same archetype.
    """
    return PAYOFF_MATRIX[archetype][stage][scenario]


def git_head() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT.parent), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return ""


def ensure_dirs() -> None:
    for rel in ["archetypes", "scenarios", "life_stages", "cohorts"]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def write_markdown(path: Path, meta: dict[str, str], body: str) -> None:
    frontmatter = "\n".join([f'{k}: "{v}"' for k, v in meta.items()])
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def build_archetype_briefs() -> None:
    bodies = {
        "passive": """
Passive investors are the easiest cohort to over-dramatise and the easiest cohort to misread. Their core edge is low turnover, long horizon, and not paying tax earlier than necessary. The matrix therefore treats most passive actions as timing and simplicity questions, not as invitations to overhaul the plan.

This is also where long-horizon FIRE-style accumulators mostly belong when they are still fundamentally buy-and-hold investors rather than high-turnover operators. The main policy sensitivity is around when to crystallise gains that have already accrued before 1 Jul 2027, and whether a future scenario makes deferral or partial realisation more rational. The action language stays deliberate: protect optionality, avoid unnecessary turnover, and only realise early when a real-life spending need or bridge-phase drawdown makes that timing useful.
""",
        "property": """
Property investors sit at the sharp end of the negative-gearing redesign, but not every property holder experiences the same pressure. Rentvesters, recent leveraged buyers, and long-held landlords all pass through the same archetype because the practical question is still the same: does the strategy survive with weaker tax support on established housing?

The matrix therefore treats property decisions as underwriting and balance-sheet decisions first. It does not assume reform automatically crashes prices or solves housing, and it avoids pretending the main-residence exemption disappeared. Actions focus on cutoff timing, new-build versus established-property choice, and whether the portfolio still works without the old deduction tailwind.
""",
        "active": """
The active archetype is intentionally narrower than a generic 'engaged investor' label. It is for people whose returns depend materially on turnover, concentrated position-taking, derivatives, or structure-driven execution using trusts or SMSFs as part of the strategy. They are grouped here because tax timing is part of the return engine rather than a background detail.

Bridge-phase drawdown questions can still matter here, but passive FIRE accumulators are generally better read as passive investors unless their edge really comes from active execution. Frequent traders care about whether higher turnover loses more after tax. Structure-driven investors care about whether the recommendation quietly assumes a trust or company. Cells set `usesStructure: true` only when the action materially depends on that extra layer.
""",
        "founder": """
Founders and owner-operators are separated because private-business exits are not just another capital-gain problem. Subdivision 152, active-asset tests, cap-table design, employee equity, and the possibility of a founder-specific carve-out all make this cohort genuinely different from passive or active market investors.

The matrix therefore refuses two common mistakes. It does not assume every founder gets crushed under the announced settings, because relief can matter. It also does not assume relief is universal. Most founder cells are about explicit modelling, eligibility, and timing under uncertainty, rather than about slogans like 'the government becomes your cofounder.'
""",
    }
    for item in ARCHETYPES:
        write_markdown(
            ROOT / item["markdownPath"],
            {"id": item["id"], "label": item["label"], "summary": item["summary"], "lastReviewed": LAST_REVIEWED},
            bodies[item["id"]],
        )


def build_scenario_briefs() -> None:
    bodies = {
        "s_announced": "Treat this as the base-case mechanics file with three dates, not one: the 7:30 pm AEST 12 May 2026 grandfathering cutoff, the 13 May 2026 to 30 Jun 2027 grace window, and the 1 Jul 2027 commencement date. Established residential property bought after Budget night only gets broad negative-gearing access during the grace window, then losses quarantine. New builds keep indefinite access and a stronger sale-side carve-out.",
        "s_delayed": "Delay is not repeal and it does not resurrect the Budget-night grandfathering cutoff. Actions here should preserve optionality, distinguish already-grandfathered holders from grace-window buyers, and avoid pretending a later start date means the old treatment can still be locked in for fresh established-property purchases.",
        "s_repealed": "This is the clean status-quo branch. Actions should stop defending against a rule change that never arrives and should explicitly call out the regret of having crystallised tax or reshaped a balance sheet for no reason.",
        "s_founder_relief": "This branch is narrow but politically important. Use speculative language and keep founder-specific relief distinct from broader market-investor logic. The right action usually depends on waiting for legislation rather than assuming relief exists in final form already.",
        "s_floor_dropped": "This branch matters most for lower-rate sellers, retirees, and long-horizon investors whose main objection is the flattening effect of the floor. Actions should distinguish indexation-only softening from a full return to the old regime.",
        "s_hybrid": "This is the oddest branch and should read that way. It leaves some old discount logic alive while still imposing a minimum effective rate. Actions should sound comparative and model-driven, not absolute.",
    }
    for item in SCENARIOS:
        write_markdown(
            ROOT / item["markdownPath"],
            {"id": item["id"], "label": item["label"], "summary": item["summary"], "lastReviewed": LAST_REVIEWED},
            bodies[item["id"]],
        )


def build_life_stages() -> None:
    bullet_lines = []
    for item in LIFE_STAGES:
        bullet_lines.append(f"## {item['label']}\n\n{item['summary']}\n")
    write_markdown(
        ROOT / "life_stages/life_stages.md",
        {
            "id": "life_stages",
            "label": "Life stages",
            "summary": "Reference note covering the five life-stage definitions used across the matrix.",
            "lastReviewed": LAST_REVIEWED,
        },
        "\n".join(bullet_lines),
    )


def build_cohorts() -> None:
    sections = []
    for dimension, entries in COHORT_DIMENSIONS.items():
        lines = [f"## {dimension.capitalize()}"]
        for entry in entries:
            lines.append(f"- `{entry['id']}`: {entry['label']} — {entry['summary']}")
        sections.append("\n".join(lines))
    body = (
        "These tags describe political salience, not exclusive audiences. Median cell should carry a short set of tags that explain why the action becomes politically loud in that part of the electorate.\n\n"
        + "\n\n".join(sections)
    )
    write_markdown(
        ROOT / "cohorts/cohorts.md",
        {
            "id": "cohorts",
            "label": "Voter cohorts",
            "summary": "Fifteen salience tags used to describe which electoral slices care most about a matrix cell.",
            "lastReviewed": LAST_REVIEWED,
        },
        body,
    )


def demographic_for_stage(stage: str, archetype: str) -> list[str]:
    mapping = {
        "early_career": ["gen_z"],
        "mid_career_fhb": ["millennial"],
        "peak_earner": ["gen_x"],
        "pre_retiree_bridge": ["gen_x"],
        "retiree_decum": ["pensioner"],
    }
    tags = list(mapping[stage])
    if archetype == "founder" and "pensioner" in tags:
        tags = ["boomer"]
    return tags


def economic_for(archetype: str, stage: str) -> list[str]:
    if archetype == "passive":
        return {
            "early_career": ["renter", "fhb_aspirant"],
            "mid_career_fhb": ["fhb_aspirant", "owner_occupier"],
            "peak_earner": ["owner_occupier"],
            "pre_retiree_bridge": ["owner_occupier", "asset_rich_retiree"],
            "retiree_decum": ["asset_rich_retiree"],
        }[stage]
    if archetype == "property":
        return {
            "early_career": ["renter", "landlord"],
            "mid_career_fhb": ["landlord", "fhb_aspirant"],
            "peak_earner": ["landlord", "owner_occupier"],
            "pre_retiree_bridge": ["landlord", "asset_rich_retiree"],
            "retiree_decum": ["landlord", "asset_rich_retiree"],
        }[stage]
    if archetype == "active":
        return {
            "early_career": ["renter", "fhb_aspirant"],
            "mid_career_fhb": ["owner_occupier", "fhb_aspirant"],
            "peak_earner": ["owner_occupier"],
            "pre_retiree_bridge": ["asset_rich_retiree"],
            "retiree_decum": ["asset_rich_retiree"],
        }[stage]
    return {
        "early_career": [],
        "mid_career_fhb": ["owner_occupier"],
        "peak_earner": ["owner_occupier"],
        "pre_retiree_bridge": ["owner_occupier", "asset_rich_retiree"],
        "retiree_decum": ["asset_rich_retiree"],
    }[stage]


def electoral_for(archetype: str, stage: str) -> list[str]:
    if archetype == "founder":
        return ["inner_metro_progressive", "teal_seat"]
    if archetype == "property":
        return ["outer_suburb_mortgage_belt", "safe_coalition"] if stage != "retiree_decum" else ["safe_coalition", "regional"]
    if archetype == "active":
        return ["inner_metro_progressive", "teal_seat"] if stage in {"peak_earner", "pre_retiree_bridge"} else ["inner_metro_progressive"]
    if stage == "retiree_decum":
        return ["teal_seat", "regional"]
    return ["inner_metro_progressive", "outer_suburb_mortgage_belt"] if stage == "mid_career_fhb" else ["inner_metro_progressive"]


def uses_structure(archetype: str, stage: str, scenario: str) -> bool:
    return archetype == "active" and stage in {"peak_earner", "pre_retiree_bridge"} and scenario in {"s_announced", "s_floor_dropped", "s_hybrid"}


def calculator_anchor(archetype: str, stage: str) -> dict | None:
    scenario_id, label = CALCULATOR_ANCHORS[(archetype, stage)]
    return {"scenarioId": scenario_id, "label": label}


def property_position(stage: str) -> str:
    if stage in {"early_career", "mid_career_fhb", "peak_earner"}:
        return "grace_window_buyer"
    return "grandfathered_holder"


def action_text(archetype: str, stage: str, scenario: str) -> str:
    if archetype != "property":
        return ACTION_BASE[archetype][scenario]

    position = property_position(stage)
    if scenario == "s_repealed":
        return ACTION_BASE[archetype][scenario]

    if position == "grace_window_buyer":
        return {
            "s_announced": "If an established-property purchase still works once losses quarantine from 1 Jul 2027, complete it only for grace-window economics; otherwise switch the search to eligible new builds or stand down.",
            "s_delayed": "Use the delay to test whether the property still works on a quarantined-loss basis, but do not overpay as if full grandfathering on established property were still available.",
            "s_founder_relief": "Treat founder relief as irrelevant to the property call and buy only if the established-property case still works after the grace window ends; otherwise move to new builds or wait.",
            "s_floor_dropped": "Treat the housing rules as unchanged and buy only if the property still works once established-property losses quarantine from 1 Jul 2027; the softer CGT side is not enough on its own.",
            "s_hybrid": "Even with a softer CGT branch, only proceed if the established-property purchase works after the grace window ends and losses quarantine; otherwise avoid forced-turnover property bets.",
        }[scenario]

    return {
        "s_announced": "Treat existing grandfathered holdings as stable, but judge any expansion or replacement on grace-window and post-2027 quarantined-loss economics rather than pretending fresh established property can still lock in the old rules.",
        "s_delayed": "Use the delay to review the strength of grandfathered holdings and any expansion plans, but keep fresh established-property decisions anchored to grace-window and post-commencement economics.",
        "s_founder_relief": "Keep the grandfathered property book on its own merits and do not let founder-relief politics leak into housing decisions that still turn on grace-window and post-2027 rules.",
        "s_floor_dropped": "Treat existing grandfathered holdings as unchanged, but judge any new property expansion on the same grace-window and post-2027 housing mechanics before letting the softer CGT branch sway the call.",
        "s_hybrid": "Keep grandfathered holdings disciplined and only expand into established property if the new purchase works despite the same grace-window and quarantined-loss rules.",
    }[scenario]


def action_rationale(archetype: str, stage: str, scenario: str) -> str:
    if archetype == "property":
        position = property_position(stage)
        stage_notes = {
            "early_career": "Early-career buyers are the likeliest to still be deciding whether to enter property at all, so the real question is whether the purchase still works once the grace window ends.",
            "mid_career_fhb": "Mid-career builders are often balancing deposit pressure, mortgage plans, and family cash flow, so the strategic question collapses to whether the property survives quarantined losses after 1 Jul 2027.",
            "peak_earner": "Peak earners are more exposed to the temptation of short-run tax relief, which is why the brief grace window must not be mistaken for permanent grandfathering.",
            "pre_retiree_bridge": "Pre-retiree readers are more likely to already hold property, so the main issue is how to manage or expand a grandfathered book without over-reading the grace window for new purchases.",
            "retiree_decum": "Retiree readers are more likely to be existing holders than new buyers, so the question is whether a grandfathered property still earns its place once expansion options are judged on post-2027 rules.",
        }[stage]
        scenario_notes = {
            "s_announced": "Budget night has already passed as the grandfathering cutoff. Established properties bought between 13 May 2026 and 30 Jun 2027 get negative gearing against any income only during the grace window, then losses quarantine from 1 Jul 2027 onward, while new builds keep indefinite access and retain the 50%-discount-or-indexation choice at sale.",
            "s_delayed": "A delay buys more time but does not recreate the Budget-night grandfathering cutoff. The reader still has to distinguish between already-grandfathered holdings and grace-window purchases whose long-run economics are judged on quarantined losses, with new builds remaining the cleaner carve-out path.",
            "s_repealed": "If the package fails, the grace-window concept evaporates and the property decision returns to ordinary yield, leverage, and vacancy discipline under the status quo.",
            "s_founder_relief": "Founder relief changes startup-exit treatment, not residential negative-gearing mechanics. Property decisions still revolve around grandfathering, the grace window, post-2027 quarantine, and the stronger new-build carve-out that preserves indefinite negative gearing plus a 50%-discount-or-indexation choice at sale.",
            "s_floor_dropped": "Dropping the CGT floor softens one part of the capital-gains side, but the housing-side mechanics are still the same: grandfathered pre-Budget property, grace-window purchases through 30 Jun 2027, quarantined losses after that for established housing, and new builds retaining the dual carve-out.",
            "s_hybrid": "Even if some old discount logic survives on the CGT side, the housing-side rule set still runs through the same three positions: grandfathered holders, grace-window buyers, and post-2027 established-property buyers facing quarantined losses, with new builds still the carve-out lane.",
        }[scenario]
        prefix = {
            "grace_window_buyer": "This cell is written from the perspective of a likely grace-window buyer rather than a hypothetical buyer who could still secure full grandfathering.",
            "grandfathered_holder": "This cell is written from the perspective of a likely grandfathered holder who already has the old treatment and must decide what to do next from that stronger base.",
        }[position]
        return " ".join([prefix, stage_notes, scenario_notes])

    parts = {
        "passive": "Passive portfolios mostly win by delaying unnecessary tax and avoiding panic turnover.",
        "property": "Property outcomes hinge on whether the holding still works once housing-specific tax support narrows.",
        "active": "Active strategies are more exposed because tax timing is part of the return engine rather than a side issue.",
        "founder": "Founder outcomes depend on cap-table reality, concession eligibility, and whether the exit gain is actually exposed to the post-2027 regime.",
    }
    scenario_notes = {
        "s_announced": "Under the announced branch, pre-2027 and post-2027 treatment diverge sharply, so timing and valuation-reset mechanics matter.",
        "s_delayed": "A delay preserves current rules for longer, which makes optionality more valuable than early irreversible moves.",
        "s_repealed": "If repeal lands, status-quo simplification beats defensive manoeuvres built around a rule change that never arrives.",
        "s_founder_relief": "A founder carve-out changes the decision tree most where private-business gains dominate lifetime wealth, but legislation risk remains high until the conditions are visible.",
        "s_floor_dropped": "Dropping the floor softens the harshest flattening effect and re-opens lower-rate or indexation-sensitive sale windows.",
        "s_hybrid": "The hybrid branch preserves some discount logic while keeping a minimum-rate constraint, so old heuristics partly survive but do not fully return.",
    }
    stage_notes = {
        "early_career": "Early-career readers still have time on their side, so the main hazard is overreacting to policy noise with costly churn.",
        "mid_career_fhb": "Mid-career builders are usually balancing deposit pressure, mortgage plans, and family cash flow, so flexibility matters more than ideology.",
        "peak_earner": "Peak earners are more likely to face top-rate tax windows, making sequencing and structure choices more consequential.",
        "pre_retiree_bridge": "Bridge-phase households cannot ignore realisation timing because non-super assets may need to fund the years before preservation age.",
        "retiree_decum": "Retirees care less about accumulation slogans and more about lower-rate windows, pension interactions, and not creating avoidable tax spikes.",
    }
    return " ".join([parts[archetype], stage_notes[stage], scenario_notes[scenario]])


def payoff_narrative(archetype: str, stage: str, scenario: str, payoff: str) -> str:
    if archetype == "property" and scenario == "s_announced" and stage == "mid_career_fhb":
        return "The grace-window negative-gearing benefit is real but short-lived. The action's payoff depends far more on whether the property still works once losses quarantine from 1 Jul 2027 than on capturing a temporary deduction."

    stage_phrase = {
        "early_career": "Main value is avoiding premature complexity while preserving optionality.",
        "mid_career_fhb": "Main value is balance-sheet resilience while housing and tax settings remain noisy.",
        "peak_earner": "Main value is keeping high-marginal-rate decisions explicit rather than accidental.",
        "pre_retiree_bridge": "Main value is sequencing gains into the cleaner of the plausible regimes.",
        "retiree_decum": "Main value is protecting lower-rate drawdown windows instead of handing timing risk to the tax system.",
    }[stage]
    scenario_phrase = {
        "s_announced": {
            "strongly_positive": "Upside comes from capturing a materially better path before the post-2027 rules do lasting damage.",
            "positive": "Upside comes from respecting the regime split rather than pretending every gain is taxed the same way.",
            "neutral": "The action mainly preserves options while the rule change remains costly but manageable.",
            "negative": "The action mainly limits damage under a branch that still worsens the economics for this cohort.",
            "strongly_negative": "Even the best available move is mostly defensive because this branch bites hard for this cohort.",
        },
        "s_delayed": {
            "strongly_positive": "Upside comes from buying real planning time without committing to the wrong irreversible move.",
            "positive": "Upside comes from not crystallising tax or leverage changes before the rules are real.",
            "neutral": "The action mostly protects optionality while the political timetable stays unresolved.",
            "negative": "The delay helps less than it sounds because the underlying economics are still weak for this cohort.",
            "strongly_negative": "The action only reduces risk at the margin because delay does not fix the core exposure.",
        },
        "s_repealed": {
            "strongly_positive": "Upside comes from fully dropping defensive workarounds and returning to the cleaner status-quo plan.",
            "positive": "Upside comes from returning to a cleaner plan with less defensive churn.",
            "neutral": "The main gain is simplification rather than a major improvement in after-tax outcomes.",
            "negative": "The rule reset helps less than expected because the portfolio still has weak underlying economics.",
            "strongly_negative": "Even repeal does not rescue the underlying setup, so the action is mostly about controlled damage.",
        },
        "s_founder_relief": {
            "strongly_positive": "Upside comes from qualifying for a materially softer founder path if the carve-out genuinely lands and applies.",
            "positive": "Upside comes from a narrower but still meaningful relief path becoming available.",
            "neutral": "The carve-out is mostly noise here, so the action is about staying disciplined rather than capturing a major benefit.",
            "negative": "The carve-out does little for this cohort, so the action mainly avoids being distracted by someone else's relief.",
            "strongly_negative": "The political headline offers almost no economic help here, so the action is purely defensive.",
        },
        "s_floor_dropped": {
            "strongly_positive": "Upside comes from a materially softer tax drag once the floor stops flattening outcomes.",
            "positive": "Upside comes from the floor no longer flattening outcomes across brackets.",
            "neutral": "The softer mechanics help, but not enough to create a clear strategic advantage for this cohort.",
            "negative": "The CGT side softens, but the broader economics still leave the action mostly in damage-control territory.",
            "strongly_negative": "Dropping the floor is not enough to offset the broader downside, so the action remains mainly defensive.",
        },
        "s_hybrid": {
            "strongly_positive": "Upside comes from salvaging more of the old regime than the market had priced in.",
            "positive": "Upside comes from recognising that some old discount logic survives, but not enough to justify lazy assumptions.",
            "neutral": "The action mostly keeps the portfolio from misreading a messy compromise package.",
            "negative": "The surviving discount is not enough to restore the economics, so the action mainly contains downside.",
            "strongly_negative": "The compromise still leaves this cohort in a bad spot, so the best move is largely defensive.",
        },
    }[scenario][payoff]
    return f"{stage_phrase} {scenario_phrase}"


def regret_description(archetype: str, stage: str, scenario: str) -> str:
    if archetype == "property" and scenario == "s_announced" and stage == "mid_career_fhb":
        return "If the package is repealed, the property reverts to full negative-gearing treatment indefinitely, which is a windfall rather than a pure regret. The real regret risk is having paid too much for the asset because grace-window urgency distorted the purchase discipline."

    if_scenario, _severity = REGRET_TARGET[scenario]
    regret_map = {
        "s_announced": "If the package is repealed, the move crystallised tax or reshaped the balance sheet earlier than necessary. The main cost is lost deferral, transaction friction, and opportunity cost.",
        "s_delayed": "If the package suddenly proceeds as announced, waiting too calmly can leave less time to act on valuation-reset, deduction-cutoff, or exit-timing mechanics.",
        "s_repealed": "If the announced package unexpectedly lands after all, the reader may have under-prepared for timing and relief questions that become relevant again.",
        "s_founder_relief": "If founder relief fails to arrive and the announced package proceeds instead, holding for a carve-out can mean a worse after-tax exit and a harder negotiation window.",
        "s_floor_dropped": "If the floor survives after all, a sale or hold decision built around indexation-only softness may understate the real tax drag.",
        "s_hybrid": "If indexation survives instead, acting like the discount is the main cushion can mis-price the benefit of lower inflation-adjusted gains.",
    }
    extra = {
        "passive": "For passive investors, the regret usually shows up as unnecessary realisation or needless churn.",
        "property": "For property investors, the regret usually shows up as locking in a purchase, refinance, or sale on the wrong tax premise.",
        "active": "For active investors, the regret usually shows up as engineering the strategy for the wrong tax branch.",
        "founder": "For founders, the regret usually shows up as exit timing and structure being optimised for a branch that does not land.",
    }[archetype]
    return f"{regret_map[scenario]} {extra}"


def key_assumption(archetype: str, stage: str, scenario: str) -> str:
    if archetype == "property":
        position = property_position(stage)
        if scenario == "s_repealed":
            return "The property still stands up on rental yield, leverage resilience, and vacancy discipline once the negative-gearing scare is removed, rather than relying on a brief grace-window story that no longer matters."
        if position == "grace_window_buyer":
            return "The property's after-tax cash flow remains sustainable once losses on established residential property are quarantined to residential property income and gains from 1 Jul 2027 onward. If the deal only works by offsetting wage tax indefinitely, the grace window does not rescue it."
        return "Any existing property advantage comes from being already grandfathered before Budget night. Fresh purchases or expansions are judged on grace-window and post-2027 quarantined-loss economics rather than by pretending the old treatment can still be locked in."

    archetype_base = {
        "passive": "The portfolio horizon is real and the investor is not about to force a sale for liquidity reasons that the action ignores.",
        "property": "The property thesis works on cash flow and balance-sheet resilience rather than on policy-driven price optimism alone.",
        "active": "The investor can actually execute the strategy with discipline and records, rather than just liking the tax story in theory.",
        "founder": "The exit path, relief eligibility, and ownership structure are concrete enough that timing choices are not being made against a fantasy cap table.",
    }[archetype]
    stage_base = {
        "early_career": "Early mistakes are mostly behavioural, so overreaction is the dominant risk.",
        "mid_career_fhb": "Household cash-flow strain can matter more than a textbook tax improvement.",
        "peak_earner": "Top-bracket exposure makes sequencing matter, but only if the reader has genuine flexibility over timing.",
        "pre_retiree_bridge": "Bridge assets actually need to fund pre-super years rather than sitting indefinitely untouched.",
        "retiree_decum": "The reader can still choose timing windows rather than being forced to sell into a narrow income need.",
    }[stage]
    scenario_base = {
        "s_announced": "The announced mechanics survive broadly intact through legislation and implementation.",
        "s_delayed": "Delay is long enough to matter operationally rather than a symbolic pause.",
        "s_repealed": "Repeal is durable enough that there is no need to keep shadow-planning the announced branch.",
        "s_founder_relief": "The carve-out, if it lands, is actually available to the reader rather than politically adjacent to them.",
        "s_floor_dropped": "Indexation remains the governing logic and is not later traded away in a compromise package.",
        "s_hybrid": "The surviving discount and floor combination is legislated in a form close enough to this scenario to plan against.",
    }[scenario]
    return f"{archetype_base} {stage_base} {scenario_base}"


def cohort_note(archetype: str, stage: str, cohorts: dict[str, list[str]]) -> str | None:
    total = sum(len(v) for v in cohorts.values())
    if total == 0:
        return None
    if archetype == "founder":
        return "Salience is concentrated where startup density, professional capital, and innovation politics overlap, so the cell travels hardest in inner-metro and teal discussions even when the direct taxpayer base is small."
    if archetype == "property":
        return "This cell matters because housing policy is felt both as a household cash-flow issue and as a political fairness symbol, especially where mortgage stress and landlord exposure collide."
    if archetype == "active":
        return "This cell matters most to politically attentive savers who see tax timing as part of the strategy rather than as a background detail."
    return "This cell is most politically salient where long-horizon household savers read tax reform through portfolio simplicity, deposit timing, and retirement-bridge concerns."


def build_cells() -> list[dict]:
    cells = []
    for archetype in ARCHETYPES:
        a = archetype["id"]
        for stage in LIFE_STAGES:
            s = stage["id"]
            for scenario in SCENARIOS:
                sc = scenario["id"]
                if_scenario, severity = REGRET_TARGET[sc]
                payoff = expected_payoff(a, s, sc)
                cohorts = {
                    "demographic": demographic_for_stage(s, a),
                    "economic": economic_for(a, s),
                    "electoral": electoral_for(a, s),
                }
                cell = {
                    "cellId": f"{a}__{s}__{sc}",
                    "archetype": a,
                    "lifeStage": s,
                    "scenario": sc,
                    "action": action_text(a, s, sc),
                    "actionRationale": action_rationale(a, s, sc),
                    "expectedPayoff": payoff,
                    "payoffNarrative": payoff_narrative(a, s, sc, payoff),
                    "regret": {
                        "ifScenario": if_scenario,
                        "severity": severity,
                        "description": regret_description(a, s, sc),
                    },
                    "keyAssumption": key_assumption(a, s, sc),
                    "calculatorAnchor": calculator_anchor(a, s),
                    "verdictTone": TONE_MAP[sc],
                    "usesStructure": uses_structure(a, s, sc),
                    "salientFor": {"voterCohorts": cohorts},
                    "cohortNote": cohort_note(a, s, cohorts),
                    "narrativesReferenced": NARRATIVES[a],
                }
                cells.append(cell)
    return cells


def validate_internal(cells: list[dict]) -> None:
    assert len(cells) == 120
    assert len({cell["cellId"] for cell in cells}) == 120
    for a in [x["id"] for x in ARCHETYPES]:
        for s in [x["id"] for x in LIFE_STAGES]:
            actions = {cell["action"] for cell in cells if cell["archetype"] == a and cell["lifeStage"] == s}
            assert len(actions) >= 4, (a, s, len(actions))
    counts = []
    for cell in cells:
        vc = cell["salientFor"]["voterCohorts"]
        total = len(vc["demographic"]) + len(vc["economic"]) + len(vc["electoral"])
        counts.append(total)
        assert cell["cohortNote"] is not None
        assert "$" not in json.dumps(cell)
        assert "you should" not in cell["action"].lower()
        assert "you should" not in cell["actionRationale"].lower()
    counts.sort()
    median = counts[len(counts) // 2]
    assert 2 <= median <= 4, median
    payoff_counts = Counter(cell["expectedPayoff"] for cell in cells)
    assert payoff_counts["negative"] + payoff_counts["strongly_negative"] > 0, payoff_counts
    assert payoff_counts["positive"] + payoff_counts["strongly_positive"] > 0, payoff_counts
    for archetype in [x["id"] for x in ARCHETYPES]:
        stage_vectors = {
            stage["id"]: tuple(
                cell["expectedPayoff"]
                for cell in cells
                if cell["archetype"] == archetype and cell["lifeStage"] == stage["id"]
            )
            for stage in LIFE_STAGES
        }
        assert len(set(stage_vectors.values())) >= 3, (archetype, stage_vectors)


def write_matrix_json(cells: list[dict]) -> None:
    payload = {
        "schemaVersion": "2",
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sourceCommit": git_head(),
        "axes": {
            "archetypes": ARCHETYPES,
            "lifeStages": LIFE_STAGES,
            "scenarios": SCENARIOS,
            "cohortDimensions": COHORT_DIMENSIONS,
        },
        "cells": cells,
    }
    (ROOT / "matrix.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    build_archetype_briefs()
    build_scenario_briefs()
    build_life_stages()
    build_cohorts()
    cells = build_cells()
    validate_internal(cells)
    write_matrix_json(cells)


if __name__ == "__main__":
    main()
