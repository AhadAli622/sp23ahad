# UI Sketch and Vision

## Design Goals

- Clean, minimal, student-friendly look.
- Fully responsive using Bootstrap grid.
- Clear separation: auth pages vs. dashboard/assistant pages.

## Main Screens

### 1. Landing / Home (`index.html`)

- Short description of the tool.
- Buttons: "Login", "Register".

ASCII sketch:

[ Logo ] Learning Path Recommender
----------------------------------
[ Become fluent, one step at a time ]

[ Login ]   [ Register ]

---

### 2. Login / Register

Simple centered form card with Bootstrap:

+---------------------------------+
|  Login                          |
|  [ email input ]                |
|  [ password input ]             |
|  ( Login button )               |
|  ( link: Need an account? )     |
+---------------------------------+

---

### 3. Dashboard + Chatbot (`dashboard.html`)

Left side: chatbot bubbles.  
Right side: small summary card of current profile.

Layout sketch:

+-----------------------------------------------------------+
| Navbar: Brand | Dashboard | Logout                       |
+-----------------------------------------------------------+
|  [col-md-8] Chatbot                                       |
|  ----------------------------------------------           |
|  Bot: Hello, what is your learning goal?                  |
|  You: [ text input __________________ ] [Send]            |
|  Bot: Great, what's your current level?                   |
|  ...                                                      |
|                                                           |
|  [col-md-4] Profile Summary                               |
|  ----------------------------------------------           |
|  Goal: ...                                               |
|  Level: ...                                              |
|  Time: ...                                               |
|  [Generate Plan] button (if not already generated)        |
+-----------------------------------------------------------+

---

### 4. Learning Path View (`learning_path.html`)

Bootstrap cards in vertical list:

Step 1 – Python Basics (4 hours)
- Variables, data types, input/output
- Recommended: video + small exercises

Step 2 – Control Flow (4 hours)
...

Vision: user can clearly scroll and see a realistic sequence instead of a huge list.

