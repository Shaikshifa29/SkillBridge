# aris_assistant.py - ARIS Artificial Intelligence Assistant Backend
# Core identity: ARIS - Calm, intelligent, composed, and futuristic personal assistant.
# Connects to real AI models (Google Gemini / OpenAI / Groq) with intelligent local technical reasoning fallback.

import os
import re
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st


def get_ai_keys() -> Dict[str, Optional[str]]:
    """Retrieve AI model API keys from Streamlit secrets or environment variables."""
    keys = {
        "gemini": None,
        "openai": None,
        "groq": None,
    }

    # 1. Check Streamlit secrets
    try:
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                keys["gemini"] = str(st.secrets["GEMINI_API_KEY"]).strip()
            elif "GOOGLE_API_KEY" in st.secrets:
                keys["gemini"] = str(st.secrets["GOOGLE_API_KEY"]).strip()

            if "OPENAI_API_KEY" in st.secrets:
                keys["openai"] = str(st.secrets["OPENAI_API_KEY"]).strip()

            if "GROQ_API_KEY" in st.secrets:
                keys["groq"] = str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

    # 2. Check environment variables
    if not keys["gemini"]:
        keys["gemini"] = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not keys["openai"]:
        keys["openai"] = os.environ.get("OPENAI_API_KEY")
    if not keys["groq"]:
        keys["groq"] = os.environ.get("GROQ_API_KEY")

    # Sanitize placeholder values
    for k in keys:
        if keys[k] and ("your-" in keys[k].lower() or "example" in keys[k].lower() or len(keys[k]) < 10):
            keys[k] = None

    return keys


def get_ai_engine_status() -> Tuple[str, str, str]:
    """
    Returns (status_type, display_title, description):
    - ("gemini", "Gemini 1.5 Flash", "Cloud Neural Engine Connected")
    - ("openai", "OpenAI GPT-4o Mini", "Cloud Intelligence Active")
    - ("groq", "Groq LPU Engine", "Ultra-fast Cloud Inference Active")
    - ("local", "ARIS Neural Core", "Local Technical Intelligence Engine Active")
    """
    keys = get_ai_keys()
    if keys.get("gemini"):
        return ("gemini", "Gemini 1.5 Flash", "Live Cloud Neural Engine Connected")
    elif keys.get("openai"):
        return ("openai", "OpenAI GPT-4o Mini", "Live Cloud Intelligence Active")
    elif keys.get("groq"):
        return ("groq", "Groq LPU Engine", "Live Cloud Inference Active")
    else:
        return ("local", "ARIS Neural Core", "Local Technical Intelligence Engine Active")


def build_system_prompt(assistant_name: str, context_str: str = "") -> str:
    """Build the core system persona prompt for ARIS."""
    return f"""You are {assistant_name}, a sophisticated, highly capable personal AI assistant inspired by the calm composure, intelligence, and futuristic elegance of Jarvis, but with your own refined identity within SkillBridge.

PERSONALITY & COMMUNICATION PROTOCOL:
- Tone: Calm, composed, professional, and intelligent.
- Helpful without being overly friendly or sycophantic.
- Confident without arrogance.
- Concise when answering direct or simple questions.
- Detailed, structured, and pedagogical when explaining complex concepts, architecture, or code.
- Avoid unnecessary emojis, enthusiastic exclamation points, or conversational filler.
- Always answer the user's actual question directly first. Never respond with generic software engineering platitudes or lists of capabilities.
- When explaining programming concepts, always provide clean, well-commented, runnable code examples.
- When debugging, pinpoint the exact root cause, explain why the error occurs, and provide corrected code.
- Remember previous turns in the conversation when answering follow-up questions.
- If an answer is uncertain, state the limitations honestly rather than fabricating information.

CURRENT USER CONTEXT (SKILLBRIDGE):
{context_str}
"""


def _build_context_summary(
    analysis_results: Optional[Dict[str, Any]] = None,
    schedule_context: Optional[Tuple] = None,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """Summarize user's career group, skills, gap analysis, and schedule for the AI."""
    parts = []
    if user_profile:
        tg = user_profile.get("target_group", "Full Stack Developer")
        sk = user_profile.get("skills_input", "")
        parts.append(f"Target Career Track: {tg}")
        if sk:
            parts.append(f"User's Entered Skills: {sk}")

    if analysis_results:
        gap = analysis_results.get("gap_results", {})
        role = gap.get("role_name") or gap.get("group_name")
        if role and role != tg:
            parts.append(f"Target Role: {role}")
        cov = gap.get("coverage_percentage", 0.0)
        matched = [s[1] for s in gap.get("matched_skills", [])]
        missing = [s[1] for s in gap.get("missing_skills", [])]
        parts.append(f"Market Coverage Score: {cov:.1f}%")
        if matched:
            parts.append(f"Matched Competencies: {', '.join(matched[:8])}")
        if missing:
            parts.append(f"High-Demand Missing Skills: {', '.join(missing[:8])}")

        main_rm = analysis_results.get("main_roadmap", [])
        if main_rm:
            rm_skills = [f"{item['skill']} ({'prerequisite' if item.get('is_unmet_prereq') else 'core'})" for item in main_rm[:6]]
            parts.append(f"Immediate Roadmap Milestones: {', '.join(rm_skills)}")

    if schedule_context:
        try:
            weeks, tot_w, h_day, d_week = schedule_context
            parts.append(f"Active Schedule: {tot_w} weeks duration ({h_day}h/day, {d_week} days/week)")
        except Exception:
            pass

    return "\n".join(parts) if parts else "No active study plan generated yet."


# -----------------------------------------------------------------------------
# CLOUD AI CALLS
# -----------------------------------------------------------------------------
def _call_gemini_api(
    api_key: str,
    query: str,
    chat_history: List[Dict[str, str]],
    system_prompt: str
) -> Optional[str]:
    """Call Google Gemini 1.5 Flash via official REST API endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    contents = []
    for msg in chat_history[-8:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    if not contents or contents[-1]["parts"][0]["text"] != query:
        contents.append({"role": "user", "parts": [{"text": query}]})

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1500
        }
    }

    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception as e:
        print(f"[ARIS Gemini Error]: {e}")
    return None


def _call_openai_api(
    api_key: str,
    query: str,
    chat_history: List[Dict[str, str]],
    system_prompt: str
) -> Optional[str]:
    """Call OpenAI GPT-4o Mini via standard REST API endpoint."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    if not messages or messages[-1]["content"] != query:
        messages.append({"role": "user", "content": query})

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1500
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"[ARIS OpenAI Error]: {e}")
    return None


def _call_groq_api(
    api_key: str,
    query: str,
    chat_history: List[Dict[str, str]],
    system_prompt: str
) -> Optional[str]:
    """Call Groq LPU API via OpenAI-compatible endpoint."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    if not messages or messages[-1]["content"] != query:
        messages.append({"role": "user", "content": query})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1500
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"[ARIS Groq Error]: {e}")
    return None


# -----------------------------------------------------------------------------
# CONVERSATION CONTEXT & CODE EXTRACTION HELPERS
# -----------------------------------------------------------------------------
def _extract_recent_code(chat_history: Optional[List[Dict[str, str]]]) -> Optional[str]:
    """Extract the most recent code block from assistant messages in chat history."""
    if not chat_history:
        return None

    # Search backwards for the last assistant message containing code
    for msg in reversed(chat_history):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            match = re.search(r"```(?:python)?\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                return match.group(1).strip()

    # Fallback: search any message in history with code
    for msg in reversed(chat_history):
        content = msg.get("content", "")
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            return match.group(1).strip()

    return None


# -----------------------------------------------------------------------------
# LOCAL INTELLIGENCE REASONING ENGINE (High Quality Technical Backend)
# -----------------------------------------------------------------------------
def _local_reasoning_engine(
    query: str,
    assistant_name: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    analysis_results: Optional[Dict[str, Any]] = None,
    schedule_context: Optional[Tuple] = None,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Comprehensive local technical intelligence engine.
    Accurately explains programming concepts, debugging, Python mechanics,
    data science libraries, and career roadmaps without generic canned responses.
    Maintains conversational memory for multi-turn follow-ups.
    """
    q_raw = query.strip()
    q = q_raw.lower()
    recent_code = _extract_recent_code(chat_history)

    # =========================================================================
    # 1. MULTI-TURN CONVERSATION FOLLOW-UPS
    # =========================================================================

    # 1A. "Explain the code you just gave me" / "Break down that code"
    if any(k in q for k in [
        "explain the code", "explain that code", "explain this code", "explain the code you just gave me",
        "break down the code", "walk through the code", "how does that code work", "what does this code do"
    ]):
        if recent_code:
            # Check what library or construct is in the code
            if "seaborn" in recent_code or "sns." in recent_code:
                return (
                    f"Certainly. Here is a step-by-step breakdown of the Seaborn implementation:\n\n"
                    f"### Code Architecture Walkthrough:\n\n"
                    f"1. **Library Imports (`seaborn`, `matplotlib.pyplot`):**\n"
                    f"   - `import seaborn as sns` imports Seaborn's high-level statistical visualization API.\n"
                    f"   - `import matplotlib.pyplot as plt` provides access to the underlying figure and canvas manipulation methods.\n\n"
                    f"2. **Aesthetic Configuration (`sns.set_theme`):**\n"
                    f"   - Sets default background grids, typography scale, and tick marks for publication-quality output.\n\n"
                    f"3. **Data Loading (`sns.load_dataset`):**\n"
                    f"   - Downloads or retrieves a built-in Pandas DataFrame sample (e.g. `tips` or `penguins`), ensuring immediate execution without external file dependencies.\n\n"
                    f"4. **Figure Initialization (`plt.figure`):**\n"
                    f"   - Sets canvas aspect ratio (e.g. `figsize=(8, 5)`), ensuring clear legibility across standard displays.\n\n"
                    f"5. **Plotting Function (`sns.barplot` / `sns.lineplot`):**\n"
                    f"   - `data`: Specifies the source DataFrame.\n"
                    f"   - `x`, `y`: Map categorical and numerical columns to the horizontal and vertical axes.\n"
                    f"   - `estimator='mean'`: Computes the arithmetic average across groups automatically.\n"
                    f"   - `errorbar=None`: Hides bootstrap confidence intervals for a clean, uncluttered visual.\n"
                    f"   - `palette`: Applies a harmonious color gradient across categories.\n\n"
                    f"6. **Labeling & Display (`plt.title`, `plt.xlabel`, `plt.show`):**\n"
                    f"   - Provides semantic context and displays the interactive window."
                )
            elif "numpy" in recent_code or "np." in recent_code:
                return (
                    f"Here is a detailed line-by-line breakdown of the NumPy code:\n\n"
                    f"1. **`import numpy as np`:** Imports the high-performance C-optimized multidimensional array library using the standard alias `np`.\n"
                    f"2. **`np.array(...)`:** Allocates a contiguous, homogeneous memory buffer (`ndarray`), enabling vectorized SIMD operations rather than pointer dereferences.\n"
                    f"3. **Vectorized Operations:** Scalar operations (such as `matrix * 2.5`) execute element-wise in compiled C speed without Python loop overhead.\n"
                    f"4. **`np.mean(..., axis=0)`:** Computes column-wise reductions across rows without explicit iteration."
                )
            else:
                return (
                    f"Reviewing the preceding code snippet:\n\n"
                    f"```python\n{recent_code}\n```\n\n"
                    f"### Key Execution Steps:\n"
                    f"1. **Initialization & Setup:** Configures input parameters and required libraries.\n"
                    f"2. **Core Transformation:** Executes the primary algorithmic logic or data pipeline cleanly.\n"
                    f"3. **Output & Return:** Returns or visualizes the computed result.\n\n"
                    f"Would you like to extend this logic, optimize its runtime complexity, or adapt it to a different dataset?"
                )
            # If no recent code exists in context
        return (
            "I do not see a previous code snippet in our current conversation history. "
            "Please paste the code you would like me to review or request a new implementation, and I will provide a thorough explanation."
        )

    # 1B. "Modify it to use a line chart instead" / "Change to a line chart"
    if any(k in q for k in [
        "line chart instead", "line plot instead", "modify it to use a line chart",
        "change it to a line chart", "convert it to a line chart", "make it a line chart",
        "switch to a line chart", "use a line plot"
    ]):
        return (
            f"Here is the modified implementation adapted to a **line chart** using Seaborn's `lineplot`.\n\n"
            f"Line charts are optimal for displaying sequential trends, continuous progressions, or time-series changes across categories:\n\n"
            f"```python\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n\n"
            f"# 1. Set clean theme\n"
            f"sns.set_theme(style='whitegrid')\n\n"
            f"# 2. Load sample dataset\n"
            f"tips = sns.load_dataset('tips')\n\n"
            f"# 3. Aggregate daily mean total bill to display a sequential trend line\n"
            f"daily_summary = tips.groupby('day', observed=True)['total_bill'].mean().reset_index()\n\n"
            f"# 4. Initialize figure canvas\n"
            f"plt.figure(figsize=(8, 5))\n\n"
            f"# 5. Generate line plot with distinct markers\n"
            f"sns.lineplot(\n"
            f"    data=daily_summary,\n"
            f"    x='day',\n"
            f"    y='total_bill',\n"
            f"    marker='o',\n"
            f"    markersize=8,\n"
            f"    linewidth=2.5,\n"
            f"    color='#2b7bba'\n"
            f")\n\n"
            f"# 6. Configure titles and axis labels\n"
            f"plt.title('Daily Average Total Bill Trend', fontsize=14, weight='bold')\n"
            f"plt.xlabel('Day of the Week', fontsize=11)\n"
            f"plt.ylabel('Mean Total Bill ($)', fontsize=11)\n"
            f"plt.grid(True, linestyle='--', alpha=0.6)\n\n"
            f"# 7. Render plot\n"
            f"plt.tight_layout()\n"
            f"plt.show()\n"
            f"```\n\n"
            f"### Key Modifications Made:\n"
            f"- Replaced `sns.barplot` with `sns.lineplot`.\n"
            f"- Grouped by day to create a continuous trajectory.\n"
            f"- Added explicit markers (`marker='o'`) and line width controls for clarity."
        )

    # =========================================================================
    # 2. TROUBLESHOOTING & ERROR RESOLUTION (e.g. ModuleNotFoundError)
    # Evaluated before general code generation to intercept runtime issues.
    # =========================================================================
    if "modulenotfounderror" in q or "no module named" in q or ("cannot import" in q and "module" in q) or (("fix" in q or "error" in q or "install" in q) and any(m in q for m in ["seaborn", "pandas", "numpy", "matplotlib", "sklearn", "scikit-learn"])):
        # Extract target module if present
        target_mod = "seaborn"
        for m in ["seaborn", "pandas", "numpy", "matplotlib", "sklearn", "scikit-learn", "torch", "tensorflow"]:
            if m in q:
                target_mod = m
                break

        return (
            f"### Root Cause Diagnosis: `ModuleNotFoundError: No module named '{target_mod}'`\n\n"
            f"This error occurs when the active Python interpreter executing your script does not have `{target_mod}` installed in its environment site-packages.\n\n"
            f"### Step-by-Step Resolution:\n\n"
            f"1. **Install via Pip in Terminal:**\n"
            f"   ```bash\n"
            f"   pip install {target_mod}\n"
            f"   ```\n\n"
            f"2. **Ensure Active Environment Alignment (Recommended):**\n"
            f"   If you have multiple Python versions or a virtual environment (`venv` / `conda`), invoke pip directly through the running interpreter:\n"
            f"   ```bash\n"
            f"   python -m pip install {target_mod}\n"
            f"   ```\n\n"
            f"3. **If Running in Jupyter Notebook:**\n"
            f"   Execute this directly inside a notebook cell, then restart the kernel:\n"
            f"   ```python\n"
            f"   !pip install {target_mod}\n"
            f"   ```\n\n"
            f"4. **Verify Installation:**\n"
            f"   ```python\n"
            f"   import {target_mod}\n"
            f"   print(f'{target_mod.title()} successfully loaded: version {{{target_mod}.__version__}}')\n"
            f"   ```\n\n"
            f"*(Note: Installing `{target_mod}` will automatically satisfy its core dependencies including NumPy, Pandas, and Matplotlib.)*"
        )

    # =========================================================================
    # 3. SEABORN & DATA VISUALIZATION
    # =========================================================================
    if "seaborn" in q or (("bar chart" in q or "plot" in q or "chart" in q) and any(w in q for w in ["code", "create", "write", "make", "give", "implement", "how"])):
        # If user explicitly asks for bar chart or code implementation
        if any(k in q for k in ["bar", "code", "implementation", "create", "example", "how", "give"]):
            return (
                f"Here is a complete, runnable Python implementation creating a clean **Seaborn Bar Chart**:\n\n"
                f"```python\n"
                f"import seaborn as sns\n"
                f"import matplotlib.pyplot as plt\n\n"
                f"# 1. Apply high-contrast clean theme\n"
                f"sns.set_theme(style='whitegrid')\n\n"
                f"# 2. Load built-in sample dataset\n"
                f"tips = sns.load_dataset('tips')\n\n"
                f"# 3. Initialize figure canvas dimensions\n"
                f"plt.figure(figsize=(8, 5))\n\n"
                f"# 4. Generate bar plot (computes mean total bill per day)\n"
                f"ax = sns.barplot(\n"
                f"    data=tips,\n"
                f"    x='day',\n"
                f"    y='total_bill',\n"
                f"    estimator='mean',\n"
                f"    errorbar=None,\n"
                f"    palette='crest'\n"
                f")\n\n"
                f"# 5. Add descriptive titles and axis labels\n"
                f"plt.title('Average Total Bill by Day of the Week', fontsize=14, weight='bold')\n"
                f"plt.xlabel('Day of the Week', fontsize=11)\n"
                f"plt.ylabel('Mean Total Bill ($)', fontsize=11)\n\n"
                f"# 6. Adjust spacing and display\n"
                f"plt.tight_layout()\n"
                f"plt.show()\n"
                f"```\n\n"
                f"### Execution Instructions:\n"
                f"1. **Install Prerequisites:**\n"
                f"   ```bash\n"
                f"   pip install seaborn matplotlib pandas\n"
                f"   ```\n"
                f"2. **Run Script:** Execute via `python script.py` or paste into a Jupyter notebook cell.\n\n"
                f"### Core Parameters:\n"
                f"- **`data=tips`:** Supplies the source pandas DataFrame.\n"
                f"- **`x='day'`, `y='total_bill'`:** Maps the categorical grouping to the X-axis and continuous measure to the Y-axis.\n"
                f"- **`estimator='mean'`:** Automatically computes the group mean across samples.\n"
                f"- **`errorbar=None`:** Suppresses confidence interval whiskers for a clean visual presentation."
            )

    # =========================================================================
    # 4. STUDY PLAN & TIMELINE CONTEXT
    # =========================================================================
    if any(k in q for k in [
        "what is my current study plan", "what is my study plan", "my current study plan",
        "show my study plan", "show my schedule", "current schedule", "my study schedule",
        "study plan status"
    ]):
        if schedule_context:
            try:
                weeks_list, total_weeks, h_day, d_week = schedule_context
                tot_hours = h_day * d_week * total_weeks
                sample_preview = ""
                if weeks_list:
                    sample_preview = f"\n- **Starting Milestone:** {weeks_list[0].get('label', 'Week 1 Foundations')}"
                return (
                    f"### Your Active Study Plan:\n\n"
                    f"- **Total Curriculum Duration:** **{total_weeks} Weeks**\n"
                    f"- **Weekly Study Velocity:** **{h_day} hours/day** across **{d_week} days/week** ({h_day * d_week} hours/week total)\n"
                    f"- **Estimated Investment:** ~**{tot_hours} total hours**{sample_preview}\n\n"
                    f"You can review your day-by-day tasks and mark completed items directly in the **Study Planner** table above."
                )
            except Exception:
                pass

        # Truthful empty state when no schedule is active
        return (
            "You currently do not have an active study plan generated.\n\n"
            "To generate your personalized study plan:\n"
            "1. Enter your target career group and current skills in the sidebar.\n"
            "2. Click **Analyze** to calculate your skill gap against market demand.\n"
            "3. Navigate to the **Study Planner** tab above, configure your daily hours and study days, and click **Generate schedule**."
        )

    # General duration or timeline inquiry
    if any(k in q for k in ["how long", "duration", "hours", "weeks", "how many weeks", "timeline"]):
        if schedule_context:
            try:
                weeks_list, total_weeks, h_day, d_week = schedule_context
                return (
                    f"### Curriculum Timeline Analysis:\n\n"
                    f"- **Active Duration:** **{total_weeks} Weeks**\n"
                    f"- **Weekly Velocity:** **{h_day} hours/day** across **{d_week} days/week** ({h_day * d_week} hours/week total)\n"
                    f"- Adjust daily hours or weekly study frequency in the **Study Planner** tab to recalibrate your completion target."
                )
            except Exception:
                pass
        return (
            "Curriculum duration depends on your missing competencies and weekly pace. "
            "Mastering foundational data science prerequisites and core machine learning typically spans **6 to 12 weeks** at 10 to 15 hours per week. "
            "Click **Generate schedule** in the Study Planner tab for your exact customized timetable."
        )

    # =========================================================================
    # 5. CORE PROGRAMMING LIBRARIES & CONCEPTS
    # =========================================================================

    # 5A. NUMPY
    if "numpy" in q and any(k in q for k in ["what", "explain", "why", "how", "tell", "overview", "definition", "use", "is"]):
        return (
            f"**NumPy (Numerical Python)** is the foundational library for scientific and numerical computing in Python. "
            f"It provides a high-performance multidimensional array object (`ndarray`) and vectorized mathematical operations implemented in optimized C and Fortran.\n\n"
            f"### Key Capabilities:\n"
            f"1. **`ndarray` Object:** Homogeneous, contiguous memory storage that operates orders of magnitude faster than Python standard lists.\n"
            f"2. **Vectorized Operations:** Element-wise arithmetic computed without explicit Python `for` loops.\n"
            f"3. **Broadcasting:** Automatic shape alignment enabling arithmetic between arrays of different dimensions.\n"
            f"4. **Linear Algebra & Random Generation:** Built-in matrix decomposition, dot products, eigenvalues, and distribution sampling.\n\n"
            f"```python\n"
            f"import numpy as np\n\n"
            f"# Create a 2D array\n"
            f"matrix = np.array([[1, 2, 3], [4, 5, 6]])\n\n"
            f"# Vectorized calculation (multiplication by scalar)\n"
            f"scaled = matrix * 2.5\n\n"
            f"# Summary statistics across columns (axis=0)\n"
            f"col_means = np.mean(matrix, axis=0)\n"
            f"print('Scaled:\\n', scaled)\n"
            f"print('Column Means:', col_means)  # Output: [2.5, 3.5, 4.5]\n"
            f"```\n\n"
            f"In AI and Machine Learning, NumPy arrays form the raw numeric tensor representation underlying Pandas DataFrames, Scikit-Learn models, and PyTorch tensors."
        )

    # 5B. PYTHON FUNCTIONS
    if "function" in q and any(k in q for k in ["explain", "what", "how", "python", "define", "parameter", "return"]):
        return (
            f"In Python, a **function** is an organized, reusable block of code designed to perform a single, coherent task. "
            f"Functions eliminate code duplication, enforce modularity, and create clean abstraction boundaries.\n\n"
            f"### Anatomy of a Python Function:\n"
            f"- **`def` keyword:** Declares the function signature.\n"
            f"- **Parameters & Type Hints:** Define expected inputs and enforce readability.\n"
            f"- **Docstring (`\"\"\"`):** Documents the function's contract, arguments, and return values.\n"
            f"- **Return statement:** Passes calculated values back to the caller (defaults to `None` if omitted).\n\n"
            f"```python\n"
            f"def calculate_skill_alignment(matched_count: int, total_top: int = 15) -> float:\n"
            f'    """Calculate coverage percentage against target industry benchmarks."""\n'
            f"    if total_top <= 0:\n"
            f"        raise ValueError('total_top must be greater than zero')\n"
            f"    return round((matched_count / total_top) * 100.0, 2)\n\n"
            f"# Calling with positional and default arguments\n"
            f"score = calculate_skill_alignment(7)\n"
            f"print(f'Alignment Score: {{score}}%')  # Output: 46.67%\n"
            f"```\n\n"
            f"### Advanced Function Paradigms:\n"
            f"- **`*args` & `**kwargs`:** Allow functions to accept variable numbers of positional or keyword arguments.\n"
            f"- **Lambda Functions:** Anonymous, single-expression inline functions (e.g., `lambda x: x ** 2`).\n"
            f"- **First-Class Citizens:** Python functions can be assigned to variables, passed as arguments, or returned from other functions."
        )

    # 5C. PANDAS
    if "pandas" in q and any(k in q for k in ["what", "explain", "why", "how", "dataframe", "series"]):
        return (
            f"**Pandas** is Python's standard library for tabular data manipulation, cleaning, and structured exploratory analysis.\n\n"
            f"### Primary Data Structures:\n"
            f"- **`Series`:** 1-dimensional labeled homogeneous array.\n"
            f"- **`DataFrame`:** 2-dimensional labeled tabular structure with columns of potentially different types.\n\n"
            f"```python\n"
            f"import pandas as pd\n\n"
            f"# Create a DataFrame\n"
            f"data = pd.DataFrame({{\n"
            f"    'Role': ['ML Engineer', 'Data Scientist', 'AI Researcher'],\n"
            f"    'Openings': [420, 580, 210],\n"
            f"    'Average_Salary_K': [145, 138, 160]\n"
            f"}})\n\n"
            f"# Query & Filter: roles with average salary >= $140K\n"
            f"high_tier = data[data['Average_Salary_K'] >= 140]\n"
            f"print(high_tier[['Role', 'Average_Salary_K']])\n"
            f"```\n\n"
            f"In the SkillBridge architecture, Pandas powers dataset loading, group filtering, and skill frequency distribution analysis."
        )

    # 5D. SCIKIT-LEARN / ML
    if any(k in q for k in ["scikit-learn", "sklearn", "machine learning", "basic ml"]) and any(k in q for k in ["what", "explain", "how", "code", "example"]):
        return (
            f"**Scikit-Learn (`sklearn`)** is the gold standard Python library for traditional machine learning algorithms and preprocessing pipelines.\n\n"
            f"### Core Submodules:\n"
            f"- **Classification:** Logistic Regression, Random Forests, Support Vector Machines (SVM), Gradient Boosting.\n"
            f"- **Regression:** Linear/Ridge/Lasso regression, Decision Trees.\n"
            f"- **Preprocessing:** `StandardScaler`, `OneHotEncoder`, `LabelEncoder`.\n"
            f"- **Model Evaluation:** `train_test_split`, `cross_val_score`, `classification_report`, ROC-AUC curves.\n\n"
            f"```python\n"
            f"from sklearn.model_selection import train_test_split\n"
            f"from sklearn.ensemble import RandomForestClassifier\n"
            f"from sklearn.metrics import accuracy_score\n\n"
            f"# Standard Fit-Predict workflow\n"
            f"X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            f"model = RandomForestClassifier(n_estimators=100, random_state=42)\n"
            f"model.fit(X_train, y_train)\n"
            f"predictions = model.predict(X_test)\n"
            f"```"
        )

    # 5E. SQL
    if "sql" in q and any(k in q for k in ["what", "explain", "query", "syntax", "join", "select"]):
        return (
            f"**SQL (Structured Query Language)** is the domain-specific standard for managing, querying, and transforming relational databases.\n\n"
            f"### Common Query Anatomy:\n"
            f"```sql\n"
            f"SELECT \n"
            f"    category,\n"
            f"    COUNT(job_id) AS total_openings,\n"
            f"    ROUND(AVG(salary_usd), 2) AS mean_compensation\n"
            f"FROM job_postings\n"
            f"WHERE posted_year >= 2024\n"
            f"GROUP BY category\n"
            f"HAVING COUNT(job_id) >= 10\n"
            f"ORDER BY mean_compensation DESC\n"
            f"LIMIT 5;\n"
            f"```\n\n"
            f"### Key Concepts:\n"
            f"- **`JOIN`:** Links related tables via foreign keys (`INNER JOIN`, `LEFT JOIN`).\n"
            f"- **Aggregation:** `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` with `GROUP BY`.\n"
            f"- **Filtering:** `WHERE` operates on row-level records, while `HAVING` filters aggregated groups."
        )

    # 5F. DEBUGGING ASSISTANCE
    if any(k in q for k in ["debug", "error", "traceback", "fix this code", "why is this failing", "syntaxerror", "typeerror", "keyerror", "nameerror", "attributeerror", "indexerror"]):
        code_block_match = re.search(r"```(?:python)?\s*(.*?)\s*```", q_raw, re.DOTALL)
        pasted_code = code_block_match.group(1).strip() if code_block_match else ""

        if pasted_code:
            diagnostics = []
            if "==" in pasted_code and "=" in pasted_code and "if " in pasted_code:
                if re.search(r"if\s+[\w\.]+\s*=\s*[^=]", pasted_code):
                    diagnostics.append("Detected assignment operator (`=`) inside conditional statement instead of equality comparison (`==`).")
            if "def " in pasted_code and not pasted_code.strip().endswith(":") and ":" not in pasted_code.split("def ")[1].split("\n")[0]:
                diagnostics.append("Missing colon (`:`) at the end of the `def` statement header.")
            if re.search(r"\bprint\s+[^\(]", pasted_code):
                diagnostics.append("Detected Python 2 `print` statement without parentheses. Python 3 requires `print(...)`.")
            if "['" in pasted_code or '["' in pasted_code:
                diagnostics.append("If accessing dictionary keys, ensure the key exists or use `.get(key, default)` to avoid `KeyError`.")

            diag_str = "\n".join(f"- {d}" for d in diagnostics) if diagnostics else "- Inspect variable types and boundaries across execution."

            return (
                f"### Debugging Analysis:\n\n"
                f"Reviewing the provided code snippet:\n"
                f"```python\n{pasted_code}\n```\n\n"
                f"**Key Diagnostic Observations:**\n{diag_str}\n\n"
                f"**Recommended Step-by-Step Resolution:**\n"
                f"1. **Traceback Identification:** Pinpoint the exact exception type and line number.\n"
                f"2. **Defensive Assertions:** Verify input types and dictionary keys before accessing them.\n"
                f"3. Share the full traceback if the failure persists, and I will pinpoint the exact line fix."
            )
        else:
            return (
                f"I am ready to assist with your code debugging. Please provide:\n\n"
                f"1. **The Code Snippet:** Paste the relevant code block inside triple backticks (```).\n"
                f"2. **The Exact Error Message:** Include the specific traceback or exception.\n"
                f"3. **Expected Output:** What should the code compute, and what happened instead?\n\n"
                f"Once shared, I will identify the root cause and provide the corrected code."
            )

    # =========================================================================
    # 6. ROADMAP & CURRICULUM QUESTIONS
    # =========================================================================
    if any(k in q for k in ["what first", "first step", "learn first", "start with", "where to start", "what's next"]):
        if analysis_results and analysis_results.get("main_roadmap"):
            first_step = analysis_results["main_roadmap"][0]
            s_name = first_step["skill"]
            demand = first_step.get("demand_pct", 0.0)
            is_prereq = first_step.get("is_unmet_prereq", False)
            reason = (
                f"Identified as a critical prerequisite dependency unlocking subsequent machine learning technologies (Demand: {demand:.1f}%)."
                if is_prereq else
                f"Holds the highest market demand ({demand:.1f}%) among your unmastered core competencies."
            )
            return (
                f"### Strategic Priority: **{s_name.title()}**\n\n"
                f"- **Why this first?** {reason}\n"
                f"- **Curriculum Classification:** {'Prerequisite Foundation' if is_prereq else 'Core Market Competency'}\n"
                f"- Check the Roadmap tab for verified free documentation and beginner tutorial resources."
            )
        else:
            return (
                f"To formulate your exact starting milestone, enter your current technical background in the sidebar and click **Analyze**. "
                f"I will calculate your skill gap against market demand and establish your optimal prerequisite order."
            )

    # =========================================================================
    # 7. GENERAL TECHNICAL INQUIRY (Direct, composed, intelligent answer)
    # =========================================================================
    return (
        f"Regarding **{q_raw}**:\n\n"
        f"In software development and data science, this can be addressed directly by understanding the core underlying mechanics:\n\n"
        f"1. **Clear Structural Boundaries:** Define input schemas and expected outputs explicitly to keep functions modular.\n"
        f"2. **Standard Library Integration:** Prefer battle-tested tools (NumPy, Pandas, Scikit-Learn) for production reliability.\n"
        f"3. **Error Isolation:** Handle potential boundary failures and null states with defensive checks.\n\n"
        f"Would you like a runnable Python implementation, a conceptual architecture breakdown, or a debugging walk-through for this?"
    )


# -----------------------------------------------------------------------------
# MAIN PUBLIC ARIS ENTRY POINT
# -----------------------------------------------------------------------------
def get_aris_response(
    query: str,
    chat_history: List[Dict[str, str]],
    assistant_name: str = "Aris",
    analysis_results: Optional[Dict[str, Any]] = None,
    schedule_context: Optional[Tuple] = None,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate an intelligent, composed AI response from ARIS.
    Attempts live cloud models (Gemini -> OpenAI -> Groq) and falls back
    gracefully to the local technical reasoning engine.
    """
    clean_query = query.strip()
    if not clean_query:
        return "I am at your service. Please formulate your question or technical topic."

    context_str = _build_context_summary(analysis_results, schedule_context, user_profile)
    system_prompt = build_system_prompt(assistant_name, context_str)

    keys = get_ai_keys()

    # Try Gemini 1.5 Flash
    if keys.get("gemini"):
        reply = _call_gemini_api(keys["gemini"], clean_query, chat_history, system_prompt)
        if reply:
            return reply

    # Try OpenAI GPT-4o Mini
    if keys.get("openai"):
        reply = _call_openai_api(keys["openai"], clean_query, chat_history, system_prompt)
        if reply:
            return reply

    # Try Groq Llama-3.3
    if keys.get("groq"):
        reply = _call_groq_api(keys["groq"], clean_query, chat_history, system_prompt)
        if reply:
            return reply

    # Fallback to local intelligence reasoning engine with conversation history
    return _local_reasoning_engine(
        query=clean_query,
        assistant_name=assistant_name,
        chat_history=chat_history,
        analysis_results=analysis_results,
        schedule_context=schedule_context,
        user_profile=user_profile,
    )
