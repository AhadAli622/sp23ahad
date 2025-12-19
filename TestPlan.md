# Test Plan – LearnPath (AI Learning Coach & Learning Path Recommender)

## 1. Introduction

This document describes the test plan for the **LearnPath** web application, a chat-based learning path recommender system built with **Flask (backend)** and **HTML/CSS/JS (frontend)**.  
The goal of testing is to ensure that:

- User authentication works correctly  
- Chat-based interaction behaves as expected  
- Learning plans are generated, stored, and displayed properly  
- Navigation, routes, and basic flows are stable  

---

## 6. Additional Test Cases (Focused checks)

### TC-EX-01 – Learning Plan Creation (Complete Info)

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in and on `/dashboard`. No recent open plan exists for this conversation. |
| **Input (Sequence)** | 1) "I want to learn Python." 2) "Beginner." 3) "I can study 5 hours per week for 5 weeks." |
| **Steps**        | 1. Send first message via the chat UI. 2. Respond to bot prompts until hours/weeks provided. 3. Observe API response from `/api/chat`. |
| **Expected**     | - `/api/chat` returns JSON with `plan_ready: true` and a `plan_id`.
|                  | - A `LearningPlan` row is created with matching `goal`, `level`, `hours_per_week`, `duration_weeks`.
|                  | - The learning path page `/learning-path/<plan_id>` renders the generated steps and resources. |

---

### TC-EX-02 – Resource Suggestion for Multiple Programming Languages

| Field            | Description |
|------------------|-------------|
| **Precondition** | `data/resources.json` contains entries for the target language (e.g., JavaScript, Rust). User is logged in. |
| **Input**        | User goal: "I want to learn Rust"; level: "Beginner"; time: "4 hours per week for 4 weeks". |
| **Steps**        | 1. Provide goal/level/time via chat to create a plan. 2. Open `/learning-path/<plan_id>`. 3. Inspect `resources` shown for each week and search for Rust-related entries. |
| **Expected**     | - At least one resource shown per relevant week where the `categories` include "Rust".
|                  | - Resource entries include `title`, `type`, and `url` and are clickable in the UI.
|                  | - If none matched, UI shows fallback resources and server logs a missing-match warning. |

---

### TC-EX-03 – AI Quota / Fallback Behavior

| Field            | Description |
|------------------|-------------|
| **Precondition** | Gemini API key not set or the service returns an error/429. The app is running. |
| **Input**        | Send the sequence to generate a plan (goal, level, hours/weeks) via chat. |
| **Steps**        | 1. Trigger plan creation via the chat flow. 2. Observe server logs for AI error messages. 3. Inspect `/api/chat` response. |
| **Expected**     | - If Gemini fails, the backend uses `call_ai_api_stub(history)` and continues the guided flow.
|                  | - `/api/chat` should still eventually return a reply; `plan_ready` may be true if the stub produced JSON.
|                  | - Server logs should contain the Gemini error and a message indicating the stub was used. |

---

### TC-EX-04 – Database File Path Verification

| Field            | Description |
|------------------|-------------|
| **Precondition** | App is configured and started. The `instance/` folder exists (app creates it automatically on startup). |
| **Input**        | Start the app and create a simple record (e.g., register a user or generate a plan). |
| **Steps**        | 1. Start the Flask app. 2. Register a test user. 3. Check filesystem for `instance/learning_path.db`. 4. Optionally, query SQLite to confirm tables exist (e.g., using `sqlite3`). |
| **Expected**     | - `instance/learning_path.db` file exists in the project `instance/` directory.
|                  | - Tables `users`, `conversations`, `chat_messages`, and `learning_plans` are present.
|                  | - New rows (user, plan) are persisted and retrievable after restart. |

For each test case, we define **inputs, steps, expected outputs, and actual outcomes**.

> **Note:** The **Actual Outcome** and **Status** columns should be filled during manual testing.

---

## 2. Scope

### In Scope
- User registration and login  
- Session handling (login/logout, access control)  
- Dashboard and conversation listing  
- `/api/chat` endpoint behavior  
- Learning plan creation and viewing (`/learning-path`, `/learning-path/<id>`)  
- Basic validations (empty input, invalid credentials, etc.)

### Out of Scope
- Performance testing  
- Security penetration testing  
- Cross-browser compatibility in depth  

---

## 3. Test Environment

- **Backend:** Python, Flask  
- **Database:** SQLite (`instance/learning_path.db`)  
- **Frontend:** HTML, CSS, JS, Bootstrap  
- **Browser:** Chrome (latest)  
- **OS:** Windows / Linux / macOS  

---

## 4. Test Cases

### 4.1 Authentication & User Management

#### TC-AUTH-01 – User Registration (Valid)

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is not logged in. No existing account with the same email. |
| **Input**        | Name: `Test User`<br>Email: `testuser@example.com`<br>Password: `Test@1234` |
| **Steps**        | 1. Open `/register` page.<br>2. Fill in valid name, email, and password.<br>3. Click **Register** button. |
| **Expected**     | - User is created in database.<br>- Redirected to dashboard `/dashboard`.<br>- Flash message: “Registration successful. Welcome!” |
| **Actual Outcome** | _To be filled during testing_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-AUTH-02 – Registration with Existing Email

| Field            | Description |
|------------------|-------------|
| **Precondition** | A user already exists with `testuser@example.com`. |
| **Input**        | Name: `New User`<br>Email: `testuser@example.com`<br>Password: `Another@123` |
| **Steps**        | 1. Open `/register`.<br>2. Enter existing email.<br>3. Submit form. |
| **Expected**     | - Registration fails.<br>- Error/flash message shown (e.g., “Email already registered” or DB unique constraint error handled).<br>- User is not logged in. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-AUTH-03 – Login with Valid Credentials

| Field            | Description |
|------------------|-------------|
| **Precondition** | User exists with email `testuser@example.com` and known password. |
| **Input**        | Email: `testuser@example.com`<br>Password: `Test@1234` |
| **Steps**        | 1. Open `/login`.<br>2. Enter valid email and password.<br>3. Click **Login**. |
| **Expected**     | - User is authenticated.<br>- `session["user_id"]` is set.<br>- Redirect to `/dashboard`.<br>- Flash: “Logged in successfully.” |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-AUTH-04 – Login with Invalid Credentials

| Field            | Description |
|------------------|-------------|
| **Precondition** | User exists in database. |
| **Input**        | Email: `testuser@example.com`<br>Password: `WrongPassword` |
| **Steps**        | 1. Go to `/login`.<br>2. Enter valid email and wrong password.<br>3. Click **Login**. |
| **Expected**     | - Login fails.<br>- Stay on or return to `/login`.<br>- Flash message: “Invalid credentials.” |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-AUTH-05 – Logout

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in. |
| **Input**        | N/A (click logout) |
| **Steps**        | 1. Click **Logout** in navbar.<br>2. Observe behavior. |
| **Expected**     | - Session `user_id` is removed.<br>- Flash: “You have been logged out.”<br>- Redirect to home or login page. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

### 4.2 Access Control & Navigation

#### TC-ACC-01 – Access Dashboard Without Login

| Field            | Description |
|------------------|-------------|
| **Precondition** | No active session (not logged in). |
| **Input**        | Direct URL: `/dashboard` |
| **Steps**        | 1. Open browser.<br>2. Manually type `/dashboard`. |
| **Expected**     | - User is redirected to login page or shown an error.<br>- No dashboard data is visible. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-ACC-02 – Open Learning Path Without Plan

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in but has no `LearningPlan` entries. |
| **Input**        | URL: `/learning-path` |
| **Steps**        | 1. Login.<br>2. In browser, go to `/learning-path`. |
| **Expected**     | - User is redirected back to dashboard.<br>- Flash message: “No learning path yet. Use the chatbot on the dashboard to create one.” |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

### 4.3 Chatbot API & Conversation Flow

#### TC-CHAT-01 – Send Empty Chat Message

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in and on dashboard.<br>JS calls `/api/chat`. |
| **Input (JSON)** | `{ "message": "", "conversation_id": null }` |
| **Steps**        | 1. In chat box, click **Send** with empty message.<br>2. Observe network response (in DevTools) or UI reply. |
| **Expected**     | - API responds with: `{"reply": "Please type a message first.", "plan_ready": false, ...}`<br>- No new conversation content should be added. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-CHAT-02 – Start New Chat Conversation

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in. |
| **Input (JSON)** | `{ "message": "Hi", "conversation_id": null }` |
| **Steps**        | 1. Type “Hi” in chat.<br>2. Click Send.<br>3. Check if `/api/chat` returns a `conversation_id` and a friendly greeting reply. |
| **Expected**     | - New `Conversation` row is created in DB for this user.<br>- New `ChatMessage` with role `"user"` and `"assistant"` stored.<br>- Response JSON includes `conversation_id` and `plan_ready: false`. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-CHAT-03 – Guided Questions for Goal, Level, and Time

| Field            | Description |
|------------------|-------------|
| **Precondition** | Active conversation exists. |
| **Input (Sequence)** | 1. “I want to learn Python.”<br>2. “Beginner.”<br>3. “I can study 5 hours per week for 5 weeks.” |
| **Steps**        | 1. Send first message and observe bot reply (should ask about level/time if missing).<br>2. Send second message (level) and observe.<br>3. Send time commitment.<br>4. Observe when bot says it will create a plan. |
| **Expected**     | - Bot asks follow-up questions until it has **goal, level, hours/week, weeks**.<br>- Final message before plan creation mentions creating a roadmap or plan. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-CHAT-04 – Learning Plan Creation (Plan Ready)

| Field            | Description |
|------------------|-------------|
| **Precondition** | Conversation has enough info for JSON plan (goal, level, hours/week, weeks). |
| **Input**        | Last message completing info, e.g. “I can give 6 hours per week for 4 weeks.” |
| **Steps**        | 1. Send final detail.<br>2. Check API response.<br>3. Inspect database for new `LearningPlan`. |
| **Expected**     | - `/api/chat` returns `plan_ready: true` and a `plan_id` field.<br>- `LearningPlan` row created with matching goal, level, and a JSON path.<br>- Bot reply acknowledges that a learning plan has been created. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

### 4.4 Learning Path View

#### TC-LP-01 – Open Latest Learning Path

| Field            | Description |
|------------------|-------------|
| **Precondition** | User has at least one `LearningPlan` saved. |
| **Input**        | URL: `/learning-path` |
| **Steps**        | 1. Login as user with saved plan.<br>2. Navigate to **View Learning Path** (or directly go to `/learning-path`). |
| **Expected**     | - Page renders `learning_path.html`.<br>- Shows profile summary (goal, level, hours_per_week, duration_weeks).<br>- Shows list of weekly steps (loop over `path` JSON). |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-LP-02 – Open Specific Learning Path by ID

| Field            | Description |
|------------------|-------------|
| **Precondition** | There are multiple `LearningPlan` entries for the user. |
| **Input**        | URL: `/learning-path/<plan_id>` with a valid plan id belonging to this user. |
| **Steps**        | 1. Login.<br>2. Go to `/learning-paths` (if implemented) or directly type a known `plan_id`.<br>3. Open `/learning-path/<plan_id>`. |
| **Expected**     | - Correct plan is loaded.<br>- Summary matches that specific plan.<br>- Path list corresponds to the selected plan. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

### 4.5 Negative & Edge Cases

#### TC-NEG-01 – Access Another User’s Plan ID (If Forced via URL)

| Field            | Description |
|------------------|-------------|
| **Precondition** | Two users exist, User A and User B. User B has a `plan_id` that User A does not own. |
| **Input**        | Logged in as User A, open `/learning-path/<plan_id_of_B>`. |
| **Steps**        | 1. Login as User A.<br>2. Try to manually access a plan id belonging to User B (if known). |
| **Expected**     | - Ideally: User should not be able to see another user’s plan (access is restricted).<br>- If not implemented, this should be noted as a **security improvement**. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

#### TC-NEG-02 – Invalid Plan ID

| Field            | Description |
|------------------|-------------|
| **Precondition** | User is logged in. |
| **Input**        | URL: `/learning-path/99999` (where `99999` does not exist). |
| **Steps**        | 1. Login.<br>2. Try to open a non-existing plan id. |
| **Expected**     | - App should handle gracefully (404 or redirect with flash message).<br>- No app crash or unhandled exception. |
| **Actual Outcome** | _To be filled_ |
| **Status**       | _Pass / Fail_ |

---

## 5. Summary

This **TestPlan.md** provides a structured way to verify:

- Correctness of main flows (login, chat, plan creation, viewing).  
- Stability of critical routes.  
- Basic validation and error handling.  

The **Actual Outcome** and **Status** columns should be updated after running each test case manually.

