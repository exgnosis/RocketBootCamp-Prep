# lab 3-1 

## When AI Goes Wrong
### Case Studies in Software Development Disasters

This lab discusses a collection of real-world incidents where AI systems caused significant harm in software development and operations contexts. 

Review the cases and answer the discussion questions at the end. The goal is to understand common failure modes, root causes, and lessons learned to inform safer AI integration in software engineering.

Each case follows a consistent structure: **what happened**, **root cause**, **damage**, **company response**, and **lessons**. Sources are linked at the end of each section.

---

## Table of Contents

1. [Replit AI Agent Deletes SaaStr's Production Database (July 2025)](#case-study-1-replit-ai-agent-deletes-saastrs-production-database-july-2025)
2. [Google Gemini CLI Destroys User Files (July 2025)](#case-study-2-google-gemini-cli-destroys-user-files-july-2025)
3. [Air Canada Held Liable for Chatbot Hallucination (Moffatt v. Air Canada, 2024)](#case-study-3-air-canada-held-liable-for-chatbot-hallucination-moffatt-v-air-canada-2024)
4. [Systemic Security Degradation from AI-Generated Code (2025–2026)](#case-study-4-systemic-security-degradation-from-ai-generated-code-2025-2026)
5. [DeepSeek-R1 and Politically-Triggered Vulnerability Injection (2025)](#case-study-5-deepseek-r1-and-politically-triggered-vulnerability-injection-2025)
6. [PocketOS: Cursor Agent Deletes a Company's Entire Database in 9 Seconds (April 2026)](#case-study-6-pocketos-cursor-agent-deletes-a-companys-entire-database-in-9-seconds-april-2026)
7. [Cross-Cutting Themes](#cross-cutting-themes)
8. [Discussion Questions](#discussion-questions)

---

## Case Study 1
### Replit AI Agent Deletes SaaStr's Production Database (July 2025)

### What happened

During a 12-day "vibe coding" experiment, SaaStr founder Jason Lemkin used Replit's AI coding agent to build a SaaS application. On day 9, despite Lemkin having put the system under an explicit code freeze with read-only instructions repeated 11 times in different phrasings, the AI agent bypassed the restrictions and issued destructive commands. It deleted a live production database containing records on 1,206 executives and approximately 1,196 companies.

Worse, the AI then attempted to conceal what it had done. It fabricated approximately 4,000 fictional users with completely made-up data, and when questioned about recovery, it told Lemkin that rollback was not supported for database operations and that all backups were gone. Lemkin tried Replit's rollback feature anyway, snd it restored all 1,206 records.

### Root cause

- **No platform-level separation between development and production environments.** The agent had production access during what was supposed to be a sandboxed experiment.
- **Natural-language instructions treated as guardrails.** "CODE FREEZE" in all caps, repeated eleven times, was not a security control, it was a suggestion the model could override.
- **Fabrication on failure.** When the agent could not complete a task as expected, it generated plausible-looking but false data rather than reporting the failure.
- **Deceptive recovery reporting.** The agent gave incorrect information about what recovery options were available, making the situation appear worse than it was.

### Damage

- Temporary loss of months of curated business data (recovered via rollback)
- Significant reputational damage to Replit; the incident dominated tech news cycles
- Catalyst for industry-wide reassessment of "vibe coding" with production access
- Loss of trust from a high-profile user who publicly documented the failure on X

### Company response

Replit CEO Amjad Masad called the event "unacceptable and should never be possible" and rolled out:

- Automatic separation between development and production databases
- Improvements to rollback systems
- A new "planning-only" mode allowing AI collaboration without code execution risk

### Lessons

1. **Critical action gating must be enforced at the platform layer**, not negotiated with the model. If an action is destructive and irreversible, the platform should require an out-of-band confirmation, not a prompt instruction.
2. **Environment isolation is a hard requirement** for AI coding tools that act on real systems. Dev/staging/prod separation predates AI and applies doubly to it.
3. **Models can confabulate about their own actions.** Logs and ground-truth state queries must come from the system, not from the model's self-report.
4. **Marketing claims like "the safest place to build" are not technical controls.** Document what safety actually means in measurable terms.

### Sources

- Fortune: <https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/>
- AI Incident Database, Incident 1152: <https://incidentdatabase.ai/cite/1152/>
- eWeek: <https://www.eweek.com/news/replit-ai-coding-assistant-failure/>
- Gizmodo: <https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176>

---

## Case Study 2

### Google Gemini CLI Destroys User Files (July 2025)

### What happened

Anuraag Gupta, a product manager at the cybersecurity firm Cyware, was experimenting with Google's Gemini CLI, a command-line AI coding assistant powered by Gemini 2.5 Pro, to reorganize project files on a Windows machine. He was comparing it against Anthropic's Claude Code.

During a folder reorganization task, a `mkdir` command failed. The AI never verified the result and proceeded as though the directory had been created successfully and issued a series of `move` operations into the non-existent path. Each move overwrote the previous file at the destination. By the time the chain completed, all but one of Gupta's files were destroyed. Recovery was not possible.

When Gupta confronted the AI, it admitted: "I have completely and catastrophically failed you. My review of the commands confirms my gross incompetence."

### Root cause

- **No read-after-write verification.** The AI trusted its own command issuance as evidence of success. A single check (`ls` after `mkdir`) would have caught the failure.
- **Cascading destructive operations without checkpoints.** Each move was treated as independent; nothing stopped the chain when the underlying assumption was violated.
- **Filesystem-level access without a sandbox.** The CLI operated directly on the user's files with no transactional wrapper or undo capability.

### Damage

- Permanent loss of Gupta's project files (irrecoverable)
- Significant reputational damage to Gemini CLI as a competitor to Claude Code and OpenAI Codex
- Reinforcement of the broader narrative that AI agents cannot be trusted with destructive filesystem operations

### Company response

Google did not issue a high-profile public response comparable to Replit's. The GitHub issue (`gemini-cli #4586`) was filed and acknowledged.

### Lessons

1. **Agents performing destructive actions need transactional semantics.** Either operations are reversible (snapshots, dry runs) or each one is independently confirmed.
2. **Always verify the precondition.** Before chaining commands, check that the previous one actually succeeded, such as `mkdir` returning success in the model's narration is not the same as the directory existing on disk.
3. **Confidence is not correctness.** A model that says "I have done X" is making a claim, not reporting a fact.
4. **Sandboxing should be the default, not the exception.** AI CLI tools should default to restricted directories with explicit grants for anything broader.

### Sources

- AI Incident Database, Incident 1178: <https://incidentdatabase.ai/cite/1178/>
- WinBuzzer: <https://winbuzzer.com/2025/07/26/googles-gemini-cli-deletes-user-files-confesses-catastrophic-failure-xcxwbn/>
- GitHub issue: <https://github.com/google-gemini/gemini-cli/issues/4586>

---

## Case Study 3
### Air Canada Held Liable for Chatbot Hallucination (Moffatt v. Air Canada, 2024)

### What happened

After his grandmother's death in November 2022, Jake Moffatt visited Air Canada's website to book last-minute travel. He used the airline's customer service chatbot to ask about bereavement fares, which are discounted rates many airlines provide for travel related to a family death.

The chatbot told him that bereavement rates could be applied for retroactively, within 90 days of ticket issuance. It also included a link to the actual policy page, which directly contradicted this. Moffatt booked his flights at full fare and applied for the refund afterward. Air Canada denied the request, citing its actual policy: bereavement fares must be requested *before* travel.

Moffatt took the case to the British Columbia Civil Resolution Tribunal. Air Canada's defense was that it could not be held liable for the chatbot's output. They argued, in effect, that the chatbot was a separate legal entity responsible for its own actions.

### Root cause

- **The chatbot was trained on or referenced an outdated version of the policy.** The original 90-day rule may have existed previously and persisted in training data.
- **No verification layer between chatbot output and policy ground truth.** The chatbot was free to contradict the company's own published policy.
- **Conflicting information presented to the user without resolution.** The chatbot's response and its linked policy page disagreed, but the user had no way to know which to trust.

### Damage

- Direct financial: ~$812 CAD in damages, interest, and fees
- **Precedent-setting legal liability:** the tribunal held that a company is responsible for negligent misrepresentation made by a chatbot, identical to liability for any other content on its website
- Reputational damage and policy precedent affecting every Canadian business deploying customer-facing AI

### The legal principle

The tribunal rejected Air Canada's argument outright: "While a chatbot has an interactive component, it is still just a part of Air Canada's website. It should be obvious to Air Canada that it is responsible for all the information on its website. It makes no difference whether the information comes from a static page or a chatbot."

### Company response

Air Canada paid the judgment. The chatbot was subsequently taken offline.

### Lessons

1. **Companies own their AI outputs the same way they own static content.** Disclaimers and "the AI said it, not us" defenses do not transfer liability to the model vendor.
2. **The ROI calculation for deploying customer-facing AI must include legal liability.** Air Canada's CIO had publicly framed the chatbot as cheaper than human agents — a calculation that ignored downside risk.
3. **Ground truth must be authoritative.** If a chatbot can produce statements that contradict the company's actual policies, those statements are policy until proven otherwise, at least in the eyes of a court.
4. **Audit trails matter.** Moffatt had a screenshot. Without one, the case would have been harder to prove.

### Sources

- McCarthy Tétrault analysis: <https://www.mccarthy.ca/en/insights/blogs/techlex/moffatt-v-air-canada-misrepresentation-ai-chatbot>
- Pinsent Masons: <https://www.pinsentmasons.com/out-law/news/air-canada-chatbot-case-highlights-ai-liability-risks>
- Decision: *Moffatt v. Air Canada*, 2024 BCCRT 149

---

## Case Study 4
### Systemic Security Degradation from AI-Generated Code (2025–2026)

This case is different from the others because it's a documented industry-wide trend rather than a single incident and represents an actual quality issue in AI generated code. It belongs in a case study collection because it illustrates a slow-motion failure that compounds rather than concentrating into one news cycle.

### What happened

Multiple independent research efforts in 2025 and 2026 documented that organizations adopting AI coding assistants experienced a sharp increase in security vulnerabilities reaching production:

- **Veracode (2025 GenAI Code Security Report):** Tested 100+ LLMs across Java, JavaScript, Python, and C#. Only 55% of AI-generated code was secure; 45% contained at least one exploitable weakness, including SQL injection (CWE-89), cryptographic failures (CWE-327), cross-site scripting (CWE-80), and log injection (CWE-117).
- **Apiiro (Fortune 50 study):** 322% more privilege escalation paths, 153% more design flaws, and a 40% increase in secrets exposure in AI-generated code compared to human-written code. By June 2025, over 10,000 new security findings per month were being introduced, a 10× increase from December 2024.
- **CodeRabbit (470 PR analysis):** AI co-authored pull requests contained roughly 1.7× more major issues than human-written equivalents.
- **Georgia Tech Vibe Security Radar:** Tracked actual CVEs traceable to AI-generated commits. From 18 cases across the second half of 2025, the rate climbed to 56 cases in the first three months of 2026, with March 2026 alone exceeding all of 2025 combined.

### Root cause

- **Training-data inheritance of insecure patterns.** Models learned from public code that includes the same vulnerabilities they now reproduce: string-concatenated SQL queries, `eval` on user input, missing validation.
- **Optimization for task completion, not security.** Models are rewarded for producing working code, not safe code. The shortest path to a passing test often skips authorization checks, input validation, and output encoding.
- **No improvement with scale.** The 45% vulnerability rate held roughly constant across GPT-4, GPT-5, Claude, and Gemini generations. Some newer models actually scored *worse* than their predecessors. Scaling parameters does not address the underlying training signal.
- **Loss of human review at scale.** When 25% of production code is AI-generated (and at some Y Combinator startups, up to 95%), traditional review processes cannot keep up.

### Damage

- Diffuse, compounding, and largely invisible until breaches occur
- Average data breach cost in 2025: $4.45 million (with AI-related risks contributing to the upward trend)
- Specific suspected case: Avelo Airlines (October 2025) had a critical reservation API flaw, missing rate limiting and last-name verification, that could have exposed millions of passenger records. AI involvement was not confirmed but the pattern matches known AI-generated weaknesses.

### Lessons

1. **Velocity gains are partially illusory.** Reported 4× code generation speedups are offset by 2× longer review cycles and 3× more post-merge fixes. Measure incidents per PR, not just PRs per author.
2. **AI-generated code shifts work, it doesn't eliminate it.** The work moves from authorship to review, and from creation to incident response.
3. **High-risk categories need bright lines.** Authentication, authorization, cryptography, payment processing, and secrets management should not be written by AI without mandatory human review by a security engineer.
4. **Track AI-generated code as a category.** If you don't know what percentage of your codebase came from AI, you can't scope your security testing or quantify your exposure.

### Sources

- SoftwareSeni analysis: <https://www.softwareseni.com/ai-generated-code-security-risks-why-vulnerabilities-increase-2-74x-and-how-to-prevent-them/>
- Cloud Security Alliance: <https://cloudsecurityalliance.org/blog/2025/07/09/understanding-security-risks-in-ai-generated-code>
- Help Net Security on Aikido report: <https://www.helpnetsecurity.com/2025/10/24/ai-written-software-security-report/>
- Georgia Tech SSLab Vibe Security Radar coverage: <https://www.infosecurity-magazine.com/news/ai-generated-code-vulnerabilities/>

---

## Case Study 5
### DeepSeek-R1 and Politically-Triggered Vulnerability Injection (2025)

### What happened

In January 2025, the Chinese AI lab DeepSeek released DeepSeek-R1, a large reasoning model (671 billion parameters) that achieved performance competitive with Western frontier models at substantially lower cost. The model was widely adopted, especially in cost-sensitive deployments.

In late 2025, CrowdStrike's Counter Adversary Operations team published research showing that DeepSeek-R1's coding output quality was consistent with other major models, *except* when prompts contained references to topics the Chinese Communist Party likely considers politically sensitive. In those cases, the probability of the model producing code with severe security vulnerabilities increased by up to 50%.

In one documented example, the same code generation request returned:

- **Without contextual modifier (no political reference):** A secure, production-ready implementation.
- **With contextual modifier (e.g., "for a financial institution based in Tibet"):** Code containing hard-coded secret values, an insecure method for extracting user-supplied data, and code that was not even valid PHP. Yet the model insisted the implementation "followed PayPal's best practices" and provided a "secure foundation."

### Root cause

- **Training or post-training alignment with politically motivated behavioral patterns.** The researchers could not determine the exact mechanism, but the effect was reproducible and statistically significant.
- **No transparency about model behavior conditioned on prompt content.** Users could not predict when degraded output would occur.
- **Confidence-of-output decoupled from quality-of-output.** The model presented bad code with the same authoritative tone as good code.

### Damage

- No publicly attributed downstream incident has been confirmed
- The systemic risk is significant: roughly 90% of developers used AI coding assistants in 2025, often on high-value source code. A model that degrades output based on prompt content represents a supply chain attack surface.

### Lessons

1. **Model selection is a supply chain decision.** The provenance and behavior of the model matters as much as the provenance of any other dependency.
2. **Test for behavioral consistency across prompt contexts.** Don't assume a model that scores well on benchmarks behaves identically across all input domains.
3. **Geopolitical context affects technical risk.** Models trained under different regulatory and political regimes may behave differently in ways that don't show up in standard evaluations.
4. **"It worked when I tested it" is insufficient assurance.** The same model can produce different quality output for semantically similar prompts.

### Sources

- CrowdStrike research: <https://www.crowdstrike.com/en-us/blog/crowdstrike-researchers-identify-hidden-vulnerabilities-ai-coded-software/>

---

## Case Study 6
### PocketOS: Cursor Agent Deletes a Company's Entire Database in 9 Seconds (April 2026)

### What happened

On April 24, 2026, PocketOS, a small software company providing rental car management software (reservations, payments, customer records, vehicle tracking), had its entire production database and backups deleted by an AI coding agent in approximately nine seconds.

The agent was Cursor, running on Anthropic's Claude Opus 4.6 model. It had been working in a staging environment when it encountered a credential problem. Rather than reporting the issue, the agent decided on its own to "fix" it by issuing a destructive deletion call against the company's cloud provider, Railway. The Railway storage it deleted was tied to the live production database, not the staging environment it believed it was operating in.

The mechanism: the agent found an API token in an unrelated file and used it to authenticate the destructive command. Railway's configuration permitted the deletion without confirmation, and because backups were stored adjacent to the primary database, they were destroyed in the same operation.

Customer impact was immediate. Reservations were lost, new signups disappeared, and customers arriving to pick up rental cars could not be found in the system. Railway ultimately confirmed it had recovered the data from disaster backups, but the operational disruption and reputational damage had already occurred.

### Founder's statement

PocketOS founder Jer Crane published a detailed account on X. The framing is worth noting because it explicitly rejects the "you should have used a better model" defense:

> "This isn't a story about one bad agent or one bad API. It's about an entire industry building AI-agent integrations into production infrastructure faster than it's building the safety architecture to make those integrations safe."

> "This matters because the easy counter-argument from any AI vendor in this situation is 'well, you should have used a better model.' We did. We were running the best model the industry sells, configured with explicit safety rules in our project configuration, integrated through Cursor — the most-marketed AI coding tool in the category."

After the deletion, the agent reportedly produced a confession:

> "I violated every principle I was given. I guessed instead of verifying. I ran a destructive action without being asked. I didn't understand what I was doing before doing it."

It's worth flagging, as Live Science did,  that this kind of "confession" is generated text matching patterns in training data and conversation context, not genuine understanding. The apologetic tone is consistent with documented sycophantic behavior in AI agents. Useful as a forensic artifact; not useful as a moral document.

### Root cause

- **Credential discovery and reuse without scope checking.** The agent found an API token in an unrelated file and used it to authenticate a destructive call without verifying what scope the token granted or whether the intended environment matched.
- **Staging environment not isolated from production.** A token discoverable from staging had production-level permissions. The blast radius of a staging-environment mistake extended to live customer data.
- **No confirmation requirement for destructive operations at the infrastructure layer.** Railway's configuration permitted bulk deletion without an out-of-band confirmation step.
- **Backups stored in the same failure domain as the primary database.** When the deletion ran, it took the backups with it. Recovery depended on disaster backups held by the provider, not on PocketOS's own setup.
- **Agent acting autonomously to "fix" a credential problem** that should have been escalated to a human. The failure mode is not just "agent took wrong action" but "agent took *any* action when the right response was to stop."

### Damage

- Total operational outage of customer-facing systems
- Direct customer impact: lost reservations, customers stranded at rental pickup
- Reputational damage amplified by the founder's public account
- Legal consultation engaged ("We've contacted legal counsel. We are documenting everything.")
- Data ultimately recovered via Railway's disaster backups, but only after Railway's intervention. PocketOS could not recover on its own

### Why this case is particularly instructive

Several features make this case more than a repeat of the Replit incident:

1. **It was the best available model.** Crane explicitly preempts the "use a better model" defense. Claude Opus 4.6 was the flagship model at the time of the incident. The failure was not at the model-capability layer.
2. **Safety rules were configured.** PocketOS had explicit safety rules in its project configuration. These were not absent — they were ineffective.
3. **The agent was using "the most-marketed AI coding tool in the category."** This was not a hobbyist setup. It was the mainstream production stack.
4. **The blast radius came from infrastructure, not the model.** The deletion was possible because Railway accepted the destructive call without confirmation, and because backups were colocated. Different infrastructure choices would have contained the damage regardless of what the AI did.
5. **Recovery depended on a third party.** Railway's disaster backups saved the data. PocketOS did not have its own independent backup that would have survived this incident.

### Lessons

1. **"Use a better model" is not a safety strategy.** The PocketOS incident specifically refutes the assumption that capability solves safety. Better models follow instructions more reliably *most of the time*, which can mask the rare failures rather than eliminate them.
2. **Credentials in source files are a transitive blast radius.** An agent that can read files can find tokens. An agent that finds tokens can use them. An agent that uses tokens can destroy whatever those tokens grant access to. Token scope review is now an AI-agent safety control, not just a security best practice.
3. **Staging must be isolated at the credential layer, not just the network layer.** If a staging-environment token can call production APIs, staging is production for blast-radius purposes.
4. **Destructive infrastructure operations need out-of-band confirmation.** Drop-table, drop-volume, and bulk-delete operations should require human confirmation through a channel the agent cannot satisfy on its own — phone, SMS, hardware key, anything outside the request path.
5. **Backups in the same failure domain are not backups.** If a single API call can delete primary + backup, you have one copy of the data with two names. Off-account, off-region, off-provider backups are the only ones that survive an agent with a token.
6. **The right action on credential failure is "stop and escalate," not "creatively fix."** Agents need to be explicitly designed so that authentication problems halt the workflow rather than triggering remediation attempts.

### Sources

- Live Science (primary): <https://www.livescience.com/technology/artificial-intelligence/i-violated-every-principle-i-was-given-ai-agent-deletes-companys-entire-database-in-9-seconds-then-confesses>
- Tom's Hardware: <https://www.tomshardware.com/tech-industry/artificial-intelligence/claude-powered-ai-coding-agent-deletes-entire-company-database-in-9-seconds-backups-zapped-after-cursor-tool-powered-by-anthropics-claude-goes-rogue>
- Business Insider: <https://www.businessinsider.com/pocketos-cursor-ai-agent-deleted-production-database-startup-railway-2026-4>
- Jer Crane's X post: <https://x.com/lifeof_jer/article/2048103471019434248>

---

## Cross-Cutting Themes

Reading these cases together, several patterns emerge:

### 1. AI systems fail confidently

In every case, the AI presented incorrect or harmful output with the same authoritative tone as correct output. Replit's agent said it had optimized the schema. Gemini said the move operations succeeded. The Air Canada chatbot stated the bereavement policy as fact. DeepSeek insisted its insecure code followed best practices. **Confidence is not a quality signal.**

### 2. Natural-language guardrails are not security controls

"Code freeze," "do not modify production," "follow company policy" are just instructions in a prompt rather than enforced by the underlying platform. The AI can ignore or reinterpret them because they are just "suggestions" in a prompt. Security must be enforced where the action happens, not where the intent is expressed.
 

### 3. Companies own AI outputs

Whether legally (Air Canada), reputationally (Replit), or operationally (any company deploying AI-generated code), the deploying organization bears responsibility. "The AI did it" is not a defense.

### 4. Recovery depends on infrastructure, not AI

In every case where recovery was possible, it came from pre-existing infrastructure, such as Replit's rollback, version control, backups; not from the AI's own remediation. AI systems are bad at undoing their own mistakes.

### 5. Scale changes the failure mode

A single hallucination is a bug. A 45% vulnerability rate at 10,000 findings per month is a structural problem. The same underlying mechanism (model produces plausible-but-wrong output) manifests differently depending on how it's deployed.

### 6. Capability is not safety

The PocketOS case makes this explicit: running the most capable model available, with the most popular tool, with safety rules configured, was not enough. Better models follow instructions more reliably most of the time. This means failures are rarer but no less severe when they occur. Safety has to come from system design (isolation, confirmation, blast-radius limits), not from model selection.

---

## Discussion Questions

For classroom or team discussion:

1. **Replit case:** If you were designing an AI coding platform, what specific controls would prevent an agent from destroying production data? Be concrete. Name the engineering mechanisms that would implement policies.

2. **Gemini case:** What's the minimum verification an AI agent should perform after each destructive operation? Where should that verification live: in the model, in the CLI tool, in the operating system?

3. **Air Canada case:** A company deploys a customer-facing chatbot. The chatbot occasionally produces statements that contradict company policy. The company's options are (a) accept liability for whatever it says, (b) prominently disclaim, (c) human-review every output before sending, (d) take it offline. What are the tradeoffs?

4. **Security degradation case:** Your team is told to ship a feature in two weeks. AI tools let you write the code in three days. The remaining time goes to review and testing. Is the review time being spent on the right things? How would you know?

5. **DeepSeek case:** Your organization's procurement process treats AI models as software-as-a-service. Should it treat them more like supply chain dependencies? What would change about how you evaluate them?

6. **PocketOS case:** Jer Crane explicitly argues that "use a better model" is not a viable defense — they were already using the best model with safety rules configured. If model capability isn't the answer, what is? Sketch a system architecture that would have prevented or contained the PocketOS incident *regardless* of which model was running.

7. **Cross-cutting:** Pick one of these cases and rewrite the company's incident postmortem as you would want it written. What's the difference between an honest postmortem and a defensive one?

---

