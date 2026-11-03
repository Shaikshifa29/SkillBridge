HOW TO RUN
1. Install Streamlit: pip install streamlit
2. Run the application on Windows: streamlit run app.py

WHAT EACH FILE DOES (2 lines each)
step0_inspect_dataset.py:
Inspects the raw CSV file to check total row counts, column headers, and sample job records.
Verifies the existence and structure of the skills and job description columns in the dataset.

module1_load_inspect.py:
Loads the dataset and filters for AI, Machine Learning, and Data Science job roles.
Parses, cleans, and extracts deduplicated skills per job posting to count overall occurrences.

module2_skill_demand.py:
Cleans skills with alias mapping and calculates percentage demand for All Roles and Fresher groups.
Sorts skills deterministically by demand and skill name, and generates comparison chart files.

module3_gap_analysis.py:
Normalizes user-entered skills and compares them against top 15 in-demand skills for the chosen group.
Calculates coverage score, identifies missing skills with demand %, and flags skills not in the dataset.

module4_roadmap.py:
Expands missing skills with prerequisite dependencies using topological sorting (Kahn's algorithm).
Builds a numbered learning path with curated free resources and separates an optional skills group.

app.py:
Implements the single-page Streamlit web user interface with sidebar inputs and an Analyze button.
Displays the coverage score, skill breakdown tables, learning roadmap, top 15 bar chart, and footer.

BACKEND / FRONTEND SPLIT (3 lines)
1. The backend consists of module1 through module4, containing pure data processing, filtering, and roadmap algorithms that return data structures without any Streamlit dependencies.
2. The frontend is contained entirely in app.py, which takes user input from the sidebar, calls backend functions, and renders tables, charts, and metrics.
3. This strict separation keeps data logic independent, testable, and reusable while keeping presentation logic centralized in a single UI script.
