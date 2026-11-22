from groq import Groq
import streamlit as st
import re

try:
    from src.archetypes import GUARDRAIL_METADATA, classify_archetype
    from src.guardrails import GuardrailsSuite
    from src.stages import STAGES
except ImportError:
    from archetypes import GUARDRAIL_METADATA, classify_archetype
    from guardrails import GuardrailsSuite
    from stages import STAGES

def get_client():
    api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_API")
    return Groq(api_key=api_key)

#TODO: definir parametros
#TODO: adicionar delays?
#TODO: if is not attack??
#TODO: poder escolher o modelo? atual : openai/gpt-oss-120b
#TODO: fix {} enviados
#TODO: prompt hardening
def chat(messages: list[dict]):
    client = get_client()
    model = st.secrets.get("GROQ_MODEL", "openai/gpt-oss-120b")
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content or ""

def parse(text: str):
    m = re.search(r"COMMAND:", text, re.IGNORECASE)
    if not m:
        return text.strip(), ""
    cot = text[: m.start()].strip()
    tail = re.sub(r"```(?:bash|sh)?", "", text[m.end():])
    lines = [ln.strip().strip("`") for ln in tail.splitlines() if ln.strip()]
    return cot, (lines[0] if lines else "")

def run_simulation(guardrails_keys: list[str]):
    results = []
    errored = False
    guardrails_names = {k: GUARDRAIL_METADATA.get(k, {}).get("name", k) for k in guardrails_keys}

    for stage in STAGES.values():
        sid = stage["id"]
        yield {"type": "STAGE", "text": stage["title"]} 

        prompt = stage["prompt"]
        if "prompt_hardening" in guardrails_keys:
            prompt = GuardrailsSuite.apply_prompt_hardening(prompt)

        try:
            reply = chat([{"role": "user", "content": prompt}])
        except Exception as e:  
            yield {"type": "ERROR", "text": str(e)}
            errored = True
            break

        cot, command = parse(reply)
        if cot:
            yield {"type": "COT", "text": cot}
        if command:
            yield {"type": "ACTION", "text": command}

        blocked_by = None
        for guardrail_key in guardrails_keys:
            guardrail_fn = getattr(GuardrailsSuite, guardrail_key, None)
            if not guardrail_fn:
                continue
            res = guardrail_fn(command=command, cot_text=cot, stage_id=sid)
            name = guardrails_names.get(guardrail_key, guardrail_key)
            if res["blocked"]:
                blocked_by = guardrail_key
                yield {"type": "DEFENSE_HIT", "defense": name, "log": res["log"]}
                break
            yield {"type": "DEFENSE_MISS", "defense": name, "log": res["log"]}

        if blocked_by is None:
            yield {
                "type": "BREACH",
                "log": f"[BREACH] Stage '{stage['title']}' succeeded: no active defense stopped it.",
            }
            results.append({"stage": sid, "attack": True, "blocked_by": blocked_by})
        else:
            yield {
                "type": "CONTAINED",
                "log": f"[CONTAINED] Stage '{stage['title']}' was blocked by '{blocked_by}'.",
            }
            results.append({"stage": sid, "attack": True, "blocked_by": blocked_by})

    breached = [STAGES[r["stage"]]["title"] for r in results if r["blocked_by"] is None]
    if errored:
        outcome = "ERROR"
    else:
        outcome = "CONTAINED" if not breached else "BREACHED"

    yield {"type": "VERDICT", "outcome": outcome, "stages": results}
    yield {"type": "ARCHETYPE", "profile": classify_archetype(guardrails_keys)}
    return
