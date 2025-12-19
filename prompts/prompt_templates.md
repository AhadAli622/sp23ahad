# Prompt Templates — copy & paste

This file contains ready-to-use prompt templates for Gemini, ChatGPT, or Grok. They are designed for UI/UX, problem diagnosis, structured JSON extraction, resource suggestion, plan generation, microcopy, accessibility checks, and debugging assistance.

Notes
- Prefer short system instructions and explicit JSON schemas when you need structured outputs.
- For production, keep prompts in a secure place and version them.

---

## A — UI Improvement / "Make a good UI"

System (optional):
"You are an expert UI/UX designer. Provide concise, prioritized improvements and sample microcopy. Keep suggestions practical and accessible."

User:
"Improve the dashboard UI for a chat-based learning coach. Provide Top 3 prioritized design changes, one accessibility improvement, and a suggested CTA microcopy."

Expected structure:
- Improvement 1: ...
- Improvement 2: ...
- Improvement 3: ...
- Accessibility: ...
- CTA microcopy: "Create my learning plan"

---

## B — Problem diagnosis / 'Face this problem — resolve it'

System:
"You are an experienced full-stack engineer. Ask clarifying questions if info is missing. Provide step-by-step fixes, minimal repro, and test commands."

User:
"My `/api/chat` endpoint returns 500 when parsing AI output. Here are logs: [paste logs]. What are likely causes and how to fix? Provide a short code patch and test steps."

Expected output:
- Likely causes (ordered)
- Quick patch (diff/snippet)
- Steps to reproduce and run tests

---

## C — Strict JSON extraction (learning profile)

System:
"You are a JSON extractor. When ready, output ONLY a JSON object with keys: `language`, `level`, `hours`, `weeks`. `level` must be one of `Beginner`, `Intermediate`, `Advanced`. `weeks` must be integer in [4,6]. Clamp if out of range. No extra text."

User:
"User messages: 'I want to learn Rust', 'Intermediate', 'I can do 3 hours per week for 8 weeks'."

Expected output (only JSON):
```json
{ "language": "Rust", "level": "Intermediate", "hours": 3, "weeks": 6 }
```

---

## D — Suggest curated resources (deterministic)

System:
"You are a content curator. Return up to 5 items as a JSON array: `[{type,title,url,note,level}]`. Prefer official docs and reputable sources."

User:
"Provide curated resources for 'Go programming' at beginner level."

Expected output (JSON array):
```json
[
  {"type":"text","title":"A Tour of Go","url":"https://tour.golang.org/","note":"Interactive tour","level":"beginner"},
  ...
]
```

---

## E — Generate step-by-step learning plan (strict schema)

System:
"You are a learning designer. Given `goal`, `level`, `hours`, `weeks`, output ONLY a JSON array `steps` where each element is `{week:int,step:int,topic:str,hours:int,mode:str}`. Ensure `weeks` elements are produced."

User:
"Create a 4-week plan for 'JavaScript' at Beginner, 4 hours/week."

Expected output example:
```json
[
  {"week":1,"step":1,"topic":"JS basics","hours":4,"mode":"videos+practice"},
  {"week":2,"step":2,"topic":"Control flow & functions","hours":4,"mode":"practice"},
  ...
]
```

---

## F — Short microcopy / tone polishing

User:
"Rewrite this CTA to be friendly and concise: 'Start the process of learning by creating a plan now'"

Expected output:
"Create my learning plan"

---

## G — Accessibility improvements checklist

User:
"Given a dashboard UI, provide an accessibility checklist focused on keyboard navigation, color contrast, and ARIA labels."

Expected output:
- Keyboard: ensure tab order, focus outlines, skip links
- Contrast: list contrast ratios and example color swaps
- ARIA: where to add `aria-label`, `role`, and examples

---

## H — Debug assistant — reproduce and test

System:
"You are a developer assistant. Provide a minimal repro, one unit test, and a suggested fix. Include commands to run tests."

User:
"Bug: `ChatMessage.query` returns empty after insert. Here is snippet: [paste]."

Expected output:
- Minimal repro code
- One pytest/unittest case
- Command: `pytest tests/test_chat.py::test_message_persist`

---

## Tips for using templates
- Always add an explicit output schema when you require structured responses.
- If the LLM is unreliable, add a fallback stub in code and log the issue.
- For UI prompts, ask for small, prioritized lists rather than very large rewrites.

*** End of prompt templates
