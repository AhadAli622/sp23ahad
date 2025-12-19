from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import os
import json
import re

# Gemini SDK
from google import genai

# -------------------- Config & Setup -------------------- #

load_dotenv()

# ✅ Yahan sahi config
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-prod")

# Ensure the `instance/` directory exists and use it for the SQLite DB (Flask convention)
instance_dir = os.path.join(os.path.dirname(__file__), "instance")
os.makedirs(instance_dir, exist_ok=True)

# Use instance/learning_path.db as the SQLite database file
db_path = os.path.join(instance_dir, "learning_path.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.replace('\\\\', '/') }"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------- Gemini Client Setup -------------------- #

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ai_client = None
if GEMINI_KEY:
    try:
        ai_client = genai.Client(api_key=GEMINI_KEY)
        print("✅ Gemini client initialized.")
    except Exception as e:
        print("❌ Gemini init failed, using stub:", e)
        ai_client = None
else:
    print("⚠️ GEMINI_API_KEY not set, using stub AI.")

# -------------------- SYSTEM INSTRUCTIONS -------------------- #

SYSTEM_INSTRUCTIONS = (
    "You are a friendly learning coach.\n"
    "You reply in clear, simple English.\n\n"
    "Chat flow:\n"
    "- When a new chat starts, do NOT immediately ask about skills or learning.\n"
    "- First, respond naturally to greetings and how-they-are type messages.\n"
    "- Light small talk is allowed as long as it stays meaningful (routine, habits, productivity, study).\n"
    "- Do NOT talk about random unrelated topics like politics or celebrity gossip.\n\n"
    "Learning trigger:\n"
    "- Move into learning/skill mode only when the user clearly shows interest, for example:\n"
    "  'I want to learn', 'I want a skill', 'I want to learn Python', 'suggest a skill',\n"
    "  or they mention a specific topic they want to study.\n"
    "- You can gently suggest learning if they say things like 'I am bored', 'wasting time', "
    "  or 'I want to be more productive', but do it softly, not forcefully.\n\n"
    "Order of questions in learning mode (very important):\n"
    "1) First, ask and confirm the target skill or learning goal "
    "(for example: 'become a junior web developer', 'learn Python basics', 'basics of data analysis').\n"
    "2) Then ask for current skill level (Beginner / Intermediate / Advanced).\n"
    "3) Then ask about their background (for example: 'CS student', 'no coding before', 'know basic HTML/CSS').\n"
    "4) Finally, ask about time availability: hours per week and how many weeks they can follow a plan.\n\n"
    "You are designing a short, prioritized learning path and a simple 4–6 week roadmap.\n"
    "- Focus on a realistic, ordered sequence of topics and activities.\n"
    "- Prefer a focused path over a huge random list of resources.\n\n"
    "When (and ONLY when) you have all required info, you must send ONLY a JSON object "
    "with this exact format:\n"
    "{ \"language\": \"<Skill or detailed goal>\", "
    "\"level\": \"<Beginner/Intermediate/Advanced>\", "
    "\"hours\": <hours per week integer>, "
    "\"weeks\": <total weeks integer between 4 and 6> }\n\n"
    "Do not assume the skill is Python. The 'language' field must match the user's described goal.\n"
    "Make sure weeks is between 4 and 6. If the user gives more or less, you choose a reasonable value in [4, 6].\n"
    "No extra text, no emojis, no explanation before or after the JSON when you send it.\n"
    "If you cannot understand the numbers, default to hours = 5 and weeks = 4.\n"
    "Until you send JSON, keep chatting normally in friendly English.\n"
)

# -------------------- Database Models -------------------- #

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    plans = db.relationship("LearningPlan", backref="user", lazy=True)
    messages = db.relationship("ChatMessage", backref="user", lazy=True)
    conversations = db.relationship("Conversation", backref="user", lazy=True)


class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False, default="New chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship("ChatMessage", backref="conversation", lazy=True)


class LearningPlan(db.Model):
    __tablename__ = "learning_plans"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    goal = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False)
    duration_weeks = db.Column(db.Integer, nullable=False)

    path_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # "user" or "assistant"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- Helper Utilities -------------------- #

def current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# -------------------- External Resources Loading -------------------- #
try:
    resources_file = os.path.join(os.path.dirname(__file__), "data", "resources.json")
    if os.path.exists(resources_file):
        with open(resources_file, "r", encoding="utf-8") as f:
            RESOURCES = json.load(f)
    else:
        RESOURCES = []
except Exception:
    RESOURCES = []


def detect_goal_from_text(text: str) -> str:
    t = text.lower()

    if "python" in t:
        return "Python Programming"
    if any(k in t for k in ["web dev", "web development", "frontend", "backend", "html", "css", "javascript", "js"]):
        return "Web Development"
    if any(k in t for k in ["data analysis", "data analytics", "analytics", "data science"]):
        return "Data Analysis"
    if any(k in t for k in ["machine learning", "ml", "ai"]):
        return "Machine Learning"
    if "sql" in t:
        return "SQL and Databases"
    if any(k in t for k in ["ui/ux", "ux design", "ui design", "graphic design"]):
        return "UI/UX / Design"

    return "Your learning goal"


# Extended language detection (covers many common programming languages)
LANGUAGE_KEYWORDS = {
    "python": "Python Programming",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "php": "PHP",
    "ruby": "Ruby",
    "r": "R",
    "sql": "SQL",
    "matlab": "MATLAB",
    "scala": "Scala",
    "perl": "Perl",
}


def detect_programming_language(text: str) -> str | None:
    t = (text or "").lower()
    for k, name in LANGUAGE_KEYWORDS.items():
        if k in t:
            return name
    return None


def suggest_resources(goal, level, topic):
    # Prefer externalized curated resources from data/resources.json if available.
    try:
        resources_list = RESOURCES  # loaded at module import
    except NameError:
        resources_list = []

    g = (goal or "").lower()
    lvl = (level or "").lower()

    matched = []

    # Match resources by category and level
    for r in resources_list:
        try:
            cats = [c.lower() for c in r.get("categories", [])]
            r_level = (r.get("level") or "all").lower()

            category_match = any(
                (cat in g) or (cat in topic.lower()) or (cat in [x.lower() for x in [goal]])
                for cat in cats
            )

            level_match = (r_level == "all") or (r_level == lvl) or (lvl == "")

            if category_match and level_match:
                matched.append(r.copy())
        except Exception:
            continue

    # If no matches found, try looser matching (category substring in goal)
    if not matched and resources_list:
        for r in resources_list:
            try:
                cats = [c.lower() for c in r.get("categories", [])]
                if any(cat in g for cat in cats):
                    matched.append(r.copy())
            except Exception:
                continue

    # Fallback to small built-in suggestions if no external resources available
    if not matched:
        # simple fallback list
        matched = [
            {"type": "video", "title": "How to Learn Anything Fast – Ali Abdaal", "url": "https://www.youtube.com/watch?v=LPDhuthFD98", "level_note": "general"},
            {"type": "text", "title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "level_note": "general"},
        ]

    # Attach a level note if missing
    for r in matched:
        if "level_note" not in r:
            r["level_note"] = (
                "better for beginners" if lvl == "beginner"
                else "good for intermediate learners" if lvl == "intermediate"
                else "you can skim basics and focus on advanced parts"
            )

    return matched


def generate_learning_path(profile):
    goal = profile["goal"]
    level = profile["level"]
    hours_per_week = profile["hours_per_week"]
    weeks = profile["duration_weeks"]

    if weeks < 4:
        weeks = 4
    elif weeks > 6:
        weeks = 6

    total_hours = hours_per_week * weeks

    base_topics = [
        (f"{goal} – Fundamentals", 4, "videos + small exercises"),
        ("Core Concepts & Practice", 4, "guided exercises"),
        ("Applied Practice & Mini Tasks", 4, "practice problems"),
        (f"Project-Oriented {goal}", 4, "mini project"),
        (f"Deepening {goal} Skills", 4, "tutorial + implementation"),
        (f"Capstone / Portfolio Piece in {goal}", 4, "project work"),
    ]

    if level.lower() == "intermediate":
        base_topics = base_topics[1:]
    elif level.lower() == "advanced":
        base_topics = [
            (f"Advanced concepts in {goal}", 5, "reading + coding"),
            (f"Best practices, patterns & optimization ({goal})", 5, "experiments"),
            (f"Capstone / real-world style project in {goal}", 6, "project"),
        ]

    estimated_sum = sum(t[1] for t in base_topics)
    if total_hours < estimated_sum:
        chosen = []
        used = 0
        for topic, hours, mode in base_topics:
            if used + hours > total_hours:
                break
            chosen.append((topic, hours, mode))
            used += hours
        if not chosen:
            t = base_topics[0]
            chosen = [(t[0], min(t[1], total_hours), t[2])]
    else:
        chosen = base_topics

    num_steps = len(chosen)
    path = []
    if num_steps == 0:
        return path

    step_index = 0
    for week in range(1, weeks + 1):
        if step_index >= num_steps:
            break

        topic, hours, mode = chosen[step_index]
        step_index += 1

        base_resources = suggest_resources(goal, level, topic)

        path.append({
            "week": week,
            "step": len(path) + 1,
            "topic": topic,
            "hours": hours,
            "mode": mode,
            "resources": base_resources,
        })

    return path

# -------------------- AI: Stub + Gemini -------------------- #

def call_ai_api_stub(history):
    user_text_all = " ".join(
        m["content"].lower() for m in history if m["role"] == "user"
    )

    last_user_msg = ""
    for msg in reversed(history):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break
    text = last_user_msg.lower()

    learning_intent_keywords = [
        "learn", "learning", "skill", "course", "class",
        "python", "javascript", "web dev", "web development",
        "programming", "coding", "frontend", "backend",
        "data analysis", "data science"
    ]
    has_learning_intent = any(kw in user_text_all for kw in learning_intent_keywords)

    skill_keywords = [
        "python", "javascript", "web dev", "web development",
        "frontend", "backend", "html", "css", "data analysis",
        "data analytics", "data science", "sql", "ui/ux",
        "ux design", "ui design", "graphic design", "machine learning", "ml", "ai"
    ]
    has_goal = any(kw in user_text_all for kw in skill_keywords)

    has_level = any(
        w in user_text_all for w in ["beginner", "intermediate", "advanced"]
    )
    has_time = bool(
        re.search(r"\b\d+\s*(hour|hours|hr|hrs)\b", user_text_all)
    ) and bool(
        re.search(r"\b\d+\s*(week|weeks)\b", user_text_all)
    )

    if has_learning_intent and has_goal and has_level and has_time:
        goal_name = detect_goal_from_text(user_text_all)

        if "intermediate" in user_text_all:
            level_val = "intermediate"
        elif "advanced" in user_text_all:
            level_val = "advanced"
        else:
            level_val = "beginner"

        hours_match = re.search(r"(\d+)\s*(hour|hours|hr|hrs)\b", user_text_all)
        weeks_match = re.search(r"(\d+)\s*(week|weeks)\b", user_text_all)

        hours_val = int(hours_match.group(1)) if hours_match else 5
        weeks_val = int(weeks_match.group(1)) if weeks_match else 4

        if weeks_val < 4:
            weeks_val = 4
        elif weeks_val > 6:
            weeks_val = 6

        return json.dumps({
            "language": goal_name,
            "level": level_val.capitalize(),
            "hours": hours_val,
            "weeks": weeks_val,
        })

    if has_learning_intent:
        if not has_goal:
            return (
                "Great, you want to learn something.\n"
                "First, tell me what skill or goal you have in mind. "
                "For example: 'Python programming', 'become a junior web developer', "
                "'basics of data analysis', or something similar."
            )
        if not has_level:
            return (
                "Nice, that is a good goal.\n"
                "How would you describe your current level in this area? "
                "Beginner, Intermediate, or Advanced?"
            )
        if not has_time:
            return (
                "Got it. Now tell me roughly how many hours per week you can study, "
                "and for how many weeks you want to follow a plan (ideally 4–6 weeks)."
            )
        return (
            "Your learning direction is getting clear.\n"
            "Once we have the exact skill, your level, and your time per week and weeks, "
            "I will create a focused 4–6 week roadmap for you."
        )

    if any(kw in text for kw in ["hi", "hello", "hey"]):
        return (
            "Hey, nice to meet you! How is life going these days? "
            "Are you usually busy with work or studies, or more relaxed?"
        )

    if "how are you" in text:
        return (
            "I'm doing well, thanks for asking! How are you feeling these days? "
            "Where does most of your time go – work, university, games, or just scrolling?"
        )

    if any(kw in text for kw in ["bored", "waste time", "wasting time", "unproductive"]):
        return (
            "I get that, it feels bad when time just slips away.\n"
            "If you want, we can slowly turn this into some kind of learning or skill-building routine "
            "that fits your schedule. First, tell me a bit about your daily routine."
        )

    return (
        "Alright, I understand.\n"
        "Tell me a little about your daily routine — when you wake up, work or study, "
        "and when you usually have free time. Later, if you want to learn a skill, "
        "we can design a plan that fits that routine."
    )


def call_ai_api(history):
    print("🧠 Calling Gemini AI...")

    if not ai_client:
        print("➡️ No Gemini client, using stub.")
        return call_ai_api_stub(history)

    try:
        convo_lines = []
        for msg in history:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            convo_lines.append(f"{prefix}: {msg['content']}")
        conversation_text = "\n".join(convo_lines)

        full_prompt = SYSTEM_INSTRUCTIONS + "\n\nConversation so far:\n" + conversation_text

        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )

        text = (response.text or "").strip()
        print("🤖 Gemini raw response:", text)
        return text

    except Exception as e:
        print("❌ Gemini error, using stub:", e)
        return call_ai_api_stub(history)

# -------------------- Template Context -------------------- #

@app.context_processor
def inject_user():
    return {"user": current_user()}

# -------------------- Routes: Auth -------------------- #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        flash("Registration successful. Welcome!")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials.")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Logged in successfully.")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))

# -------------------- Routes: Chats & Plans -------------------- #

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()

    conv_id = request.args.get("conversation_id", type=int)

    conversations = (
        Conversation.query
        .filter_by(user_id=user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    active_conversation = None
    if conv_id:
        active_conversation = Conversation.query.filter_by(
            id=conv_id, user_id=user.id
        ).first()

    if not active_conversation:
        if conversations:
            active_conversation = conversations[0]
        else:
            active_conversation = Conversation(user_id=user.id, title="New chat")
            db.session.add(active_conversation)
            db.session.commit()
            conversations.append(active_conversation)

    messages = (
        ChatMessage.query
        .filter_by(user_id=user.id, conversation_id=active_conversation.id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    # 🔹 ALL learning plans for this user (latest first)
    plans = (
        LearningPlan.query
        .filter_by(user_id=user.id)
        .order_by(LearningPlan.created_at.desc())
        .all()
    )
    last_plan = plans[0] if plans else None

    last_plan_steps = None
    if last_plan:
        try:
            last_plan_steps = json.loads(last_plan.path_json)
        except json.JSONDecodeError:
            last_plan_steps = None

    return render_template(
        "dashboard.html",
        messages=messages,
        last_plan=last_plan,
        last_plan_steps=last_plan_steps,
        conversations=conversations,
        active_conversation=active_conversation,
        plans=plans,   # ✅ yahan se tum history UI mein dikha sakte ho
    )


@app.route("/new-chat")
@login_required
def new_chat():
    user = current_user()
    conv = Conversation(user_id=user.id, title="New chat")
    db.session.add(conv)
    db.session.commit()
    return redirect(url_for("dashboard", conversation_id=conv.id))

# ✅ NEW: saari learning paths ki list
@app.route("/learning-paths")
@login_required
def all_learning_paths():
    user = current_user()
    plans = (
        LearningPlan.query
        .filter_by(user_id=user.id)
        .order_by(LearningPlan.created_at.desc())
        .all()
    )
    return render_template("learning_paths_list.html", plans=plans)


@app.route("/learning-path")
@app.route("/learning-path/<int:plan_id>")
@login_required
def learning_path(plan_id=None):
    user = current_user()

    if plan_id is not None:
        plan = LearningPlan.query.filter_by(
            id=plan_id,
            user_id=user.id
        ).first()
        if not plan:
            flash("That learning path was not found.")
            return redirect(url_for("dashboard"))
    else:
        plan = (
            LearningPlan.query.filter_by(user_id=user.id)
            .order_by(LearningPlan.created_at.desc())
            .first()
        )
        if not plan:
            flash("No learning path yet. Use the chatbot on the dashboard to create one.")
            return redirect(url_for("dashboard"))

    steps = json.loads(plan.path_json)
    profile = {
        "goal": plan.goal,
        "level": plan.level,
        "hours_per_week": plan.hours_per_week,
        "duration_weeks": plan.duration_weeks,
    }

    return render_template("learning_path.html", profile=profile, path=steps, plan=plan)


@app.route("/api/chat", methods=["POST"])
@login_required
def chat_api():
    user = current_user()
    data = request.get_json(force=True) or {}
    user_message = (data.get("message") or "").strip()
    conv_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"reply": "Please type a message first.", "plan_ready": False})

    conversation = None
    if conv_id:
        conversation = Conversation.query.filter_by(
            id=conv_id, user_id=user.id
        ).first()

    if not conversation:
        conversation = (
            Conversation.query
            .filter_by(user_id=user.id)
            .order_by(Conversation.updated_at.desc())
            .first()
        )
        if not conversation:
            conversation = Conversation(user_id=user.id, title="New chat")
            db.session.add(conversation)
            db.session.commit()

    db_messages = (
        ChatMessage.query
        .filter_by(user_id=user.id, conversation_id=conversation.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in db_messages]

    history.append({"role": "user", "content": user_message})
    db_msg = ChatMessage(
        user_id=user.id,
        conversation_id=conversation.id,
        role="user",
        content=user_message
    )
    db.session.add(db_msg)

    if conversation.title == "New chat":
        conversation.title = (user_message[:40] + "…") if len(user_message) > 40 else user_message

    ai_text = call_ai_api(history).strip()
    bot_reply = ai_text
    plan_ready = False

    json_matches = re.findall(r"\{.*?\}", ai_text, re.DOTALL)
    for json_str in json_matches:
        try:
            data_obj = json.loads(json_str)
            if all(k in data_obj for k in ["language", "level", "hours", "weeks"]):
                hours = int(data_obj["hours"])
                weeks = int(data_obj["weeks"])

                if weeks < 4:
                    weeks = 4
                elif weeks > 6:
                    weeks = 6

                profile = {
                    "goal": data_obj["language"],
                    "level": data_obj["level"],
                    "hours_per_week": hours,
                    "duration_weeks": weeks,
                }

                steps = generate_learning_path(profile)

                plan = LearningPlan(
                    user_id=user.id,
                    goal=profile["goal"],
                    level=profile["level"],
                    hours_per_week=profile["hours_per_week"],
                    duration_weeks=profile["duration_weeks"],
                    path_json=json.dumps(steps),
                )

                plan_ready = True
                bot_reply = (
                    f"Done! I have created a custom learning path for you focusing on "
                    f"{profile['goal']} at {profile['level']} level, "
                    f"{profile['hours_per_week']} hours per week for {profile['duration_weeks']} weeks."
                )

                db_bot = ChatMessage(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    role="assistant",
                    content=bot_reply,
                )

                conversation.updated_at = datetime.utcnow()

                db.session.add(plan)
                db.session.add(db_bot)
                db.session.commit()

                return jsonify({
                    "reply": bot_reply,
                    "plan_ready": plan_ready,
                    "conversation_id": conversation.id,
                    "plan_id": plan.id,   # ✅ specific plan ka id
                })
        except Exception as e:
            print("JSON parse error or save error:", e, "RAW:", ai_text)

    db_bot = ChatMessage(
        user_id=user.id,
        conversation_id=conversation.id,
        role="assistant",
        content=bot_reply,
    )
    conversation.updated_at = datetime.utcnow()
    db.session.add(db_bot)
    db.session.commit()

    return jsonify({
        "reply": bot_reply,
        "plan_ready": plan_ready,
        "conversation_id": conversation.id,
    })

# -------------------- Create tables -------------------- #

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Disable the reloader to keep a single process (easier to run inside this environment)
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
