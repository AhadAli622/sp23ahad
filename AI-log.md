```markdown
# AI Log — tools, prompts, and reflections

This file records which AI tools were used during development, representative prompts, how they are integrated into the codebase, and brief reflections on usefulness and limitations.

---

## 1) Tools Used

- **Gemini (Google GenAI)** — used as the primary backend LLM in `app.py` via the `google.genai` SDK. The app tries to call Gemini for conversation continuation and for extracting structured plan parameters (language, level, hours, weeks). When the API key or quota is unavailable, the app falls back to a local stub implementation.

- **ChatGPT (OpenAI)** — used experimentally during design and early prompt engineering (developer notes). If you prefer, you can re-target the AI integration to OpenAI's APIs by replacing `call_ai_api` with an OpenAI client.

- **Grok (UI/UX ideation)** — used as an ideation assistant for UI/UX sketches, labels, and wording suggestions during the design phase (the ASCII sketches and short copy in `UI-Sketch-and-Vision.md` were refined using Grok outputs).

---

## 2) How they are integrated

- `app.py` calls the AI via `call_ai_api(history)`. If `GEMINI_API_KEY` is present, the code initializes `genai.Client(api_key=...)` and sends a combined prompt (system instructions + conversation). The returned text is parsed for either plain assistant replies or an embedded JSON object with the exact fields required for plan generation.

- If Gemini is not available (no key or quota exceeded), `call_ai_api` catches exceptions and calls `call_ai_api_stub(history)`. The stub is a deterministic rule-based responder that simulates follow-up prompts and, when the conversation contains goal/level/time, returns the expected JSON payload.

- UI/UX design iterations used Grok for brainstorming microcopy and layout ideas; the final sketches were edited and stored in `UI-Sketch-and-Vision.md`.

---

## 3) Representative prompts

- **System instruction (summarized):**
  - You are a friendly learning coach. Reply in clear English. Guide users to provide: 1) target skill, 2) current level, 3) background, 4) weekly time and weeks (4–6). Only when all info is available, return a JSON object exactly in the format: { "language": "<...>", "level": "<Beginner|Intermediate|Advanced>", "hours": <int>, "weeks": <4..6> } — with no extra text when sending JSON.

- **Example user prompt (chat flow):**
  - "I want to learn Python"
  - "Beginner"
  - "I can give 5 hours per week for 5 weeks"

- **Resource suggestion prompt (internal):**
  - The server uses `suggest_resources(goal, level, topic)` locally to attach curated resource items from `data/resources.json`. No external LLM call is made for resource matching (this keeps the resource list deterministic and editable).

---

## 4) Example AI outputs / expected JSON

- When user provides complete info the assistant should emit a JSON snippet like:

```json
{ "language": "Python Programming", "level": "Beginner", "hours": 5, "weeks": 5 }
```

- The backend detects this payload in the assistant's text (via regex) and converts it into a `LearningPlan` with steps from `generate_learning_path()`.

---

## 5) Reflections: usefulness and limitations

- **Usefulness:**
  - LLMs are excellent at conversational flows and extracting structured intent from free text. Using an LLM (Gemini or ChatGPT) lets the app ask follow-up clarifying questions naturally and accept casual user input.
  - Grok helped iterate on short UI copy and layout suggestions quickly.

- **Limitations & Mitigations:**
  - **Quota / Availability:** Cloud LLMs can be rate-limited (we saw `RESOURCE_EXHAUSTED` quota errors while testing). Mitigation: the app has a local stub that keeps dev/testing workflows functional.
  - **Hallucination / Incorrect JSON:** LLMs sometimes produce malformed JSON or extra text. Mitigation: the server scans for JSON objects and validates required keys before using the payload; if parsing fails the bot asks clarifying questions.
  - **Privacy / Safety:** User messages are transmitted to third-party APIs if enabled. Document this in your privacy policy and avoid sending sensitive PII.
  - **Cost / Billing:** Calls to commercial LLMs have cost implications — prefer stub/data-driven behavior for high-volume or predictable functionality (like resource matching).

---

## 6) Prompts & tuning notes (engineering)

- Keep system instructions short, directive, and explicit about exact JSON formatting to reduce unexpected output.
- Use short examples during prompt engineering to demonstrate the exact JSON-only response you expect when the assistant is ready to produce the plan.
- Validate and sanitize any LLM output before persisting (we parse JSON and enforce `weeks` to be within [4,6]).

---

## 7) Where to look in the code

- `app.py` — `call_ai_api`, `call_ai_api_stub`, `SYSTEM_INSTRUCTIONS`, `/api/chat` handling, and `generate_learning_path`.
- `data/resources.json` — curated, editable resources used by `suggest_resources`.

---

If you'd like, I can add more detailed saved prompt templates (for Gemini and ChatGPT) and example transcripts (redacted) to this log.

```
# AI Usage Log (Midterm Project)

> NOTE: This log records where I used an AI assistant (ChatGPT) during the project.
> I have reviewed, edited and understood all outputs before using them.

## Entry 1 – 06 Dec 2025

**What I asked:**  
Explain Option 2 (Learning Path Recommender) and help me choose a tech stack for a professional-looking web app.

**How AI helped:**  
- Compared Python CLI, Flask, and Node.js.
- Recommended Flask + HTML + Bootstrap.
- I accepted this suggestion.

## Entry 2 – 06 Dec 2025

**What I asked:**  
Generate documentation skeletons and project structure for my midterm (ProblemStatement, UseCases, README, TestPlan, UI sketch, roadmap).

**How AI helped:**  
- Produced draft text for all .md files and proposed repo structure.
- I will adapt wording and shorten some sections manually.

## Entry 3 – 06 Dec 2025

**What I asked (planned):**  
Generate starter Flask code for login, registration and chatbot-style recommender.

**How AI helped:**  
- Provided example routes, templates, and recommendation logic.
- I will refactor variable names and add comments to ensure I fully understand the code.

---

## Prompt Templates  
 

- **System prompt — Friendly coach (Small-talk first, JSON when ready):**

```text
You are a friendly learning coach. Reply in clear English only.
- Begin with normal conversational replies to greetings and everyday chat. Do not immediately ask about learning goals.
- Only switch to learning-mode when the user explicitly expresses learning intent (e.g., "I want to learn", "I want to study", "teach me", "help me learn", "create a plan").
- When in learning-mode, ask only the needed clarifying questions in this order: 1) target skill or goal, 2) current level (Beginner/Intermediate/Advanced), 3) background, 4) hours per week and number of weeks (aim 4–6).
- Once you have all required fields, respond with ONLY a single JSON object (no extra text):
  { "language": "<skill or detailed goal>", "level": "<Beginner|Intermediate|Advanced>", "hours": <int>, "weeks": <4..6> }
```

- **Intent classifier (quick LLM check) — prompt**

```text
You are a tiny classifier that answers only with one token: YES or NO.
Return YES if the user explicitly expresses intent to learn, study, or requests a learning plan.
Return NO otherwise. Examples of YES: "I want to learn Python", "Can you make a study plan?", "Teach me web development".
Examples of NO: "I like Python", "What's the weather?", "How are you?", "I use Python at work".
User message: "{{user_message}}"
```

- **JSON plan generator (strict output)**

```text
You are a focused plan generator. When given user-provided goal, level, hours, and weeks, output ONLY this JSON object with keys exactly: language, level, hours, weeks.
If any numbers are outside recommended bounds, clamp weeks to the range [4,6].
Example output: { "language": "Python Programming", "level": "Beginner", "hours": 5, "weeks": 5 }
```

- **Assistant small-talk examples (for local testing)**

```text
User: "Hi"
Assistant: "Hey — good to see you! How's your day going? Anything interesting happening?"

User: "I'm bored"
Assistant: "I get that. If you'd like, we can explore a small learning step you could try in 30 minutes — anything you'd like to get better at?"
```

Use these templates to seed `SYSTEM_INSTRUCTIONS` or as separate prompts when calling the LLM for intent classification or JSON extraction. They are designed to encourage the small-talk-first behavior and to make the exact JSON format explicit when the assistant is ready to generate the plan.

---

## Prompt Templates (copy / paste)

 

- **System prompt — Friendly coach (Small-talk first, JSON when ready):**

```text
You are a friendly learning coach. Reply in clear English only.
- Begin with normal conversational replies to greetings and everyday chat. Do not immediately ask about learning goals.
- Only switch to learning-mode when the user explicitly expresses learning intent (e.g., "I want to learn", "I want to study", "teach me", "help me learn", "create a plan").
- When in learning-mode, ask only the needed clarifying questions in this order: 1) target skill or goal, 2) current level (Beginner/Intermediate/Advanced), 3) background, 4) hours per week and number of weeks (aim 4–6).
- Once you have all required fields, respond with ONLY a single JSON object (no extra text):
  { "language": "<skill or detailed goal>", "level": "<Beginner|Intermediate|Advanced>", "hours": <int>, "weeks": <4..6> }
```

- **Intent classifier (quick LLM check) — prompt**

```text
You are a tiny classifier that answers only with one token: YES or NO.
Return YES if the user explicitly expresses intent to learn, study, or requests a learning plan.
Return NO otherwise. Examples of YES: "I want to learn Python", "Can you make a study plan?", "Teach me web development".
Examples of NO: "I like Python", "What's the weather?", "How are you?", "I use Python at work".
User message: "{{user_message}}"
```

- **JSON plan generator (strict output)**

```text
You are a focused plan generator. When given user-provided goal, level, hours, and weeks, output ONLY this JSON object with keys exactly: language, level, hours, weeks.
If any numbers are outside recommended bounds, clamp weeks to the range [4,6].
Example output: { "language": "Python Programming", "level": "Beginner", "hours": 5, "weeks": 5 }
```

- **Assistant small-talk examples (for local testing)**

```text
User: "Hi"
Assistant: "Hey — good to see you! How's your day going? Anything interesting happening?"

User: "I'm bored"
Assistant: "I get that. If you'd like, we can explore a small learning step you could try in 30 minutes — anything you'd like to get better at?"
```

Use these templates to seed `SYSTEM_INSTRUCTIONS` or as separate prompts when calling the LLM for intent classification or JSON extraction. They are designed to encourage the small-talk-first behavior and to make the exact JSON format explicit when the assistant is ready to generate the plan.
