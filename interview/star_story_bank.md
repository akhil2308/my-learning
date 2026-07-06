# STAR Story Bank — behavioral rounds are a retrieval problem; you lose by composing live, you win by indexing ahead

**Level 16 · The Final Boss · Session 3 · [INTERVIEW-CRITICAL]**
*(Deliberately scheduled in week 1: stories need weeks of refinement, not a pre-interview cram.)*

## TL;DR

- Senior behavioral rounds ask ~8 recurring themes. You need **8 pre-built stories**, each tagged to 2–3 themes, so any question is a lookup, not improvisation.
- Format: **STAR with numbers** — Situation (1 sentence), Task (1 sentence), Action (3–4 concrete decisions *you* made), Result (metric + what you'd do differently).
- The senior differentiator is in the A: "I decided/convinced/traded-off," never "we did." Interviewers score agency and judgment, not project summaries.
- Every story ends with a **scar**: what broke, what you learned, what you now do by default. Perfect stories read as junior or fake.
- This doc is a workbook. Fill 2 slots today (the rep), then 1 per week. Rehearse out loud — written ≠ retrievable.

## Mental Model

```mermaid
flowchart LR
    subgraph themes ["The 8 themes interviewers draw from"]
        T1["Ownership beyond scope"]
        T2["Technical conflict / disagree-and-commit"]
        T3["Scaling / perf under pressure"]
        T4["Failure & what changed after"]
        T5["Ambiguity → structure"]
        T6["Mentoring / raising the bar"]
        T7["Hard trade-off (deadline vs quality)"]
        T8["Influencing without authority"]
    end
    subgraph bank ["Your 8 stories (each tagged 2–3 themes)"]
        S1["IRIS"] & S2["RAPID"] & S3["Supervisor orch"] & S4["fastapi template"] & S5["…"]
    end
    Q["Any behavioral question"] --> MATCH["match question → theme → story"] --> themes
    themes --> bank
    bank --> DELIVER["90-second STAR delivery\n+ numbers + scar"]
```

## What Actually Happens

What the interviewer does with your answer, minute by minute:

1. They ask "tell me about a time you disagreed with a technical decision." They're not curious about the project — they're filling a rubric row: *conflict: does this person disagree productively at senior scope?*
2. **First 15 seconds:** they calibrate scope. "Our team" framing → mid-level. "I noticed X was going to cost us Y, so I…" → senior. Situation must establish stakes in one sentence with a number (users, ₹/$, latency, team size).
3. **The middle:** they listen for *decision points* — moments with a real alternative. Each Action line should be `considered A vs B → chose B because <reason>`. This is where judgment is scored.
4. **The Result:** they want a measured outcome ("p99 220ms→45ms," "on-call pages −70%," "3 teams adopted it") and honest cost. Then the follow-up probe: "what would you do differently?" — if you haven't pre-written the scar, this is where composed-live stories collapse.
5. They cross-reference: two questions later they'll probe the same story from another angle. Pre-built stories stay consistent; improvised ones drift, and drift reads as embellishment.

## The Opinionated Take

- **Build 8 stories, not 20.** Depth and rehearsal beat coverage; each story tagged to 2–3 themes covers the matrix. When you'd be wrong: if a target company publishes its principles (e.g., Amazon LPs), re-tag the bank to *their* vocabulary the night before.
- **Numbers are non-negotiable.** Dig through old dashboards, PRs, incident docs *now* — reconstructing metrics 11 months later is why stories go vague.
- **Say "I" and tolerate the discomfort.** Credit the team in one clause, then narrate your decisions. Interviewers cannot hire "we."
- 90 seconds max for the unprompted answer; let follow-ups pull depth. A 5-minute monologue reads as unable-to-scope.

## Interview Ammo

*(Meta-round: the questions each theme arrives dressed as.)*

1. T1 Ownership: "Tell me about a time you took on something outside your role." / "A problem nobody owned."
2. T2 Conflict: "Disagreed with a senior engineer/your manager — what happened?" / "A decision you lost — did you commit?"
3. T3 Scaling: "The hardest performance problem you've solved." / "A system that hit its limits."
4. T4 Failure: "Your biggest production incident." / "A project that failed."
5. T5 Ambiguity: "You were handed something vague — walk me through your first two weeks."
6. T6 Mentoring: "How did you level someone up?" / "Raising the quality bar on a team."

Strong-answer shape for all: 1-sentence situation with a stake, 3 decision points with named alternatives, measured result, one scar.

## Practice Rep (60 min, pass/fail)

Fill **slots 1 and 2 below** (recommend IRIS and supervisor-orchestration — your freshest metrics). For each: complete every field, including ≥2 real numbers and the scar line. Then deliver each **out loud, timed** (voice memo).

**Pass:** 2 slots fully filled with zero placeholder text; both recordings ≤ 2 minutes; each recording contains ≥2 numbers and ≥1 explicit "I decided/chose/pushed for."
**Fail:** any field says "TBD," any recording over 2:30, or a story with no metric.
**Ongoing rep:** 1 slot per week; re-record each story once before 1-Aug.

## Story Slots (the workbook)

> Template per slot — copy verbatim:
> - **Title (5 words):**
> - **Themes (2–3 of T1–T8):**
> - **S** — situation + stake (1 sentence, 1 number):
> - **T** — what *I* was on the hook for (1 sentence):
> - **A1/A2/A3** — decision points (`considered X vs Y → chose Y because…`):
> - **R** — measured result (metrics!):
> - **Scar** — what broke / what I'd do differently / new default:
> - **60-sec cut** (what survives if the interviewer is impatient):

### Slot 1 — IRIS
*(fill via rep)*

### Slot 2 — Supervisor orchestration (multi-agent platform)
*(fill via rep)*

### Slot 3 — RAPID

### Slot 4 — fastapi-large-app-template (raising the bar / T6, T1)

### Slot 5 — Production incident (T4 — the honest one)

### Slot 6 — RAG pipeline evolution (HyDE/multi-query/compression — T3, T5)

### Slot 7 — Conflict story (T2 — find it in old design reviews)

### Slot 8 — Wildcard (T8 influencing without authority — cross-team adoption of something you built)

## Self-Check (5 questions, answers at bottom)

1. Why do pre-built stories beat live composition even for a strong communicator?
2. What single word pattern most reliably separates senior answers from mid-level ones?
3. Why must every story include a scar?
4. Your answer is running past 3 minutes. What went wrong structurally?
5. How do you reuse 8 stories against a company with 14 published leadership principles?

---

<details><summary>Answers</summary>

1. Interviewers probe the same story from multiple angles; pre-built stories stay consistent and keep their numbers. Also, retrieval under pressure fails — indexing (theme → story) turns a hard generative task into an easy lookup.
2. "I" with decision verbs — "I decided/convinced/traded off X for Y" — versus "we did/it was decided."
3. It preempts the guaranteed "what would you do differently?" follow-up, signals self-awareness, and makes the rest of the story credible.
4. You front-loaded depth instead of letting follow-ups pull it. Deliver the 90-second cut; keep detail in reserve.
5. Re-tag, don't rewrite: map each story to their vocabulary (one story usually serves 2–3 principles) and adjust the emphasis of the Action lines the night before.

</details>
