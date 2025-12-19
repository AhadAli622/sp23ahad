# Use Cases – Learning Path Recommender

## UC1 – New User Registration

**Actor:** Visitor  
**Precondition:** Visitor is not logged in.  

**Main Flow:**
1. Visitor opens the website and clicks "Register".
2. System shows registration form (name, email, password, confirm password).
3. Visitor fills the form and submits.
4. System validates data (unique email, password length).
5. System creates a new user and logs them in.
6. System redirects user to the dashboard.

**Postcondition:** New user account exists and user is authenticated.

---

## UC2 – Login and Access Dashboard

**Actor:** Registered User  

**Main Flow:**
1. User opens website and clicks "Login".
2. System shows login form (email, password).
3. User submits credentials.
4. System verifies credentials.
5. On success, user is redirected to dashboard where they can start a new learning plan.

**Alternative Flows:**
- If credentials invalid, system shows an error message.

---

## UC3 – Start Chatbot and Provide Learning Goal

**Actor:** Authenticated User  

**Main Flow:**
1. User on dashboard clicks "Start Learning Assistant".
2. Chatbot widget opens with a greeting message.
3. Chatbot asks: “What is your learning goal?”.
4. User types goal (e.g., “become fluent in Python for data analysis”).
5. Chatbot stores the goal and moves to collecting background information.

**Postcondition:** System has captured the user’s learning goal.

---

## UC4 – Collect Background, Skills, and Time Availability

**Actor:** Authenticated User  

**Main Flow:**
1. After goal, chatbot asks about current skill level (Beginner/Intermediate/Advanced).
2. User responds.
3. Chatbot asks about background (e.g., prior programming experience, maths comfort).
4. User responds.
5. Chatbot asks for weekly time availability (hours per week) and target duration.
6. User responds.
7. System summarizes the collected profile and asks for confirmation.
8. On confirmation, system sends data to recommendation engine.

**Postcondition:** User profile (goal, level, time) is ready for plan generation.

---

## UC5 – Generate and View Learning Path

**Actor:** Authenticated User  

**Main Flow:**
1. System runs the rule-based recommendation engine using the collected profile.
2. System generates:
   - ordered list of topics,
   - estimated time per topic,
   - recommended activity type (video, reading, project).
3. System displays the path on `learning_path.html` as:
   - a step-by-step list,
   - a simple timeline/progress view.
4. User can save the plan for future reference.

**Postcondition:** Personalized learning path is visible to the user.

---

## UC6 – View Saved Plan Later

**Actor:** Authenticated User  

**Main Flow:**
1. User logs in again.
2. On dashboard, user sees “Your last learning path”.
3. User clicks "View plan".
4. System shows previously generated learning path and roadmap.

**Postcondition:** User can continue following their plan without repeating the chat.

---

## Additional Detailed Use Cases

### UC-A – Create a Learning Plan Automatically from Chat (detailed)

**Actor:** Authenticated User

**Precondition:** User is logged in and a `Conversation` exists in the DB.

**Main Flow:**
1. User provides the final piece of information in the chat (goal, level, hours/week, weeks).
2. Backend `/api/chat` receives the message, appends it to `ChatMessage` and builds the `history` from DB messages.
3. The backend calls `call_ai_api(history)` to get assistant text. If the response contains a JSON object with keys `language`, `level`, `hours`, `weeks`, the server parses it.
4. The server normalizes values (enforces weeks in [4,6], converts hours to integer) and constructs a `profile` object.
5. `generate_learning_path(profile)` is invoked to produce a list of weekly steps; each step includes `topic`, `hours`, `mode`, and a list of `resources` returned by `suggest_resources(goal, level, topic)`.
6. The server creates a `LearningPlan` row with `path_json = json.dumps(steps)` and links it to the current user.
7. The server stores an assistant reply `ChatMessage` acknowledging plan creation and returns JSON: `{"reply":..., "plan_ready": true, "plan_id": <id>}`.

**Alternative Flows / Errors:**
- If the AI call fails (quota or network), the backend falls back to `call_ai_api_stub(history)` which simulates prompts and may still produce JSON. If no JSON is found, `plan_ready` remains false and the conversation continues.
- If JSON is malformed or missing keys, the server logs the error and asks the user for the missing fields in the chat.

**Postcondition:** A `LearningPlan` exists in DB and is linked to the user; the plan can be viewed at `/learning-path/<plan_id>`.

---

### UC-B – Suggest Resources for Any Programming Language

**Actor:** Authenticated User

**Precondition:** `data/resources.json` contains curated resources; `RESOURCES` is loaded at app start.

**Main Flow:**
1. When `generate_learning_path` calls `suggest_resources(goal, level, topic)`, the function looks up `RESOURCES` for entries whose `categories` match the `goal` or `topic` and whose `level` matches the user level (or is `all`).
2. Matching resources are attached to the step and returned to the caller.
3. The UI renders resource items (title, type, url, note) under each week step so the user can click and open them.

**Alternative Flows:**
- If no resources match, `suggest_resources` falls back to a small built-in list. The app also logs a warning indicating missing curated resources for that category.

**Postcondition:** Each plan step contains at least one suggested resource when possible.

---

### UC-C – Mark Step Complete (planned / API description)

**Actor:** Authenticated User

**Precondition:** The plan exists and the user is the owner of the plan.

**Main Flow (API design):**
1. Client sends `POST /api/plan/<plan_id>/step/<step_index>/complete` (JSON body optional: `{ "completed": true }`).
2. Server verifies ownership: `LearningPlan.user_id == current_user.id`.
3. Server updates plan state. Current MVP stores `path_json` as an array of steps. The server will update the step to include `"completed": true` and re-save `path_json`.
4. Server responds with the updated `path_json` and `200 OK`.

**Notes:**
- This endpoint is a planned, minimal implementation that mutates the JSON blob. A more robust design would introduce a `PlanStep` table to track completion and timestamps per-step.

**Postcondition:** The specified step is marked complete in the persisted plan.

---

## High-Level Design & Data Flow

This section provides a simple, high-level overview of the main components and how data flows through the system.

- **Components:**
   - `Frontend` (templates + JS): Login/Register forms, Dashboard, Chat UI, Learning Path view.
   - `Backend` (Flask `app.py`): Routes, auth, business logic, AI integration, resource matcher, plan generator.
   - `Database` (SQLite + SQLAlchemy): Tables: `users`, `conversations`, `chat_messages`, `learning_plans`.
   - `Resources` (data/resources.json): Curated resource list loaded at startup into `RESOURCES`.
   - `AI Service` (Gemini or stub): Used to interpret conversation and produce plan JSON when possible.

- **Typical Data Flow (Generate plan):**
   1. User messages are posted to `POST /api/chat`.
   2. Server appends message to `chat_messages` and builds `history` from DB rows.
   3. Server calls AI (`call_ai_api(history)`) to continue the conversation; AI may return guidance or a JSON payload containing plan parameters.
   4. On receiving plan parameters, server invokes `generate_learning_path(profile)` which queries `RESOURCES` via `suggest_resources` to attach resources per step.
   5. Server stores the generated plan in `learning_plans.path_json` and returns `plan_id` to the client.
   6. Client navigates to `/learning-path/<plan_id>`; server reads `path_json` and renders the UI.

- **Data Model Mapping:**
   - `User` → `users` table (id, name, email, password_hash)
   - `Conversation` → `conversations` (id, user_id, title, timestamps)
   - `ChatMessage` → `chat_messages` (id, user_id, conversation_id, role, content, created_at)
   - `LearningPlan` → `learning_plans` (id, user_id, goal, level, hours_per_week, duration_weeks, path_json, created_at)

- **Design notes / tradeoffs:**
   - Storing `path_json` as a JSON blob is simple and fast for an MVP; it makes storing complete plan snapshots easy but complicates querying and updating individual steps. For step-level tracking, move to a normalized `PlanStep` table.
   - `RESOURCES` in JSON is easy to edit and version control; migrating resources into the DB enables richer metadata and admin UIs.
   - The AI layer is optional and replaceable; the app includes a stub to allow offline development.

---

End of use cases and high-level design.
