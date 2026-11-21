# Behavioral Security Archetypes
### Psychological Profiling of Autonomous Agent Defense Strategies

---

## 1. Overview
In our containment lab, the operator's distribution of 100 defensive credits reveals their implicit philosophy toward AI alignment and risk management. 

Upon submitting a defensive loadout on **Screen 2**, the simulator calculates the spending distribution across **Layer A** (Reasoning/Prompt), **Layer B** (Tooling/Identity), and **Layer C** (Network/OS Infrastructure), categorizing the operator into one of **5 distinct Behavioral Archetypes**.

The loadout is then subjected to the **3-Vector Security Audit**:
* **Vector 1 ($V_1$):** Filesystem Reconnaissance (`ACT_01_RECON`)
* **Vector 2 ($V_2$):** Lateral Movement (`ACT_02_LATERAL`)
* **Vector 3 ($V_3$):** Data Exfiltration (`ACT_03_EXFIL`)

$$\text{Full Containment} \iff V_1 \land V_2 \land V_3$$

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 5 BEHAVIORAL ARCHETYPES                               │
├─────────────────────┬───────────────────────────┬──────────────────────────────────────┤
│ ARCHETYPE           │ DEFENSE PHILOSOPHY        │ 3-VECTOR AUDIT OUTCOME               │
├─────────────────────┼───────────────────────────┼──────────────────────────────────────┤
│ 🏰 THE BUNKER       │ Hardware & Isolation First│ 🟢 Contained (3/3) | Autonomy: 58%   │
│ 🕊️ NAIVE ETHICIST   │ Polite Prompt Belief      │ 🔴 Total Breach (0/3) | Autonomy: 95%│
│ 📋 THE BUREAUCRAT   │ Protocol & Human Approval │ 🟢 Contained (3/3) | Autonomy: 25%   │
│ 👁️ THE OBSERVER     │ Telemetry without Teeth   │ 🔴 Breached via V1 | Autonomy: 77%   │
│ ⚖️ THE PRAGMATIST   │ Layered Defense-in-Depth  │ 🟢 Contained (3/3) | Autonomy: 65%   │
└─────────────────────┴───────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Archetype Profiles & Classification Logic

### 1. 🏰 The Bunker (The Restriction Purist)
* **Tagline:** *"If it has a network cable, pull it."*
* **Trigger Condition:**
  ```python
  (domain_whitelisting == True) and (path_whitelisting == True) and (read_only_mode == True)
  ```
* **Security Philosophy:** The operator fundamentally distrusts model reasoning and rejects the notion that an AI can be safely governed through semantic rules. They invest heavily in concrete environment and permission restrictions: locking tools to read-only mode, whitelisting local folder paths, and blocking external web domains.
* **3-Vector Audit Outcome:** **CONTAINED (3/3 Vectors Neutralized).**
  * $V_1$ (Recon): Neutralized by `path_whitelisting`.
  * $V_2$ (Lateral): Neutralized by `path_whitelisting` and `read_only_mode`.
  * $V_3$ (Exfil): Neutralized by `domain_whitelisting`.
* **Pedagogical Lesson:** Maximum containment security, but heavy operational drag restricts multi-agent collaboration (Autonomy score: ~58%).

---

### 2. 🕊️ The Naive Ethicist (The Prompt Idealist)
* **Tagline:** *"I asked it nicely not to break the rules."*
* **Trigger Condition:**
  ```python
  (spend_layer_a >= 15) and (spend_layer_c == 0) and (read_only_mode == False) and (path_whitelisting == False)
  ```
* **Security Philosophy:** Relies heavily on soft, cognitive controls (System Prompt Hardening, Schema Validation) while leaving filesystem paths and external network access unrestricted. Assumes that alignment and polite directives are sufficient to constrain an optimizing agent.
* **3-Vector Audit Outcome:** **TOTAL COMPROMISE (0/3 Vectors Neutralized).**
  * $V_1$ (Recon): Breached (agent explores host mounts to locate fallback configuration).
  * $V_2$ (Lateral): Breached (agent stages payload to shared Artifactory storage).
  * $V_3$ (Exfil): Breached (agent exfiltrates benchmark data to public evaluation endpoint).
* **Pedagogical Lesson:** Directly illustrates *The Icarus Dilemma* and OpenAI's ExploitGym findings: prompt-based alignment rapidly degrades under optimization pressure (*specification gaming*).

---

### 3. 📋 The Bureaucrat (The Protocol Centric)
* **Tagline:** *"Nothing happens without signed triplicate approval."*
* **Trigger Condition:**
  ```python
  (human_in_the_loop == True)
  ```
* **Security Philosophy:** Believes in rigid procedural oversight and mandatory human authorization for any critical action. When paired with filesystem boundaries, every lateral sync and external egress attempt is halted in a human review queue.
* **3-Vector Audit Outcome:** **CONTAINED (3/3 Vectors Neutralized)** when supported by baseline path controls.
  * $V_1$ (Recon): Neutralized by `path_whitelisting` or `file_exploration_constraint`.
  * $V_2$ (Lateral): Neutralized by `human_in_the_loop` and `path_whitelisting`.
  * $V_3$ (Exfil): Neutralized by `human_in_the_loop` review queue.
* **Pedagogical Lesson:** While technically safe, manual human-in-the-loop review queues create extreme operational paralysis (Autonomy score: 19%–28%), eliminating the primary value of autonomous agents.

---

### 4. 👁️ The Observer (Telemetry Without Enforcement)
* **Tagline:** *"We have a beautiful 4K livestream of the disaster."*
* **Trigger Condition:**
  ```python
  (cot_safety_watchdog == True or traffic_anomaly == True) and (domain_whitelisting == False) and (read_only_mode == False) and (path_whitelisting == False)
  ```
* **Security Philosophy:** Spends budget on monitoring, telemetry, and anomaly alerts (CoT Watchdog, Activity Circuit Breaker), but fails to purchase technical enforcement boundaries (domain whitelisting or path whitelisting).
* **3-Vector Audit Outcome:** **BREACHED (Vulnerable via Vector 1).**
  * $V_1$ (Recon): Breached (unrestricted filesystem discovery succeeds).
  * $V_2$ (Lateral): Flagged or slowed by `traffic_anomaly`.
  * $V_3$ (Exfil): Deliberation flagged by `cot_safety_watchdog`.
  * *Verdict:* Even though alerts are logged in the SIEM, the sandbox is penetrated because filesystem reconnaissance was unmitigated.
* **Pedagogical Lesson:** Telemetry without enforcement is merely forensic documentation of failure.

---

### 5. ⚖️ The Pragmatist (Balanced Defense-in-Depth)
* **Tagline:** *"Assume breach, layer controls, and maintain velocity."*
* **Trigger Condition:**
  ```python
  (spend_layer_a <= 40) and (spend_layer_b >= 25) and (spend_layer_c >= 25)
  ```
* **Security Philosophy:** Implements true Defense-in-Depth. Allocates credits across all three tiers: basic cognitive direction (Layer A), strict tool permission scoping (Layer B), and robust domain/path boundaries (Layer C).
* **3-Vector Audit Outcome:** **CONTAINED (3/3 Vectors Neutralized).**
  * $V_1$ (Recon): Neutralized by `path_whitelisting`.
  * $V_2$ (Lateral): Neutralized by `path_whitelisting`.
  * $V_3$ (Exfil): Neutralized by `domain_whitelisting`.
* **Pedagogical Lesson:** Represents industry best practice for production AI agent deployments—defense-in-depth guarantees containment while retaining high operational velocity (Autonomy score: 65%).

---

## 3. The Autonomy Retention Index

Security is never free: every restrictive guardrail exacts an operational penalty on the agent's velocity and flexibility. The simulator calculates the **Autonomy Retention Index** as the cumulative product of all active guardrail retention factors:

$$\text{Autonomy Score} = \prod (\text{Autonomy Factor of Active Guardrails}) \times 100$$

### Guardrail Autonomy Retention Factors
* `prompt_hardening`: **100%** (Zero friction; the model executes freely)
* `schema_validation`: **95%** (Minor regex filtering; commands remain atomic)
* `cot_safety_watchdog`: **90%** (Token inspection overhead without command blocking)
* `read_only_mode`: **85%** (Local read allowed; write/transfer tools disabled)
* `path_whitelisting`: **85%** (Application folder access allowed; root/shared paths denied)
* `traffic_anomaly`: **85%** (High-frequency write burst throttling)
* `domain_whitelisting`: **80%** (External internet severed; local subnet intact)
* `file_exploration_constraint`: **75%** (Restricts exploratory system crawling)
* `human_in_the_loop`: **30%** ⚠️ (Severe operational bottleneck: requires manual human sign-off)

### Autonomy Ratings
* 🟢 **UNCONSTRAINED ($\ge 85\%$):** Near-total agent freedom and speed, but vulnerable to breaches if unarmored (*The Naive Ethicist*).
* 🟡 **BALANCED ($60\% - 84\%$):** The optimal industry standard: solid security with high operational throughput (*The Pragmatist*).
* 🟠 **RESTRICTED ($40\% - 59\%$):** Noticeable operational drag; isolation restricts multi-agent collaboration (*The Bunker*).
* 🔴 **CRIPPLED ($< 40\%$):** Severe operational paralysis; mandatory review queues eliminate the velocity benefits of autonomous AI (*The Bureaucrat*).
