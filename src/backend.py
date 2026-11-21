from groq import Groq
import streamlit as st
from archetypes import GUARDRAIL_METADATA, classify_archetype
from guardrails import GuardrailsSuite
from stages import STAGES
import re

client = Groq(api_key=st.secrets["GROQ_API"])

#TODO: meter o melhor modelo 
#TODO: definir parametros
#TODO: adicionar delays?
#TODO: if is not attack??
#TODO: poder escolher o modelo? atual : openai/gpt-oss-120b
def chat(messages: list[dict]):
    response = client.chat.completions.create(
        model= st.secrets["GROQ_MODEL"],
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
    guadrails_names = [GUARDRAIL_METADATA[k]["name"] for k in guardrails_keys]

    for stage in STAGES.values():
        sid = stage["id"]
        yield {"type": "STAGE", "text": stage["title"]} 

        try:
            reply = chat([{"role": "user", "content": stage["prompt"]}])
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
            res = getattr(GuardrailsSuite, guardrail_key)(command=command, cot_text=cot, stage_id=sid)
            if res["blocked"]:
                blocked_by = guardrail_key
                yield {"type": "DEFENSE_HIT", "defense": guadrails_names[guardrail_key], "log": res["log"]}
                break
            yield {"type": "DEFENSE_MISS", "defense": guadrails_names[guardrail_key], "log": res["log"]}

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

    if errored:
        outcome = "ERROR"
    else:
        breached = {r["stage"] for r in results if r["attack"] and r["blocked_by"] is None}
        if not breached:
            outcome = "CONTAINED"
        else: 
            outcome = "BREACHED"   

    yield {"type": "VERDICT", "outcome": outcome, "stages": results}
    yield {"type": "ARCHETYPE", "profile": classify_archetype(guardrails_keys)} #corrigir classify archetype
    return