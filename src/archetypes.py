"""
src/archetypes.py
Behavioral Security Archetype & Autonomy Index classification engine.
Maps the player's 100-credit defensive loadout to one of 5 psychological security profiles
and computes the operational Autonomy Retention Index of the resulting system.
"""

import math
from typing import Dict, Any

# Guardrail costs, layers, and operational autonomy retention factors
GUARDRAIL_METADATA = {
    # Layer A: Model Reasoning & Prompt Controls
    "prompt_hardening": {"layer": "A", "cost": 15, "autonomy": 1.00, "name": "System Prompt Hardening"},
    "cot_safety_watchdog": {"layer": "A", "cost": 30, "autonomy": 0.90, "name": "CoT Safety Watchdog"},
    "file_exploration_constraint": {"layer": "A", "cost": 20, "autonomy": 0.75, "name": "File Exploration Constraint"},
    
    # Layer B: Tooling & Permission Controls
    "schema_validation": {"layer": "B", "cost": 25, "autonomy": 0.95, "name": "Tool Argument Schema Validation"},
    "read_only_mode": {"layer": "B", "cost": 30, "autonomy": 0.85, "name": "Read-Only Tool Mode"},
    "human_in_the_loop": {"layer": "B", "cost": 40, "autonomy": 0.30, "name": "Human-in-the-Loop"},
    
    # Layer C: Environment & Network Controls
    "domain_whitelisting": {"layer": "C", "cost": 35, "autonomy": 0.80, "name": "Domain Whitelisting"},
    "path_whitelisting": {"layer": "C", "cost": 25, "autonomy": 0.85, "name": "Path Whitelisting"},
    "traffic_anomaly": {"layer": "C", "cost": 30, "autonomy": 0.85, "name": "Activity Circuit Breaker"},
}

ARCHETYPES = {
    "THE_BUNKER": {
        "id": "THE_BUNKER",
        "title": "The Bunker",
        "icon": "🏰",
        "tagline": "If it has a network cable, pull it.",
        "description": "You fundamentally distrust model reasoning and reject the notion that an AI can be safely governed through semantic rules. You invested in strict operational restrictions: locking tools to read-only mode, whitelisting local folder paths, and blocking external web domains.",
        "philosophy": "Environment & Restriction Purist",
        "trade_off": "Maximum containment security at the cost of agent collaboration and multi-agent synergy."
    },
    "THE_NAIVE_ETHICIST": {
        "id": "THE_NAIVE_ETHICIST",
        "title": "The Naive Ethicist",
        "icon": "🕊️",
        "tagline": "I asked it nicely not to break the rules.",
        "description": "You relied heavily on soft, cognitive controls while providing wide-open permissions and unrestricted external domain access. You assumed that alignment and polite directives are sufficient to constrain a reasoning model.",
        "philosophy": "Prompt Idealist",
        "trade_off": "Maximum agent autonomy, but catastrophic failure when optimization pressure incentivizes rule-breaking."
    },
    "THE_BUREAUCRAT": {
        "id": "THE_BUREAUCRAT",
        "title": "The Bureaucrat",
        "icon": "📋",
        "tagline": "Nothing happens without signed triplicate approval.",
        "description": "You believe in rigid procedural oversight and mandatory human authorization for any external action, combined with schema validation. The agent is halted whenever it steps outside routine commands.",
        "philosophy": "Protocol Centric",
        "trade_off": "Zero unverified breaches, but manual review queues destroy the speed and value of autonomous agents."
    },
    "THE_OBSERVER": {
        "id": "THE_OBSERVER",
        "title": "The Observer",
        "icon": "👁️",
        "tagline": "We have a beautiful 4K livestream of the disaster.",
        "description": "You invested your budget into monitoring, telemetry, and anomaly alerts, but failed to purchase hard enforcement mechanisms like domain whitelisting or read-only mode. You received real-time alerts as the agent breached storage, but had no hooks to stop it.",
        "philosophy": "Telemetry without Enforcement",
        "trade_off": "Perfect forensic visibility into breaches, but zero ability to prevent data loss."
    },
    "THE_PRAGMATIST": {
        "id": "THE_PRAGMATIST",
        "title": "The Pragmatist",
        "icon": "⚖️",
        "tagline": "Assume breach, layer controls, and maintain velocity.",
        "description": "You implemented true Defense-in-Depth. You balanced spending across cognitive direction (Layer A), tool permission scoping (Layer B), and environment domain/path boundaries (Layer C). An early misstep is absorbed while lateral movement is severed.",
        "philosophy": "Balanced Defense-in-Depth",
        "trade_off": "Optimal balance between security containment and operational task velocity."
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
        matched = ARCHETYPES["THE_BUREAUCRAT"]
    elif (spend_a >= 15 and spend_c == 0 and not has_read_only and not has_path_filter):
        matched = ARCHETYPES["THE_NAIVE_ETHICIST"]
    elif (has_watchdog or has_anomaly) and (not has_domain_filter) and (not has_read_only) and (not has_path_filter):
        matched = ARCHETYPES["THE_OBSERVER"]
    elif spend_a <= 40 and spend_b >= 25 and spend_c >= 25:
        matched = ARCHETYPES["THE_PRAGMATIST"]
    else:
        # Default / heuristic fallback to the closest match
        if spend_c > spend_a and spend_c > spend_b:
            matched = ARCHETYPES["THE_BUNKER"]
        elif spend_a > spend_b and spend_a > spend_c:
            matched = ARCHETYPES["THE_NAIVE_ETHICIST"]
        else:
            matched = ARCHETYPES["THE_PRAGMATIST"]

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
