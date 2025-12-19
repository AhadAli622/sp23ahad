# Problem Statement – Learning Path Recommender System

## Background
Students today rely heavily on online learning platforms, tutorials, videos, and documentation to gain new skills. Although there is an abundance of learning material, the lack of structure often creates confusion instead of clarity. Learners struggle to decide where to start, which topic to learn next, and how to track their overall progress in a meaningful way.

This project aims to design and implement a **Learning Path Recommender System** that generates structured, personalized learning paths for users based on their current skill level, learning goals, and preferences.



## Primary Users

### 1. Beginners / Students
Learners who want to start a new technology or skill (e.g., Python, Web Development, AI/ML) but do not know the correct order of topics and concepts.

### 2. Intermediate Learners
Users who are familiar with the basics but need guidance on what to learn next in order to advance and fill their knowledge gaps.

### 3. Self-paced Independent Learners
Individuals who prefer to learn on their own from multiple sources (videos, articles, blogs, documentation) instead of following a fixed, rigid course.

*(Optional future group)*  
### 4. Educators / Mentors
Instructors who may want to provide pre-defined or semi-personalized paths to their students in later versions of the system.

---

## Pain Points

### 1. Lack of a Structured Roadmap
Most learners do not have a clear, step-by-step roadmap. They jump randomly between tutorials, which leads to gaps in their understanding.

### 2. Resource Overload
There are too many learning resources available online. Without guidance, it is difficult for learners to select resources that match their level and goals.

### 3. Difficulty Tracking Progress
Learners often forget which topics they have already covered and which ones are still pending, making it hard to maintain consistency and long-term progress.

### 4. One-Size-Fits-All Courses
Traditional courses follow a fixed sequence and do not adapt to the learner’s existing knowledge, preferred learning style, or pace. This reduces engagement and effectiveness.

---

## Why the Problem Matters

- Students waste significant time on content that is either too basic or too advanced for them.  
- A lack of direction causes frustration, demotivation, and drop-off from self-learning.  
- Personalized, adaptive learning paths can make the learning process more efficient, focused, and enjoyable.  
- A structured system can help learners clearly see where they stand and what they should learn next, leading to measurable progress.

By tackling these issues, the Learning Path Recommender System supports more effective self-learning and improves the overall learning experience.

---

## Scope of the Project (Mid-Semester Version)

For the mid-semester milestone, the focus is on delivering a **functional core prototype** of the system.

### In Scope (Mid-Sem)

- Basic **user profile setup**  
  - Current skill level (e.g., Beginner, Intermediate)  
  - Learning goals (e.g., learn Python basics, web dev fundamentals)  
  - Simple preferences (e.g., preferred content type: video, article, etc. – optional)  

- A manually curated **dataset of learning resources**  
  - Categorized by topic, difficulty level, and format  
  - Stored in a structured format (e.g., JSON, CSV, or database)

- A **rule-based recommendation engine** (implemented in Flask backend)  
  - Uses simple rules and topic ordering to generate a learning path  
  - Selects the next resource based on difficulty, prerequisites, and user progress  

- A minimal **web-based user interface**  
  - **Frontend:** HTML, CSS, JavaScript  
  - **Backend:** Flask (Python)  
  - Allows users to:  
    - Create or select a profile  
    - View their recommended learning path  
    - Mark topics/resources as completed  

- **Progress updating**  
  - When a user completes a topic, the system updates their status and recommends the next step.

These features are sufficient to demonstrate the main concept and workflow of the Learning Path Recommender.

> Note: In the current MVP the UI and backend store learning plans and show steps, but explicit per-step "mark complete" functionality is planned for the next iteration (see ReleaseRoadmap / ToDo).

---

## Explicit Out-of-Scope Features (For Now)

The following features are **not** included in the mid-semester version and may be considered for the final project or future work:

- Advanced machine learning models (e.g., collaborative filtering, deep learning-based recommenders)  
- Automatic web scraping or live integration with external platforms (YouTube, Coursera, etc.)  
- Complex analytics or dashboards for detailed progress visualization  
- Complex analytics or dashboards for detailed progress visualization  
- Full user authorization and advanced role management — OUT OF SCOPE for the mid-semester version.

  Note: Basic user authentication (register/login/logout with password hashing) is implemented in the MVP; advanced role-based authorization and permissions are planned for later versions.
- Large-scale multi-user recommendation based on usage data  
- Native mobile applications (Android/iOS)
