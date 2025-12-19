<<<<<<< HEAD
# mid
=======
# LearnPath – AI Learning Coach & Learning Path Recommender

LearnPath is a **chat‑based learning path recommender system** that acts as your personal AI learning coach.  
Instead of filling long forms, the user simply **chats with the coach**, and the system builds a **4–6 week personalized learning roadmap** with topics, weekly breakdown and curated resources.

The app includes **user authentication, a dashboard, chat history, saved learning plans, and a dedicated learning path view**.

---

## 🌟 Key Features

### 1. User Accounts & Authentication
  - Saved learning plans  
  - Chat history  
  - Conversation timeline  

### 2. Chat‑Based Learning Coach
  - **Goal / skill** (e.g. *"Python basics"*, *"frontend web dev"*)  
  - **Current level** (Beginner / Intermediate / Advanced)  
  - **Study time** (hours per week, number of weeks – kept between 4 and 6)  

### 3. Personalized Learning Path Generation
- 4–6 week roadmap (depending on the user’s time)  
- Each week has:
  - Topic / focus  
  - Mode (reading, practice, project, etc.)  
- For known goals like **Python** or **Web / Frontend (HTML, CSS, JS)** it attaches curated resources such as:
  - YouTube full‑course videos  
  - Official documentation  

The final plan is saved in the database and can be re‑opened later.

### 4. Dashboard with Chat & Plans
- Shows recent conversations in a **left sidebar**  
- Main area shows:
  - Active chat with the AI coach  
  - Quick stats about plans  
  - Buttons to create a **New Chat** or open your **Learning Path**  
- Each conversation and its messages are stored in the database.

### 5. Learning Path View
Dedicated `/learning-path` page displays:

- User profile summary (goal, level, hours per week, total weeks)  
- Clean card‑based layout of weekly steps  
- Each week:
  - Title / goal for the week  
  - Hours and focus mode  
  - Helpful tips / notes  
- CTA to go back to the dashboard and continue chatting with the coach.

---

## 🧱 Tech Stack

**Backend**
- Python  
- Flask 3  
- Flask‑SQLAlchemy (ORM)  
- SQLite database (`instance/learning_path.db`)  
- dotenv for environment config  

**Frontend**
- HTML + Jinja2 templates (`base.html`, `index.html`, `dashboard.html`, `learning_path.html`, `login.html`, `register.html`)  
- CSS (custom design embedded in `base.html`)  
- Bootstrap 5  
- Boxicons  
- Vanilla JavaScript (for chat API calls and dynamic updates)

---

## 🗂 Project Structure

```bash
mid/
├── app.py                     # Main Flask app (routes, models, logic, chatbot, planner)
├── requirements.txt
├── .env                       # Environment config (ignored in VCS, but present locally)
├── instance/
│   └── learning_path.db       # SQLite database (auto-created)
├── templates/
│   ├── base.html              # Global layout, navbar, styling, scripts
│   ├── index.html             # Landing page / marketing hero
│   ├── dashboard.html         # Chat UI + conversations sidebar
│   ├── learning_path.html     # Generated learning plan view
│   ├── login.html             # Login form
│   └── register.html          # Registration form
├── AI-log.md                  # Notes about AI behaviour / prompts
├── ProblemStatement.md
├── README.md                  # (This file – project documentation)
├── ReleaseRoadmap.md
├── TestPlan.md
└── UI-Sketch-and-Vision.md
```

> Note: There is also a `.venv/` and `venv/` folder in the zip but those are local virtual environments and **not part of the source code**.



## 🌐 Routes / Endpoints

### Page Routes
- `GET /`  
  Landing page (index) with hero section and call‑to‑action to start.

- `GET /register`  
  Show registration form.

- `POST /register`  
  Create a new user, hash password, redirect to dashboard.

- `GET /login`  
  Show login form.

- `POST /login`  
  Authenticate user and open dashboard.

- `GET /logout`  
  Log the user out and clear session.

- `GET /dashboard`  
  Main app page:
  - Chat interface with AI coach  
  - List of user’s past conversations  
  - Quick stats and actions  

- `GET /learning-paths`  
  List of existing learning plans for the user (most recent first).

- `GET /learning-path`  
  Open the latest learning plan for the logged‑in user.

- `GET /learning-path/<int:plan_id>`  
  Open a specific learning plan by its ID.

### API Routes
- `POST /api/chat`  
  Accepts JSON:
  ```json
  { "message": "user text", "conversation_id": optional_id }
  ```
  Behaviour:
  - Saves user message  
  - Runs chatbot logic  
  - Possibly creates or updates a `LearningPlan`  
  - Returns JSON:
  ```json
  {
    "reply": "...bot answer...",
    "plan_ready": true/false,
    "conversation_id": 123,
    "plan_id": 5   // only when a new plan is created
  }
  



## ⚙️ Installation & Setup

### 1️⃣ Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate
# or (cmd): venv\Scripts\activate
# or (macOS / Linux): source venv/bin/activate
```


### 2️⃣ Install Dependencies
From inside the `mid/` folder:

```powershell
pip install -r requirements.txt
```

The `requirements.txt` includes `Flask-SQLAlchemy`, `python-dotenv`, and the optional `google-genai` SDK (used when you provide `GEMINI_API_KEY`).

The example client uses `requests` — install it if you plan to run `example_client.py`:

```powershell
pip install requests
```

### 3️⃣ Environment Variables
Create a `.env` file in `mid/` (if not already present) with at least:

```
FLASK_SECRET_KEY=some-secret-key
GEMINI_API_KEY=your_gemini_api_key_optional
```

The app uses `instance/learning_path.db` by default (the `instance/` folder is created automatically), so SQLite works out of the box.

### 4️⃣ Run the App (development)
```powershell
python app.py
```

By default it runs in **debug mode** on:

http://127.0.0.1:5000/

### 5️⃣ Quick programmatic example (example_client.py)
There's a small example script `example_client.py` that demonstrates registering/logging in and sending chat messages programmatically. It simulates the minimal flow that produces a learning plan.

Run it while the Flask app is running:
```powershell
python example_client.py
```

Example expected console output (shortened):

```
Registered and logged in as new test user.
-> Sending: Hi
<- Reply: Hey, nice to meet you! How is life going these days? ...
-> Sending: I want to learn Python
<- Reply: Great, you want to learn something. First, tell me what skill or goal you have in mind.
-> Sending: Beginner
-> Sending: I can study 5 hours per week for 5 weeks
<- Reply: Done! I have created a custom learning path for you focusing on Python Programming at Beginner level, 5 hours per week for 5 weeks.
Plan created! plan_id: 7
You can open the plan at: http://127.0.0.1:5000/learning-path/7
```

The `learning_path` page will render the plan with weekly steps and suggested resources loaded from `data/resources.json`.

## 🔮 Future Improvements

- More advanced AI logic for plan generation  
- Support for more domains (data science, mobile dev, etc.)  
- Progress completion buttons directly on the learning path steps  
- Email verification and password reset  
- Rich analytics dashboard for tracking study consistency  

---

## 👨‍💻 Author / Contributors

- **Ahad Ali** – Full‑stack developer (Flask + Frontend)  

 
>>>>>>> 4011cce (Initial commit)
