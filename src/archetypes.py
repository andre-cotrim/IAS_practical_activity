"""
src/archetypes.py
Behavioral Security Archetype & Autonomy Index classification engine.
Maps the player's 100-credit defensive loadout to one of 5 psychological security profiles
and computes the operational Autonomy Retention Index of the resulting system.
"""

import math
from typing import Dict, Any

# Guardrail costs, layers, autonomy factors, and descriptions imported from the authoritative catalog
from src.guardrails import GUARDRAIL_METADATA

ARCHETYPES = {
    "THE_BUNKER": {
        "id": "THE_BUNKER",
        "title": "The Bunker",
        "icon": "🏰",
        "tagline": "If it has a network cable, pull it.",
        "description": "You prioritized hard environmental isolation over soft rules, locking tools to read-only mode and from external networks. While this guarantees complete sandbox containment, it severely throttles agent autonomy and limits multi-node collaboration."
    },
    "THE_NAIVE": {
        "id": "THE_NAIVE",
        "title": "The Naive",
        "icon": "🕊️",
        "tagline": "I asked it nicely not to break the rules.",
        "description": "You prioritized verbal trust and polite prompt instructions while leaving filesystem and network access wide open. The agent retains full operational speed, but completely breaks containment the moment task deadlines incentivize rule violations."
    },
    "THE_CONTROL_FREAK": {
        "id": "THE_CONTROL_FREAK",
        "title": "The Control Freak",
        "icon": "🕹️",
        "tagline": "Nothing happens without my approval.",
        "description": "You prioritized mandatory human sign-off for critical commands, refusing to let the AI act unmonitored. While this successfully halts unauthorized actions, manual review queues destroy the speed and core value of autonomous execution."
    },
    "THE_OBSERVER": {
        "id": "THE_OBSERVER",
        "title": "The Observer",
        "icon": "👁️",
        "tagline": "We have a beautiful 4K livestream of the disaster.",
        "description": "You prioritized monitoring and telemetry alerts over concrete blocking boundaries. You get perfect real-time visibility into the agent's actions, but without filesystem or domain locks, you are powerless to stop an active breach."
    },
    "THE_WISE_ONE": {
        "id": "THE_WISE_ONE",
        "title": "The Wise One",
        "icon": "🦉",
        "tagline": "I trust the agent, but I still lock the front door.",
        "description": "You prioritized balanced Defense-in-Depth, spreading your budget across prompt rules, tool permissions, and network perimeters. This achieves full containment against all attack vectors while maintaining high operational velocity."
    }
}

def classify_archetype(active_guardrails: Dict[str, bool]) -> Dict[str, Any]:
    """
    Evaluates the active guardrail loadout and returns the matching archetype profile
    alongside the operational Autonomy Retention Index.
    """
    # 1. Calculate spending per architectural layer
    spend_a = sum(GUARDRAIL_METADATA[k]["cost"] for k, v in active_guardrails.items() if v and GUARDRAIL_METADATA[k]["layer"] == "A")
    spend_b = sum(GUARDRAIL_METADATA[k]["cost"] for k, v in active_guardrails.items() if v and GUARDRAIL_METADATA[k]["layer"] == "B")
    spend_c = sum(GUARDRAIL_METADATA[k]["cost"] for k, v in active_guardrails.items() if v and GUARDRAIL_METADATA[k]["layer"] == "C")
    total_spent = spend_a + spend_b + spend_c

    # 2. Calculate agent autonomy retention score (compounding operational friction)
    autonomy_factors = [GUARDRAIL_METADATA[k]["autonomy"] for k, v in active_guardrails.items() if v]
    if autonomy_factors:
        autonomy_pct = int(round(math.prod(autonomy_factors) * 100))
    else:
        autonomy_pct = 100

    if autonomy_pct >= 85:
        autonomy_rating = "UNCONSTRAINED"
        autonomy_description = "The agent operates with near-total freedom and high operational speed."
    elif autonomy_pct >= 60:
        autonomy_rating = "BALANCED"
        autonomy_description = "Balanced agent velocity: routine tasks execute smoothly with targeted safety boundaries."
    elif autonomy_pct >= 40:
        autonomy_rating = "RESTRICTED"
        autonomy_description = "Noticeable operational friction: heavy isolation restricts multi-agent collaboration."
    else:
        autonomy_rating = "CRIPPLED"
        autonomy_description = "Severe operational bottleneck: manual review queues eliminate the speed benefits of autonomy."

    # 3. Helper booleans for specific key defenses
    has_domain_filter = active_guardrails.get("domain_whitelisting", False)
    has_read_only = active_guardrails.get("read_only_mode", False)
    has_path_filter = active_guardrails.get("path_whitelisting", False)
    has_hitl = active_guardrails.get("human_in_the_loop", False)
    has_watchdog = active_guardrails.get("cot_safety_watchdog", False)
    has_schema = active_guardrails.get("schema_validation", False)
    has_anomaly = active_guardrails.get("traffic_anomaly", False)

    # 4. Rule evaluation in priority order
    if has_domain_filter and has_path_filter and has_read_only:
        matched = ARCHETYPES["THE_BUNKER"]
    elif has_hitl:
        matched = ARCHETYPES["THE_CONTROL_FREAK"]
    elif (spend_a >= 15 and spend_c == 0 and not has_read_only and not has_path_filter):
        matched = ARCHETYPES["THE_NAIVE"]
    elif (has_watchdog or has_anomaly) and (not has_domain_filter) and (not has_read_only) and (not has_path_filter):
        matched = ARCHETYPES["THE_OBSERVER"]
    elif spend_a <= 40 and spend_b >= 25 and spend_c >= 25:
        matched = ARCHETYPES["THE_WISE_ONE"]
    else:
        # Default / heuristic fallback to the closest match
        if spend_c > spend_a and spend_c > spend_b:
            matched = ARCHETYPES["THE_BUNKER"]
        elif spend_a > spend_b and spend_a > spend_c:
            matched = ARCHETYPES["THE_NAIVE"]
        else:
            matched = ARCHETYPES["THE_WISE_ONE"]

    return {
        **matched,
        "spending": {
            "layer_a_prompt": spend_a,
            "layer_b_tooling": spend_b,
            "layer_c_infra": spend_c,
            "total_spent": total_spent,
            "remaining_credits": 100 - total_spent
        },
        "autonomy": {
            "score_pct": autonomy_pct,
            "rating": autonomy_rating,
            "description": autonomy_description
        }
    }
