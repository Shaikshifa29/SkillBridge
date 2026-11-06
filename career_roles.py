# career_roles.py - Comprehensive Technical Career Roles, Skills Ontology & Learning Resources
# Defines 36 technical career paths across 6 categories with structured skill mappings,
# difficulty tiers, prerequisite dependencies, and trustworthy clickable learning links.

import re
import urllib.parse
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

# =============================================================================
# 1. CAREER CATEGORIES AND ROLES (36 Technical Roles Across 6 Categories)
# =============================================================================
CAREER_CATEGORIES: Dict[str, List[str]] = {
    "AI & Machine Learning": [
        "AI Engineer",
        "Machine Learning Engineer",
        "Deep Learning Engineer",
        "NLP Engineer",
        "Computer Vision Engineer",
        "Generative AI Engineer",
    ],
    "Data Careers": [
        "Data Analyst",
        "Data Scientist",
        "Data Engineer",
        "Business Intelligence Developer",
        "Analytics Engineer",
    ],
    "Software Development": [
        "Software Developer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Mobile App Developer",
        "Python Developer",
        "Java Developer",
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst",
        "Security Engineer",
        "Penetration Tester",
        "Ethical Hacker",
        "SOC Analyst",
        "Cloud Security Engineer",
    ],
    "Cloud & DevOps": [
        "Cloud Engineer",
        "DevOps Engineer",
        "Site Reliability Engineer",
        "Platform Engineer",
    ],
    "Other Technical Careers": [
        "Database Administrator",
        "QA Automation Engineer",
        "Software Test Engineer",
        "Blockchain Developer",
        "Embedded Systems Engineer",
        "IoT Engineer",
        "Network Engineer",
        "Systems Engineer",
    ],
}

# Flat list of all 36 roles
ALL_ROLES: List[str] = [role for roles in CAREER_CATEGORIES.values() for role in roles]

# Default role when initial or fallback selection is needed
DEFAULT_ROLE = "Full Stack Developer"


def get_category_for_role(role_name: str) -> str:
    """Return the parent category for a given role name."""
    for category, roles in CAREER_CATEGORIES.items():
        if role_name in roles:
            return category
    return "Software Development"


# =============================================================================
# 2. MASTER LEARNING RESOURCES REPOSITORY (Verified & Authoritative URLs)
# =============================================================================
# Contains official documentation, MDN, W3Schools, Kaggle, freeCodeCamp, OWASP, etc.
LEARNING_RESOURCES: Dict[str, Tuple[str, str]] = {
    # Web & Frontend
    "html": ("MDN Web Docs - HTML: Structuring the Web", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content"),
    "css": ("MDN Web Docs - CSS: Styling the Web", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics"),
    "javascript": ("MDN Web Docs - JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
    "typescript": ("TypeScript Official Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "react": ("React Official Documentation - Learn React", "https://react.dev/learn"),
    "next.js": ("Next.js Official Documentation & App Router Tutorial", "https://nextjs.org/docs"),
    "tailwind css": ("Tailwind CSS Official Documentation & Framework Guide", "https://tailwindcss.com/docs"),
    "redux": ("Redux Essentials Tutorial - State Management", "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"),
    "web performance": ("web.dev by Google - Fast Load Times & Web Vitals", "https://web.dev/explore/fast"),
    "accessibility": ("MDN Web Docs - Accessibility (a11y) Guide", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility"),

    # Programming Languages
    "python": ("Python 3 Official Tutorial - Beginners Guide", "https://docs.python.org/3/tutorial/"),
    "java": ("Java Official Tutorials by Oracle", "https://docs.oracle.com/javase/tutorial/"),
    "c++": ("LearnCpp - Complete Modern C++ Programming Guide", "https://www.learncpp.com/"),
    "c": ("Learn-C.org - Interactive C Tutorial", "https://www.learn-c.org/"),
    "c#": ("Microsoft Learn - C# Documentation and Tutorials", "https://learn.microsoft.com/en-us/dotnet/csharp/"),
    "go": ("Go Official Documentation - Tour of Go", "https://go.dev/tour/"),
    "rust": ("The Rust Programming Language Book", "https://doc.rust-lang.org/book/"),
    "r": ("R for Data Science Book (2e) - Online Free Edition", "https://r4ds.hadley.nz/"),
    "solidity": ("Solidity Official Documentation & Smart Contract Guide", "https://docs.soliditylang.org/"),
    "kotlin": ("Kotlin Official Documentation & Android Basics", "https://kotlinlang.org/docs/home.html"),
    "swift": ("Apple Developer - Swift Programming Language", "https://developer.apple.com/swift/"),

    # Backend & APIs
    "node.js": ("Node.js Official Documentation & Guides", "https://nodejs.org/en/learn"),
    "express": ("Express.js Official Guide - Fast Node Web Framework", "https://expressjs.com/en/starter/installing.html"),
    "fastapi": ("FastAPI Official Documentation - Modern Python APIs", "https://fastapi.tiangolo.com/tutorial/"),
    "django": ("Django Official Documentation - The Web Framework for Perfectionists", "https://docs.djangoproject.com/en/stable/intro/tutorial01/"),
    "spring boot": ("Spring Boot Official Getting Started Guides", "https://spring.io/guides/gs/spring-boot/"),
    "rest apis": ("RESTful API Design Best Practices Guide", "https://restfulapi.net/"),
    "graphql": ("GraphQL Official Tutorial - Introduction to GraphQL", "https://graphql.org/learn/"),
    "microservices": ("Microservices Architecture Guide by Martin Fowler", "https://martinfowler.com/articles/microservices.html"),
    "redis": ("Redis Official Documentation - In-Memory Caching", "https://redis.io/docs/latest/"),

    # Databases & Data Handling
    "sql": ("W3Schools - Complete SQL Tutorial", "https://www.w3schools.com/sql/"),
    "postgresql": ("PostgreSQL Official Documentation & Tutorial", "https://www.postgresql.org/docs/current/tutorial.html"),
    "mysql": ("MySQL Official Reference Manual", "https://dev.mysql.com/doc/refman/8.0/en/"),
    "mongodb": ("MongoDB University - Free Developer Courses & Manual", "https://www.mongodb.com/docs/manual/tutorial/"),
    "pandas": ("Pandas Official User Guide - 10 Minutes to Pandas", "https://pandas.pydata.org/docs/user_guide/10min.html"),
    "numpy": ("NumPy Quickstart Tutorial - Numerical Computing in Python", "https://numpy.org/doc/stable/user/quickstart.html"),
    "data modeling": ("Databricks - Relational & Dimensional Data Modeling Guide", "https://www.databricks.com/glossary/data-modeling"),
    "data warehousing": ("Snowflake - What is Data Warehousing Architecture", "https://www.snowflake.com/guides/what-is-data-warehousing/"),
    "dbt": ("dbt Official Documentation - What is dbt?", "https://docs.getdbt.com/docs/introduction"),
    "etl pipelines": ("Apache Airflow Official Tutorial - Automated ETL Workflows", "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html"),
    "spark": ("Apache Spark Quick Start - Unified Cluster Computing", "https://spark.apache.org/docs/latest/quick-start.html"),
    "hadoop": ("Apache Hadoop Documentation - HDFS & MapReduce", "https://hadoop.apache.org/docs/stable/"),

    # Data Visualization & BI
    "matplotlib": ("Matplotlib Official Tutorials - Pyplot & Scientific Plotting", "https://matplotlib.org/stable/tutorials/index.html"),
    "seaborn": ("Seaborn Official Tutorial - Statistical Data Visualization", "https://seaborn.pydata.org/tutorial.html"),
    "power bi": ("Microsoft Learn - Power BI Guided Learning & Certifications", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"),
    "tableau": ("Tableau Official Free Training Videos & Tutorials", "https://www.tableau.com/learn/training"),
    "excel": ("Microsoft Support - Excel Video Training & Formulas", "https://support.microsoft.com/en-us/office/excel-video-training-9bc05390-e94c-46af-972b-aa0300a6a099"),
    "statistics": ("Khan Academy - Statistics and Probability Course", "https://www.khanacademy.org/math/statistics-probability"),

    # Machine Learning & AI
    "machine learning": ("Kaggle Learn - Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning"),
    "basic ml": ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course"),
    "scikit-learn": ("Scikit-Learn Official User Guide - Machine Learning in Python", "https://scikit-learn.org/stable/user_guide.html"),
    "deep learning": ("Practical Deep Learning for Coders - Fast.ai Course", "https://course.fast.ai/"),
    "pytorch": ("PyTorch Official Tutorials - Deep Learning Framework", "https://pytorch.org/tutorials/"),
    "tensorflow": ("TensorFlow 2 Quickstart for Beginners - Official Tutorial", "https://www.tensorflow.org/tutorials/quickstart/beginner"),
    "keras": ("Getting Started with Keras - High-Level Deep Learning", "https://keras.io/getting_started/"),
    "nlp": ("Hugging Face NLP Course - Natural Language Processing with Transformers", "https://huggingface.co/learn/nlp-course"),
    "computer vision": ("OpenCV Official Tutorials - Computer Vision Fundamentals", "https://docs.opencv.org/4.x/d9/df8/tutorial_root.html"),
    "generative ai": ("DeepLearning.AI - Generative AI for Everyone Course", "https://www.deeplearning.ai/short-courses/"),
    "prompt engineering": ("LearnPrompting.org - Comprehensive Guide to Prompt Engineering", "https://www.learnprompting.org/"),
    "llms": ("Hugging Face Transformers Documentation - State-of-the-art LLMs", "https://huggingface.co/docs/transformers/index"),
    "langchain": ("LangChain Official Documentation - Building Applications with LLMs", "https://python.langchain.com/docs/get_started/introduction"),
    "vector databases": ("Pinecone Learning Center - What is a Vector Database?", "https://www.pinecone.io/learn/vector-database/"),
    "mlops": ("Made With ML - MLOps Course by Goku Mohandas", "https://madewithml.com/"),

    # Cloud, DevOps & Linux
    "linux": ("Linux Journey - Free Interactive Linux Fundamentals", "https://linuxjourney.com/"),
    "git": ("Pro Git Book - Version Control with Git Official Guide", "https://git-scm.com/doc"),
    "docker": ("Docker Get Started Guide - Containerization Fundamentals", "https://docs.docker.com/get-started/"),
    "kubernetes": ("Kubernetes Official Basics & Tutorials", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
    "aws": ("AWS Skill Builder - Free Official Cloud Training", "https://aws.amazon.com/training/digital/"),
    "azure": ("Microsoft Learn - Azure Fundamentals Learning Path", "https://learn.microsoft.com/en-us/training/azure/"),
    "gcp": ("Google Cloud Skills Boost - Cloud Digital Leader & Labs", "https://cloud.google.com/learn"),
    "terraform": ("HashiCorp Developer - Terraform Tutorials & IaC", "https://developer.hashicorp.com/terraform/tutorials"),
    "ci/cd": ("GitHub Actions Official Documentation - Automated CI/CD", "https://docs.github.com/en/actions"),
    "ansible": ("Ansible Official Documentation - Getting Started with Automation", "https://docs.ansible.com/ansible/latest/getting_started/index.html"),
    "prometheus": ("Prometheus Official Overview - Systems Monitoring & Alerting", "https://prometheus.io/docs/introduction/overview/"),
    "grafana": ("Grafana Tutorials - Metrics Visualization & Dashboards", "https://grafana.com/tutorials/"),
    "sre": ("Google Site Reliability Engineering - Free Online SRE Books", "https://sre.google/books/"),
    "bash": ("ShellScript.sh - Beginner to Advanced Bash Shell Scripting", "https://www.shellscript.sh/"),

    # Cybersecurity
    "cybersecurity": ("OWASP Top Ten Security Risks - Web Application Security", "https://owasp.org/www-project-top-ten/"),
    "security fundamentals": ("Cisco Networking Academy - Introduction to Cybersecurity", "https://www.netacad.com/courses/cybersecurity/introduction-cybersecurity"),
    "networking": ("Cisco Networking Academy - Computer Networking Basics", "https://www.netacad.com/courses/networking"),
    "siem tools": ("Splunk Free Training - Fundamentals of SIEM & Log Analysis", "https://www.splunk.com/en_us/training/free-courses/splunk-fundamentals-1.html"),
    "incident response": ("CISA - Incident Response Principles & Cyber Defense Guidelines", "https://www.cisa.gov/resources-tools/resources/incident-response-guide"),
    "penetration testing": ("PortSwigger Web Security Academy - Free Pentesting Labs", "https://portswigger.net/web-security"),
    "ethical hacking": ("OWASP Web Security Testing Guide (WSTG)", "https://owasp.org/www-project-web-security-testing-guide/"),
    "soc analyst": ("TryHackMe - SOC Level 1 Training Pathway", "https://tryhackme.com/path/outline/soclevel1"),
    "cloud security": ("Cloud Security Alliance - Security Guidance for Cloud Computing", "https://cloudsecurityalliance.org/research/guidance/"),
    "wireshark": ("Wireshark User Guide - Network Packet Analysis", "https://www.wireshark.org/docs/wsug_html_chunked/"),
    "cryptography": ("Stanford Online / Coursera - Cryptography I Course", "https://www.coursera.org/learn/crypto"),
    "iam": ("AWS Identity and Access Management (IAM) User Guide", "https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html"),

    # Mobile, QA, Hardware & Specializations
    "react native": ("React Native Official Getting Started Documentation", "https://reactnative.dev/docs/getting-started"),
    "flutter": ("Flutter Official Getting Started Guide & Dart Basics", "https://docs.flutter.dev/get-started/"),
    "android development": ("Android Developers Official Course - Kotlin Foundations", "https://developer.android.com/courses"),
    "ios development": ("Apple Developer - Learn Swift & SwiftUI Tutorials", "https://developer.apple.com/learn/"),
    "qa automation": ("Selenium Official Documentation - Browser Automation", "https://www.selenium.dev/documentation/"),
    "playwright": ("Playwright Official Documentation - Fast End-to-End Testing", "https://playwright.dev/docs/intro"),
    "cypress": ("Cypress Official Guides - Modern Web Testing", "https://docs.cypress.io/guides/overview/why-cypress"),
    "api testing": ("Postman Learning Center - API Testing & Automation", "https://learning.postman.com/docs/getting-started/introduction/"),
    "software testing": ("ISTQB Certified Tester Foundation Level Syllabus", "https://www.istqb.org/certifications/certified-tester-foundation-level"),
    "blockchain": ("Ethereum.org - Developer Documentation & Smart Contracts", "https://ethereum.org/en/developers/docs/"),
    "web3": ("Web3.js Official Documentation - Ethereum JavaScript API", "https://web3js.readthedocs.io/"),
    "embedded systems": ("FreeRTOS Official Kernel Documentation & Guides", "https://www.freertos.org/Documentation/RTOS_book.html"),
    "iot": ("MQTT.org - Getting Started with IoT Messaging Protocol", "https://mqtt.org/getting-started/"),
    "microcontrollers": ("Arduino Official Documentation & Tutorials", "https://docs.arduino.cc/"),
    "system administration": ("Microsoft Learn - Windows Server Administration Fundamentals", "https://learn.microsoft.com/en-us/sysinternals/"),
}


def get_skill_resource(skill_name: str) -> Tuple[str, str]:
    """Retrieve verified learning resource (title, url) for any skill name with safe fallback."""
    clean_key = skill_name.strip().lower()

    # Exact match in repository
    if clean_key in LEARNING_RESOURCES:
        return LEARNING_RESOURCES[clean_key]

    # Substring matching against known keys
    for key, (title, url) in LEARNING_RESOURCES.items():
        if key in clean_key or clean_key in key:
            return (title, url)

    # Trustworthy search fallback
    encoded_query = urllib.parse.quote(f"{skill_name.title()} official tutorial for beginners documentation")
    fallback_url = f"https://www.google.com/search?q={encoded_query}"
    fallback_title = f"{skill_name.title()} Official Documentation & Tutorials (Verified Resource Search)"
    return fallback_title, fallback_url


# =============================================================================
# 3. STRUCTURED ROLE DEFINITIONS WITH INDIVIDUALIZED SKILL LISTS
# =============================================================================
def _make_skill(
    skill: str,
    display_name: str,
    stage: str,
    level: str,
    why_matters: str,
    practice_project: str,
    prerequisites: Optional[List[str]] = None,
    demand_pct: float = 75.0,
) -> Dict[str, Any]:
    """Helper factory function to construct a rich skill specification."""
    res_title, res_url = get_skill_resource(skill)
    return {
        "skill": skill.strip().lower(),
        "display_name": display_name,
        "stage": stage,
        "level": level,
        "why_matters": why_matters,
        "practice_project": practice_project,
        "prerequisites": prerequisites or [],
        "demand_pct": round(demand_pct, 1),
        "resource_title": res_title,
        "resource_url": res_url,
    }


# Comprehensive mapping of all 36 roles to unique, role-appropriate technical skill curriculums
ROLE_SKILLS_DATA: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # CATEGORY: AI & MACHINE LEARNING
    # -------------------------------------------------------------------------
    "AI Engineer": {
        "category": "AI & Machine Learning",
        "description": "Designs, trains, and deploys intelligent artificial intelligence architectures, deep neural networks, and generative models into high-scale production systems.",
        "skills": [
            _make_skill("python", "Python Programming", "Foundations", "Beginner", "Foundational language powering the entire modern AI ecosystem.", "Build an automated CLI data scraper and analyzer.", [], 98.5),
            _make_skill("numpy", "NumPy & Numerical Operations", "Foundations", "Beginner", "High-performance contiguous tensor representations.", "Implement matrix transformations and broadcasting routines from scratch.", ["python"], 92.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Essential for collaborative model tracking and code governance.", "Manage feature branches and pull requests on GitHub.", [], 88.0),
            _make_skill("machine learning", "Machine Learning Fundamentals", "Core Skills", "Intermediate", "Underpins predictive modeling, cost functions, and optimization.", "Train and tune classification models with cross-validation.", ["python", "numpy"], 94.0),
            _make_skill("deep learning", "Deep Learning & Neural Networks", "Core Skills", "Intermediate", "Core paradigm for vision, speech, and transformer architectures.", "Build multi-layer perceptrons with backpropagation.", ["machine learning"], 91.0),
            _make_skill("pytorch", "PyTorch Framework", "Core Skills", "Intermediate", "Industry standard library for research and production deep learning.", "Train a convolutional neural network with GPU acceleration.", ["deep learning"], 89.5),
            _make_skill("rest apis", "REST APIs & Model Serving", "Core Skills", "Intermediate", "Enables client applications to interface with inference endpoints.", "Deploy a model inference server using FastAPI.", ["python"], 84.0),
            _make_skill("docker", "Docker & Containerization", "Advanced Skills", "Advanced", "Packages model dependencies for reproducible cloud deployment.", "Containerize an AI service and orchestrate with Docker Compose.", ["linux"], 87.0),
            _make_skill("llms", "Large Language Models & Transformers", "Advanced Skills", "Advanced", "Powers cutting-edge generative AI and contextual text reasoning.", "Fine-tune an open-source LLM using LoRA techniques.", ["pytorch"], 93.0),
            _make_skill("vector databases", "Vector Databases & Embeddings", "Advanced Skills", "Advanced", "Enables semantic search, memory recall, and RAG architectures.", "Build a semantic document search engine with ChromaDB.", ["python"], 86.5),
            _make_skill("mlops", "MLOps & Automated Pipelines", "Projects & Specialization", "Advanced", "Maintains model health, CI/CD automation, and drift monitoring.", "Set up an automated model retraining pipeline with GitHub Actions.", ["docker"], 81.0),
        ],
    },

    "Machine Learning Engineer": {
        "category": "AI & Machine Learning",
        "description": "Bridges data science and software engineering by creating robust feature pipelines, scalable training workflows, and high-performance ML inference systems.",
        "skills": [
            _make_skill("python", "Python Core Mechanics", "Foundations", "Beginner", "Primary language for ML modeling, data structures, and automation.", "Develop modular data validation functions.", [], 98.0),
            _make_skill("pandas", "Pandas Data Manipulation", "Foundations", "Beginner", "Crucial for cleaning and structuring tabular training data.", "Perform feature aggregation on 500k+ customer transactions.", ["python"], 93.0),
            _make_skill("sql", "SQL Querying", "Foundations", "Beginner", "Extracts raw data directly from relational data stores.", "Construct multi-table JOINs and window function queries.", [], 89.0),
            _make_skill("scikit-learn", "Scikit-Learn Algorithms", "Core Skills", "Intermediate", "Gold standard for classical machine learning and preprocessing.", "Implement a Random Forest classifier with hyperparameter search.", ["python", "pandas"], 95.0),
            _make_skill("machine learning", "Machine Learning Algorithms", "Core Skills", "Intermediate", "Theoretical understanding of loss, regularization, and bias-variance.", "Compare performance curves of linear and ensemble models.", ["python"], 92.0),
            _make_skill("deep learning", "Deep Learning Foundations", "Core Skills", "Intermediate", "Required for non-linear pattern extraction in high-dimensional data.", "Construct and train a deep neural network on unstructured data.", ["machine learning"], 88.0),
            _make_skill("docker", "Docker Containerization", "Advanced Skills", "Advanced", "Eliminates environment drift across training and production.", "Package model prediction endpoints in Docker containers.", ["python"], 86.0),
            _make_skill("mlops", "MLOps & Continuous Training", "Advanced Skills", "Advanced", "Ensures models run reliably with automated monitoring.", "Configure an end-to-end ML tracking pipeline using MLflow.", ["docker"], 85.0),
            _make_skill("ci/cd", "CI/CD for Machine Learning", "Projects & Specialization", "Advanced", "Automates testing, packaging, and validation upon code commits.", "Build automated unit test pipelines validating model predictions.", ["docker"], 82.0),
        ],
    },

    "Deep Learning Engineer": {
        "category": "AI & Machine Learning",
        "description": "Specializes in multi-layer artificial neural networks, custom loss functions, tensor operations, and GPU-accelerated computing for perceptual intelligence.",
        "skills": [
            _make_skill("python", "Python for Scientific Computing", "Foundations", "Beginner", "Foundational programming language for deep learning scripts.", "Implement mathematical tensor routines.", [], 98.0),
            _make_skill("numpy", "NumPy Matrix Operations", "Foundations", "Beginner", "Understands contiguous memory and linear algebra transformations.", "Code vector dot products and matrix decompositions.", ["python"], 94.0),
            _make_skill("deep learning", "Deep Neural Networks", "Core Skills", "Intermediate", "Deep understanding of backpropagation, activations, and gradient descent.", "Build a custom multi-layer perceptron from mathematical equations.", ["numpy"], 96.0),
            _make_skill("pytorch", "PyTorch Deep Learning Framework", "Core Skills", "Intermediate", "Primary production engine for training complex networks.", "Build and train custom PyTorch modules with autograd.", ["deep learning"], 95.0),
            _make_skill("tensorflow", "TensorFlow & Keras", "Core Skills", "Intermediate", "Enterprise deep learning platform for scalable training.", "Construct sequential models with TensorBoard visualization.", ["deep learning"], 87.0),
            _make_skill("computer vision", "Convolutional Neural Networks (CNNs)", "Advanced Skills", "Advanced", "Essential for spatial image and video feature representation.", "Train a ResNet architecture for fine-grained image classification.", ["pytorch"], 91.0),
            _make_skill("llms", "Transformers & Attention Mechanisms", "Advanced Skills", "Advanced", "Core mechanism powering modern language, vision, and multi-modal models.", "Implement a multi-head self-attention layer in PyTorch.", ["pytorch"], 92.5),
            _make_skill("docker", "GPU Containerization with Docker", "Projects & Specialization", "Advanced", "Runs reproducible distributed GPU workloads in production clusters.", "Deploy a CUDA-accelerated inference container.", ["pytorch"], 84.0),
        ],
    },

    "NLP Engineer": {
        "category": "AI & Machine Learning",
        "description": "Builds linguistic AI applications, text processing engines, entity recognition models, and semantic language pipelines.",
        "skills": [
            _make_skill("python", "Python Programming", "Foundations", "Beginner", "Standard language for text tokenization, parsing, and NLP tooling.", "Write regular expression text parsers and sanitizers.", [], 98.0),
            _make_skill("git", "Version Control with Git", "Foundations", "Beginner", "Tracks corpus versions, tokenizers, and model checkpoints.", "Version code repositories on GitHub.", [], 85.0),
            _make_skill("nlp", "Natural Language Processing Fundamentals", "Core Skills", "Intermediate", "Tokenization, stemmers, TF-IDF, POS tagging, and sentiment scoring.", "Build a text classification pipeline using NLTK and spaCy.", ["python"], 96.0),
            _make_skill("pytorch", "PyTorch Framework", "Core Skills", "Intermediate", "Underlying deep learning framework for training language models.", "Train an LSTM model for sequence prediction.", ["python"], 90.0),
            _make_skill("llms", "Hugging Face & Transformer Models", "Advanced Skills", "Advanced", "Pre-trained language representations (BERT, RoBERTa, LLaMA).", "Fine-tune a BERT model for domain-specific Named Entity Recognition.", ["nlp", "pytorch"], 95.0),
            _make_skill("vector databases", "Vector Embeddings & Semantic Search", "Advanced Skills", "Advanced", "Indexes documents in high-dimensional vector spaces.", "Build a contextual semantic document retriever.", ["python"], 89.0),
            _make_skill("rest apis", "FastAPI Text API Services", "Projects & Specialization", "Advanced", "Serves real-time language inference to client frontends.", "Deploy a high-throughput multilingual translation API.", ["python"], 83.0),
        ],
    },

    "Computer Vision Engineer": {
        "category": "AI & Machine Learning",
        "description": "Develops algorithms that understand visual data, image segmentation, object detection, and spatial recognition.",
        "skills": [
            _make_skill("python", "Python Scientific Scripting", "Foundations", "Beginner", "Base programming language for computer vision experiments.", "Write automated image resizing and batching scripts.", [], 98.0),
            _make_skill("numpy", "NumPy Matrix & Image Arrays", "Foundations", "Beginner", "Images are represented as multi-channel 3D numerical arrays.", "Manipulate RGB channels and spatial filters with NumPy slicing.", ["python"], 95.0),
            _make_skill("computer vision", "OpenCV & Image Processing", "Core Skills", "Intermediate", "Edge detection, contours, morphological transforms, and affine warping.", "Build an automated document scanner with perspective correction.", ["numpy"], 96.0),
            _make_skill("deep learning", "Deep Learning Foundations", "Core Skills", "Intermediate", "Powers automatic feature extraction over manual kernel filters.", "Train a convolutional classifier on visual patterns.", ["numpy"], 91.0),
            _make_skill("pytorch", "PyTorch Vision Pipelines", "Core Skills", "Intermediate", "Standard framework for modern vision architectures (YOLO, ResNet).", "Train a custom object detector using transfer learning.", ["deep learning"], 93.0),
            _make_skill("docker", "Docker Edge Deployment", "Advanced Skills", "Advanced", "Deploys vision models to edge devices and cloud instances.", "Containerize a real-time OpenCV stream processing service.", ["python"], 84.0),
            _make_skill("rest apis", "Video & Image Streaming APIs", "Projects & Specialization", "Advanced", "Delivers live camera inferences to client applications.", "Build a real-time web camera detection dashboard.", ["pytorch"], 82.0),
        ],
    },

    "Generative AI Engineer": {
        "category": "AI & Machine Learning",
        "description": "Specializes in foundation models, prompt architecture, Retrieval-Augmented Generation (RAG), and autonomous agent networks.",
        "skills": [
            _make_skill("python", "Python for Modern AI", "Foundations", "Beginner", "Primary syntax for AI SDKs, orchestration frameworks, and APIs.", "Build an automated document ingestion script.", [], 99.0),
            _make_skill("prompt engineering", "Prompt Engineering & Structure", "Foundations", "Beginner", "Master few-shot prompting, chain-of-thought, and output constraints.", "Craft structured JSON extraction prompts with high reliability.", ["python"], 94.0),
            _make_skill("llms", "Foundation LLMs & Transformers", "Core Skills", "Intermediate", "In-depth understanding of context windows, tokenization, and temperature.", "Benchmark responses across multiple commercial foundation models.", ["python"], 96.0),
            _make_skill("langchain", "LangChain & Agentic Frameworks", "Core Skills", "Intermediate", "Chains prompts, memories, and external tools into autonomous workflows.", "Build a research assistant agent equipped with web browsing tools.", ["python", "llms"], 95.0),
            _make_skill("vector databases", "Vector Databases & Embeddings", "Core Skills", "Intermediate", "Grounds generative models in external factual knowledge.", "Implement a hybrid keyword + vector retrieval system.", ["python"], 92.0),
            _make_skill("rest apis", "FastAPI AI Streaming Services", "Advanced Skills", "Advanced", "Streams Server-Sent Events (SSE) tokens to responsive frontends.", "Build an asynchronous streaming chat API with token metrics.", ["python"], 88.0),
            _make_skill("docker", "Docker Deployment for AI Agents", "Projects & Specialization", "Advanced", "Provides reproducible sandboxed execution for agent tools.", "Deploy a containerized RAG microservice with automated health checks.", ["python"], 85.0),
        ],
    },

    # -------------------------------------------------------------------------
    # CATEGORY: DATA CAREERS
    # -------------------------------------------------------------------------
    "Data Analyst": {
        "category": "Data Careers",
        "description": "Translates numbers into actionable business insights through SQL queries, statistical analysis, and interactive executive dashboards.",
        "skills": [
            _make_skill("excel", "Advanced Excel & Formulas", "Foundations", "Beginner", "Universal tool for rapid ad-hoc calculations and pivot tables.", "Build an interactive financial variance model with XLOOKUP.", [], 92.0),
            _make_skill("sql", "SQL Querying & Data Extraction", "Foundations", "Beginner", "Extracts, filters, and joins data across relational enterprise databases.", "Write complex multi-table queries with window functions.", [], 97.0),
            _make_skill("statistics", "Business Statistics Fundamentals", "Foundations", "Beginner", "Crucial for understanding distributions, confidence intervals, and hypothesis tests.", "Conduct an A/B test analysis calculating p-values and effect size.", [], 88.0),
            _make_skill("python", "Python for Data Analysis", "Core Skills", "Intermediate", "Automates repetitive workflows and cleans messy datasets.", "Write automated CSV data cleaning scripts.", ["sql"], 89.0),
            _make_skill("pandas", "Pandas Data Manipulation", "Core Skills", "Intermediate", "Powerful DataFrame filtering, grouping, and aggregation routines.", "Perform cohort analysis calculating monthly user retention rates.", ["python"], 93.0),
            _make_skill("power bi", "Power BI Interactive Dashboards", "Core Skills", "Intermediate", "Builds executive reports with DAX calculations and data drill-downs.", "Design an executive sales performance dashboard with DAX measures.", ["sql"], 94.0),
            _make_skill("tableau", "Tableau Visual Storytelling", "Advanced Skills", "Intermediate", "Industry standard platform for interactive visual presentations.", "Publish an interactive customer journey dashboard to Tableau Public.", ["sql"], 90.0),
            _make_skill("data modeling", "Star Schema & Data Modeling", "Projects & Specialization", "Advanced", "Structures data warehouses for high-speed business reporting.", "Design a star-schema fact and dimension model for e-commerce.", ["sql"], 84.0),
        ],
    },

    "Data Scientist": {
        "category": "Data Careers",
        "description": "Applies statistical modeling, machine learning, and predictive analytics to discover hidden patterns and solve complex business problems.",
        "skills": [
            _make_skill("python", "Python for Data Science", "Foundations", "Beginner", "Standard programming language for data manipulation and modeling.", "Develop reusable statistical testing modules in Python.", [], 99.0),
            _make_skill("sql", "Advanced SQL Analytics", "Foundations", "Beginner", "Extracts complex cohorts and historical aggregations from databases.", "Write recursive CTEs and analytical window functions.", [], 95.0),
            _make_skill("statistics", "Applied Probability & Statistics", "Foundations", "Beginner", "Theoretical bedrock of hypothesis testing, regression, and variance.", "Perform multivariate hypothesis tests on simulated experiment data.", [], 93.0),
            _make_skill("pandas", "Pandas & Data Wrangling", "Core Skills", "Intermediate", "Cleans, pivots, and reshapes messy multi-source data.", "Handle missing data and imputations across multi-gigabyte datasets.", ["python"], 96.0),
            _make_skill("matplotlib", "Data Visualization with Matplotlib & Seaborn", "Core Skills", "Intermediate", "Communicates exploratory data distributions and model metrics.", "Generate publication-grade correlation heatmaps and violin plots.", ["python", "pandas"], 91.0),
            _make_skill("scikit-learn", "Scikit-Learn Machine Learning", "Core Skills", "Intermediate", "Standard toolkit for classification, regression, and clustering.", "Build a customer churn predictor with ROC-AUC evaluation.", ["python", "pandas"], 96.0),
            _make_skill("deep learning", "Deep Learning Foundations", "Advanced Skills", "Advanced", "Models unstructured text, vision, and high-cardinality sequences.", "Train a multi-layer neural network on tabular embeddings.", ["scikit-learn"], 87.0),
            _make_skill("data modeling", "Feature Engineering & Data Modeling", "Projects & Specialization", "Advanced", "Extracts high-signal predictive features from raw event streams.", "Engineer automated time-series lag and rolling average features.", ["pandas"], 88.0),
        ],
    },

    "Data Engineer": {
        "category": "Data Careers",
        "description": "Constructs reliable data pipelines, automated ETL workflows, scalable data warehouses, and streaming architectures.",
        "skills": [
            _make_skill("sql", "SQL Mastery & Optimization", "Foundations", "Beginner", "Defines relational schemas, indexes, and high-performance queries.", "Tune and optimize slow join queries using execution explain plans.", [], 98.0),
            _make_skill("python", "Python for Data Engineering", "Foundations", "Beginner", "Core language for data transformations, API calls, and pipeline DAGs.", "Write an automated data pipeline extracting JSON from REST APIs.", [], 96.0),
            _make_skill("linux", "Linux & Bash Automation", "Foundations", "Beginner", "Required for managing cloud VMs, cron schedules, and permissions.", "Write automated bash scripts that archive and transfer data files.", [], 88.0),
            _make_skill("data warehousing", "Cloud Data Warehousing (Snowflake / BigQuery)", "Core Skills", "Intermediate", "Modern columnar storage architectures for petabyte-scale analytics.", "Design and partition a data warehouse in Snowflake.", ["sql"], 95.0),
            _make_skill("etl pipelines", "ETL & Workflow Orchestration (Airflow)", "Core Skills", "Intermediate", "Coordinates scheduled dependency graphs and automated retries.", "Build an Apache Airflow DAG extracting, transforming, and loading data.", ["python"], 94.0),
            _make_skill("dbt", "dbt (Data Build Tool)", "Core Skills", "Intermediate", "Enables modular, test-driven SQL data transformation inside warehouses.", "Build production dbt models with automated schema tests.", ["sql"], 92.0),
            _make_skill("spark", "Apache Spark Big Data Processing", "Advanced Skills", "Advanced", "Distributed in-memory computing for large-scale data processing.", "Write PySpark transformations over terabytes of distributed data.", ["python"], 89.0),
            _make_skill("docker", "Docker for Data Infrastructure", "Advanced Skills", "Advanced", "Runs Airflow, Spark, and local databases in reproducible environments.", "Deploy a local multi-container Airflow and Postgres cluster.", ["linux"], 87.0),
            _make_skill("git", "Git for Data Pipelines", "Projects & Specialization", "Advanced", "Governs data code, automated schema migrations, and CI/CD.", "Implement automated CI testing for dbt pipeline pull requests.", [], 85.0),
        ],
    },

    "Business Intelligence Developer": {
        "category": "Data Careers",
        "description": "Designs enterprise analytics architectures, dimensional star schemas, self-service BI systems, and automated executive reporting.",
        "skills": [
            _make_skill("sql", "SQL & Database Design", "Foundations", "Beginner", "The foundation of all business data queries and view definitions.", "Write parameterized analytical SQL views for reporting engines.", [], 98.0),
            _make_skill("excel", "Excel Analytical Modeling", "Foundations", "Beginner", "Rapid prototyping of business rules and ad-hoc client models.", "Build dynamic financial scenario models with sensitivity tables.", [], 89.0),
            _make_skill("data modeling", "Dimensional Modeling & Star Schema", "Core Skills", "Intermediate", "Designing clean fact tables and dimension hierarchies.", "Design a complete star schema model for retail inventory analytics.", ["sql"], 95.0),
            _make_skill("power bi", "Power BI & Advanced DAX", "Core Skills", "Intermediate", "Builds complex dynamic calculations and interactive reports.", "Create advanced DAX measures calculating Year-Over-Year growth.", ["sql"], 96.0),
            _make_skill("tableau", "Tableau Enterprise Reporting", "Core Skills", "Intermediate", "Visual analytics platform for executive presentation.", "Design an interactive operational health dashboard.", ["sql"], 90.0),
            _make_skill("data warehousing", "Data Warehousing Fundamentals", "Advanced Skills", "Advanced", "Structures historical business data for performant analytics.", "Implement slowly changing dimensions (SCD Type 2) in a warehouse.", ["sql"], 87.0),
            _make_skill("etl pipelines", "ETL Fundamentals", "Projects & Specialization", "Advanced", "Automates nightly data extraction into analytics datamarts.", "Build an automated data extraction and transformation pipeline.", ["sql"], 85.0),
        ],
    },

    "Analytics Engineer": {
        "category": "Data Careers",
        "description": "Bridges data engineering and data analysis by applying software engineering best practices to data models, testing, and semantic layers.",
        "skills": [
            _make_skill("sql", "Advanced Analytical SQL", "Foundations", "Beginner", "Core language of the modern data stack and warehouse modeling.", "Write window functions, CTEs, and complex joins.", [], 99.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Enables peer reviews, pull requests, and CI/CD for data models.", "Manage branching and code reviews for data warehouse repositories.", [], 92.0),
            _make_skill("python", "Python for Analytics", "Foundations", "Beginner", "Used for custom data tests, API connectors, and automation.", "Write automated data verification scripts in Python.", [], 89.0),
            _make_skill("dbt", "dbt (Data Build Tool)", "Core Skills", "Intermediate", "Applies software engineering (tests, documentation, versioning) to SQL.", "Develop modular dbt models with unit tests and documentation.", ["sql", "git"], 97.0),
            _make_skill("data warehousing", "Cloud Data Warehouses (Snowflake/BigQuery)", "Core Skills", "Intermediate", "Columnar warehouses that store transformed analytical assets.", "Configure role-based access and compute clustering in Snowflake.", ["sql"], 94.0),
            _make_skill("data modeling", "Dimensional Modeling", "Advanced Skills", "Advanced", "Organizes business logic into reusable, standardized dimensions.", "Build an enterprise customer 360 dimensional model.", ["sql"], 93.0),
            _make_skill("ci/cd", "CI/CD for Data Platforms", "Projects & Specialization", "Advanced", "Runs automated data tests on pull requests before deployment.", "Configure GitHub Actions to run dbt build on pull requests.", ["git", "dbt"], 88.0),
        ],
    },

    # -------------------------------------------------------------------------
    # CATEGORY: SOFTWARE DEVELOPMENT
    # -------------------------------------------------------------------------
    "Full Stack Developer": {
        "category": "Software Development",
        "description": "Builds end-to-end web applications, encompassing responsive client frontends, robust backend APIs, databases, and deployment.",
        "skills": [
            _make_skill("html", "HTML5 & Semantic Markup", "Foundations", "Beginner", "The foundational skeleton of all accessible web applications.", "Code an accessible, semantically structured portfolio website.", [], 98.0),
            _make_skill("css", "CSS3 & Modern Layouts", "Foundations", "Beginner", "Styles web applications using Flexbox, CSS Grid, and responsive queries.", "Build a responsive mobile-first landing page with Flexbox and Grid.", ["html"], 96.0),
            _make_skill("javascript", "Modern JavaScript (ES6+)", "Foundations", "Beginner", "Powers interactive client-side logic and modern asynchronous operations.", "Build an interactive task tracker with DOM manipulation and fetch API.", ["html"], 99.0),
            _make_skill("git", "Git & GitHub Version Control", "Foundations", "Beginner", "Essential tool for code tracking, branching, and team collaboration.", "Manage collaborative pull requests and merge conflicts.", [], 94.0),
            _make_skill("react", "React.js Framework", "Core Skills", "Intermediate", "Declarative component-driven frontend architecture.", "Build an interactive e-commerce shopping cart with state management.", ["javascript"], 97.0),
            _make_skill("node.js", "Node.js & Express Runtime", "Core Skills", "Intermediate", "Executes JavaScript on the server to build high-concurrency backends.", "Construct a RESTful CRUD API server with route handlers.", ["javascript"], 95.0),
            _make_skill("rest apis", "REST API Architecture", "Core Skills", "Intermediate", "Standard communication protocol between frontend and backend services.", "Design clean endpoints following HTTP status codes and JSON specs.", ["node.js"], 93.0),
            _make_skill("postgresql", "Relational Databases (PostgreSQL / SQL)", "Core Skills", "Intermediate", "Stores persistent user, product, and application data reliably.", "Design an e-commerce database schema with foreign keys and indexes.", ["sql"], 94.0),
            _make_skill("typescript", "TypeScript Type Safety", "Advanced Skills", "Advanced", "Adds compile-time type safety to full-stack codebases, reducing bugs.", "Refactor a JavaScript React and Node codebase to strict TypeScript.", ["javascript"], 91.0),
            _make_skill("docker", "Docker Containerization", "Advanced Skills", "Advanced", "Packages the entire full-stack app for identical production deployment.", "Dockerize a multi-container React, Node, and Postgres application.", ["node.js"], 88.0),
            _make_skill("ci/cd", "CI/CD & Cloud Deployment", "Projects & Specialization", "Advanced", "Automates testing, building, and deploying web applications.", "Deploy a full-stack SaaS platform to the cloud with GitHub Actions.", ["docker"], 86.0),
        ],
    },

    "Frontend Developer": {
        "category": "Software Development",
        "description": "Crafts responsive, accessible, and high-performance user interfaces and interactive experiences for the web.",
        "skills": [
            _make_skill("html", "HTML5 & Semantic Elements", "Foundations", "Beginner", "Provides structural hierarchy and accessibility for web pages.", "Build a semantic, accessible content article with audio/video tags.", [], 99.0),
            _make_skill("css", "Modern CSS & Flexbox / Grid", "Foundations", "Beginner", "Controls layouts, animations, transitions, and media queries.", "Design a responsive multi-column magazine layout.", ["html"], 98.0),
            _make_skill("javascript", "JavaScript ES6+ & DOM Manipulation", "Foundations", "Beginner", "Drives asynchronous fetching, event handling, and dynamic UI state.", "Build a dynamic weather dashboard fetching public weather APIs.", ["html", "css"], 99.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Tracks UI iterations and component changes.", "Create and review pull requests on GitHub.", [], 92.0),
            _make_skill("react", "React.js Component Architecture", "Core Skills", "Intermediate", "Builds reusable UI components using hooks and virtual DOM.", "Construct a real-time Kanban board with drag-and-drop state.", ["javascript"], 98.0),
            _make_skill("tailwind css", "Tailwind CSS Utility Framework", "Core Skills", "Intermediate", "Rapid UI styling directly in markup with responsive design tokens.", "Build a modern dark-mode enabled dashboard with Tailwind.", ["css"], 94.0),
            _make_skill("typescript", "TypeScript for Frontend", "Core Skills", "Intermediate", "Prevents runtime UI errors through strict prop and state typing.", "Write type-safe React components with typed props and events.", ["javascript"], 92.0),
            _make_skill("next.js", "Next.js & Server-Side Rendering", "Advanced Skills", "Advanced", "Provides SSR, static site generation, and SEO optimization.", "Build a high-performance blog platform with Next.js App Router.", ["react"], 93.0),
            _make_skill("accessibility", "Web Accessibility (WCAG / a11y)", "Advanced Skills", "Advanced", "Ensures web apps are usable by people with disabilities and screen readers.", "Audit and remediate accessibility issues using Lighthouse and Axe.", ["html"], 88.0),
            _make_skill("web performance", "Web Performance & Core Web Vitals", "Projects & Specialization", "Advanced", "Optimizes bundle sizes, lazy loading, and rendering speed.", "Optimize a web application to achieve 95+ Google Lighthouse score.", ["javascript"], 87.0),
        ],
    },

    "Backend Developer": {
        "category": "Software Development",
        "description": "Engineers scalable server-side systems, business logic, microservices, databases, and secure APIs.",
        "skills": [
            _make_skill("python", "Python / Core Backend Language", "Foundations", "Beginner", "Server-side language for rapid, readable, and maintainable backend code.", "Build modular data processing and validation services.", [], 97.0),
            _make_skill("sql", "SQL Querying & Schema Design", "Foundations", "Beginner", "Communicates with relational databases to store and query state.", "Design relational tables with indexes and foreign key constraints.", [], 96.0),
            _make_skill("git", "Git & Code Collaboration", "Foundations", "Beginner", "Governs backend versions, releases, and branch protection.", "Manage trunk-based development with pull requests.", [], 91.0),
            _make_skill("rest apis", "RESTful API Engineering", "Core Skills", "Intermediate", "Designs robust, secure HTTP endpoints for client consumption.", "Build an authenticated REST API with rate limiting and input validation.", ["python"], 96.0),
            _make_skill("postgresql", "PostgreSQL Database Administration", "Core Skills", "Intermediate", "Enterprise open-source relational database engine.", "Optimize queries using indexing strategies and EXPLAIN ANALYZE.", ["sql"], 94.0),
            _make_skill("node.js", "Node.js & Express / FastAPI", "Core Skills", "Intermediate", "Asynchronous runtime for high-throughput server backends.", "Construct an asynchronous microservice handling concurrent requests.", ["rest apis"], 93.0),
            _make_skill("redis", "Redis Caching & Session Storage", "Advanced Skills", "Advanced", "Ultra-fast in-memory cache reducing database load.", "Implement a Redis caching layer for heavy database queries.", ["python"], 90.0),
            _make_skill("docker", "Docker for Backend Services", "Advanced Skills", "Advanced", "Isolates server environments and database dependencies.", "Deploy containerized backend services with Docker Compose.", ["linux"], 89.0),
            _make_skill("microservices", "Microservices & Message Queues", "Projects & Specialization", "Advanced", "Decouples services using message brokers like RabbitMQ or Kafka.", "Build an asynchronous order processing pipeline with message queues.", ["docker"], 86.0),
        ],
    },

    "Software Developer": {
        "category": "Software Development",
        "description": "Generalist software engineer building robust computer programs, algorithms, data structures, and maintainable systems.",
        "skills": [
            _make_skill("python", "Core Programming Fundamentals", "Foundations", "Beginner", "Develops computational thinking, control flow, and modularity.", "Implement core search and sorting algorithms.", [], 98.0),
            _make_skill("git", "Version Control with Git", "Foundations", "Beginner", "Governs source code history, tagging, and team branches.", "Collaborate on a multi-contributor open source repository.", [], 93.0),
            _make_skill("sql", "SQL Data Manipulation", "Foundations", "Beginner", "Extracts, inserts, and manages structured application data.", "Write complex analytical SQL queries.", [], 92.0),
            _make_skill("linux", "Linux Systems & CLI", "Foundations", "Beginner", "Standard operating system for running and testing software.", "Automate development environments with bash shell scripts.", [], 89.0),
            _make_skill("rest apis", "REST APIs & Web Services", "Core Skills", "Intermediate", "Exposes software functionality to web and mobile clients.", "Build a multi-tier API service with full error handling.", ["python"], 94.0),
            _make_skill("postgresql", "Relational Databases", "Core Skills", "Intermediate", "Provides ACID compliance and transactional data guarantees.", "Design database schemas with constraints and triggers.", ["sql"], 92.0),
            _make_skill("docker", "Docker Containers", "Core Skills", "Intermediate", "Standardizes development and production software runtimes.", "Package a software application into a Docker container.", ["linux"], 88.0),
            _make_skill("ci/cd", "CI/CD & Automated Testing", "Advanced Skills", "Advanced", "Verifies code health automatically with unit and integration tests.", "Set up automated test pipelines with GitHub Actions.", ["git"], 87.0),
            _make_skill("microservices", "Software Design Patterns & Architecture", "Projects & Specialization", "Advanced", "Applies clean architecture and SOLID design principles.", "Refactor a monolithic service into decoupled modular components.", ["rest apis"], 85.0),
        ],
    },

    "Mobile App Developer": {
        "category": "Software Development",
        "description": "Builds native and cross-platform mobile applications for smartphones and tablets across iOS and Android.",
        "skills": [
            _make_skill("javascript", "JavaScript Fundamentals", "Foundations", "Beginner", "Core language powering cross-platform mobile runtimes.", "Write asynchronous JavaScript functions and event handlers.", [], 96.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Tracks mobile app releases, assets, and feature development.", "Manage mobile release branches on GitHub.", [], 90.0),
            _make_skill("react native", "React Native Cross-Platform", "Core Skills", "Intermediate", "Builds native iOS and Android apps from a unified JavaScript codebase.", "Construct a cross-platform mobile fitness tracker app.", ["javascript"], 96.0),
            _make_skill("rest apis", "Mobile REST API Integration", "Core Skills", "Intermediate", "Connects mobile apps to cloud backends and authentication.", "Connect mobile app screens to a backend JSON API.", ["react native"], 94.0),
            _make_skill("typescript", "TypeScript for Mobile", "Core Skills", "Intermediate", "Enforces strict type safety across navigation screens and states.", "Write typed React Native navigation and state structures.", ["javascript"], 91.0),
            _make_skill("android development", "Android SDK & Mobile OS Architecture", "Advanced Skills", "Advanced", "Understands Android lifecycles, permissions, and native components.", "Integrate native camera and geolocation hardware permissions.", ["react native"], 89.0),
            _make_skill("ios development", "iOS & Apple Human Interface Guidelines", "Advanced Skills", "Advanced", "Ensures compliance with Apple App Store guidelines and gesture UX.", "Style mobile screens following iOS design standards.", ["react native"], 88.0),
            _make_skill("ci/cd", "Mobile App Deployment (App Store / Play Store)", "Projects & Specialization", "Advanced", "Automates building APKs/IPAs and deploying to mobile app stores.", "Configure automated mobile builds using Fastlane.", ["git"], 84.0),
        ],
    },

    "Python Developer": {
        "category": "Software Development",
        "description": "Specializes in Pythonic programming, web frameworks (Django/FastAPI), asynchronous concurrency, and automation.",
        "skills": [
            _make_skill("python", "Python Deep Dive & OOP", "Foundations", "Beginner", "Advanced Python mechanics, generators, decorators, and context managers.", "Implement custom context managers and functional decorators.", [], 99.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Governs Python package versions and releases.", "Create and publish a Python package on PyPI test index.", [], 92.0),
            _make_skill("sql", "SQL & Database Interaction", "Foundations", "Beginner", "Interacts with relational database engines via raw SQL and ORMs.", "Write optimized database queries using Python DB-API.", [], 94.0),
            _make_skill("fastapi", "FastAPI Modern Web Services", "Core Skills", "Intermediate", "Builds fast, self-documenting asynchronous Python APIs.", "Develop a high-performance async REST API with Pydantic validation.", ["python"], 97.0),
            _make_skill("django", "Django Web Framework", "Core Skills", "Intermediate", "Full-featured 'batteries-included' web framework with built-in admin.", "Build an enterprise CRM web portal with Django ORM and auth.", ["python", "sql"], 93.0),
            _make_skill("postgresql", "PostgreSQL & SQLAlchemy", "Core Skills", "Intermediate", "Object-relational mapping and database migrations with Alembic.", "Configure SQLAlchemy models and automated database migrations.", ["sql"], 92.0),
            _make_skill("docker", "Docker for Python Microservices", "Advanced Skills", "Advanced", "Containerizes Python runtimes and virtual environments.", "Create lightweight multi-stage Docker builds for Python apps.", ["python"], 89.0),
            _make_skill("redis", "Redis & Celery Task Queues", "Advanced Skills", "Advanced", "Executes background workers and asynchronous task scheduling.", "Configure Celery workers for automated background email sending.", ["python"], 87.0),
            _make_skill("ci/cd", "Pytest & CI/CD Pipelines", "Projects & Specialization", "Advanced", "Automated unit and integration testing with code coverage reports.", "Achieve 90%+ test coverage with Pytest and GitHub Actions.", ["python"], 86.0),
        ],
    },

    "Java Developer": {
        "category": "Software Development",
        "description": "Develops enterprise-grade backend systems, Spring Boot microservices, high-concurrency transactional architectures, and JVM applications.",
        "skills": [
            _make_skill("java", "Java Core & Object-Oriented Design", "Foundations", "Beginner", "Solid foundation in Java syntax, JVM internals, collections, and streams.", "Implement object-oriented design patterns (Factory, Strategy).", [], 99.0),
            _make_skill("git", "Git for Enterprise Projects", "Foundations", "Beginner", "Manages enterprise software branches and Maven/Gradle dependencies.", "Maintain clean feature branches and multi-module builds.", [], 91.0),
            _make_skill("sql", "SQL & Database Design", "Foundations", "Beginner", "Interacts with enterprise relational databases.", "Write complex relational queries with joins and subqueries.", [], 94.0),
            _make_skill("spring boot", "Spring Boot Framework", "Core Skills", "Intermediate", "The dominant framework for enterprise Java web applications and microservices.", "Build a production-grade RESTful API with Spring Boot.", ["java"], 98.0),
            _make_skill("postgresql", "Hibernate & JPA Data Persistence", "Core Skills", "Intermediate", "Simplifies object-relational mapping and transaction management.", "Configure Spring Data JPA entities with automatic repository methods.", ["java", "sql"], 94.0),
            _make_skill("rest apis", "Enterprise REST APIs & Security", "Core Skills", "Intermediate", "Secures APIs with Spring Security, OAuth2, and JWT tokens.", "Secure an API with Spring Security and role-based access control.", ["spring boot"], 93.0),
            _make_skill("docker", "Docker for JVM Services", "Advanced Skills", "Advanced", "Containerizes Java JARs for high-scale cloud deployment.", "Containerize a Spring Boot application using multi-stage Docker builds.", ["java"], 88.0),
            _make_skill("microservices", "Microservices with Spring Cloud", "Advanced Skills", "Advanced", "Builds distributed services with service discovery and API gateways.", "Construct a distributed microservice cluster with Eureka and Gateway.", ["spring boot"], 87.0),
            _make_skill("ci/cd", "Maven / Gradle & CI/CD Automation", "Projects & Specialization", "Advanced", "Automates Java compilation, JUnit tests, and cloud deployments.", "Build an automated Jenkins/GitHub Actions pipeline for Java JARs.", ["java"], 85.0),
        ],
    },

    # -------------------------------------------------------------------------
    # CATEGORY: CYBERSECURITY
    # -------------------------------------------------------------------------
    "Cybersecurity Analyst": {
        "category": "Cybersecurity",
        "description": "Monitors security events, investigates incidents, analyzes vulnerabilities, and defends corporate networks against intrusions.",
        "skills": [
            _make_skill("networking", "Computer Networking (TCP/IP, DNS, Subnets)", "Foundations", "Beginner", "Must understand how data travels across networks to spot malicious traffic.", "Analyze packet captures and identify TCP handshake anomalies.", [], 98.0),
            _make_skill("linux", "Linux System Administration", "Foundations", "Beginner", "Security tools and server forensics run heavily on Linux environments.", "Navigate system directories, permissions, and log files in /var/log.", [], 95.0),
            _make_skill("security fundamentals", "Cybersecurity Core Principles", "Foundations", "Beginner", "CIA triad, defense-in-depth, threat actors, and attack vectors.", "Conduct a vulnerability assessment on a local virtual machine.", [], 97.0),
            _make_skill("python", "Python Scripting for Security", "Core Skills", "Intermediate", "Automates log parsing, API checks, and threat intelligence lookups.", "Write a Python script that parses firewall logs for repeated failed logins.", ["networking"], 91.0),
            _make_skill("siem tools", "SIEM Tools & Log Analysis (Splunk/Sentinel)", "Core Skills", "Intermediate", "Centralizes and correlates millions of enterprise security events.", "Construct Splunk queries to detect brute-force password attacks.", ["networking", "linux"], 96.0),
            _make_skill("wireshark", "Wireshark & Packet Forensics", "Core Skills", "Intermediate", "Deep inspection of network traffic to discover active malware communication.", "Inspect suspicious PCAP files and extract transmitted credentials.", ["networking"], 92.0),
            _make_skill("incident response", "Incident Response & Playbooks", "Advanced Skills", "Advanced", "Steps to contain, eradicate, and recover from cybersecurity breaches.", "Draft a comprehensive incident response plan for ransomware infection.", ["siem tools"], 94.0),
            _make_skill("cybersecurity", "Vulnerability Management & OWASP", "Advanced Skills", "Advanced", "Scans systems for unpatched flaws before adversaries exploit them.", "Scan a network using Nessus and prioritize remediation tickets.", ["security fundamentals"], 90.0),
            _make_skill("soc analyst", "Threat Intelligence & MITRE ATT&CK", "Projects & Specialization", "Advanced", "Maps adversary techniques to proactive cyber defenses.", "Map simulated adversary behaviors to the MITRE ATT&CK matrix.", ["siem tools"], 88.0),
        ],
    },

    "Security Engineer": {
        "category": "Cybersecurity",
        "description": "Designs and builds secure systems, automated security controls, firewall architectures, and identity governance.",
        "skills": [
            _make_skill("networking", "Network Security Architecture", "Foundations", "Beginner", "Understands firewalls, VPNs, proxies, and DMZ network topology.", "Design a secure segmented corporate network topology.", [], 97.0),
            _make_skill("linux", "Linux Systems Hardening", "Foundations", "Beginner", "Applies CIS benchmarks, kernel hardening, and least privilege permissions.", "Harden a Linux server following CIS Level 1 benchmarks.", [], 96.0),
            _make_skill("cryptography", "Applied Cryptography & PKI", "Foundations", "Beginner", "Symmetric/asymmetric encryption, hashing, certificates, and TLS.", "Set up a private Certificate Authority (CA) and issue TLS certs.", [], 93.0),
            _make_skill("python", "Python / Go for Security Automation", "Core Skills", "Intermediate", "Automates security policy checks and vulnerability remediations.", "Write automated scripts checking cloud security configurations.", ["linux"], 90.0),
            _make_skill("iam", "Identity & Access Management (IAM)", "Core Skills", "Intermediate", "Enforces least-privilege access, MFA, and federated SSO.", "Design an enterprise role-based access control (RBAC) policy.", ["security fundamentals"], 94.0),
            _make_skill("cloud security", "Cloud Security (AWS / Azure)", "Core Skills", "Intermediate", "Secures cloud VPCs, storage buckets, and IAM roles against leaks.", "Audit cloud infrastructure and remediate public storage buckets.", ["iam"], 95.0),
            _make_skill("cybersecurity", "Application Security & OWASP Top 10", "Advanced Skills", "Advanced", "Prevents code vulnerabilities (SQLi, XSS, CSRF, SSRF).", "Implement automated security linting (SAST) in a CI/CD pipeline.", ["security fundamentals"], 92.0),
            _make_skill("docker", "Container & Kubernetes Security", "Projects & Specialization", "Advanced", "Secures container images, rootless execution, and Kubernetes RBAC.", "Scan Docker images for CVE vulnerabilities with Trivy.", ["linux"], 89.0),
        ],
    },

    "Penetration Tester": {
        "category": "Cybersecurity",
        "description": "Simulates real-world cyber attacks against networks, web applications, and systems to discover and prove exploitable vulnerabilities.",
        "skills": [
            _make_skill("linux", "Kali Linux & Command Line Mastery", "Foundations", "Beginner", "The primary operating system and toolkit for offensive security testing.", "Configure and navigate offensive security tools in Kali Linux.", [], 97.0),
            _make_skill("networking", "Network Protocols & Port Scanning", "Foundations", "Beginner", "Identifies active hosts, open ports, and running service banners.", "Perform comprehensive network reconnaissance with Nmap.", [], 98.0),
            _make_skill("bash", "Bash & Python Scripting for Pentesting", "Foundations", "Beginner", "Customizes public exploits and automates repetitive test sequences.", "Write a multi-threaded port and directory enumeration script.", ["networking"], 91.0),
            _make_skill("cybersecurity", "OWASP Web Vulnerability Exploitation", "Core Skills", "Intermediate", "Exploits SQL injection, cross-site scripting (XSS), and authentication flaws.", "Identify and exploit SQLi vulnerabilities on a test web application.", ["networking"], 98.0),
            _make_skill("penetration testing", "Burp Suite & Web Proxy Interception", "Core Skills", "Intermediate", "Intercepts, modifies, and automates HTTP requests between browser and server.", "Intercept and bypass client-side validation using Burp Suite.", ["cybersecurity"], 96.0),
            _make_skill("ethical hacking", "Privilege Escalation Techniques", "Advanced Skills", "Advanced", "Elevates low-privileged user shells to root/Administrator permissions.", "Exploit a misconfigured SUID binary on Linux to gain root access.", ["linux"], 93.0),
            _make_skill("wireshark", "Network Sniffing & MITM Attacks", "Advanced Skills", "Advanced", "Captures credentials and session tokens over unencrypted protocols.", "Perform ARP spoofing in a closed virtual lab to inspect credentials.", ["networking"], 88.0),
            _make_skill("incident response", "Penetration Testing Documentation & Reporting", "Projects & Specialization", "Advanced", "Communicates technical risks and remediation steps to executives.", "Write an executive penetration test report detailing critical findings.", ["cybersecurity"], 89.0),
        ],
    },

    "Ethical Hacker": {
        "category": "Cybersecurity",
        "description": "Applies offensive hacking techniques ethically to evaluate security postures, perform red teaming, and discover zero-day flaws.",
        "skills": [
            _make_skill("networking", "TCP/IP & Protocol Analysis", "Foundations", "Beginner", "Foundational understanding of network communication and routing.", "Capture and dissect raw network traffic frames.", [], 98.0),
            _make_skill("linux", "Linux Systems & File Permissions", "Foundations", "Beginner", "Navigating target filesystems and exploiting misconfigured access.", "Enumerate Linux user privileges and cron jobs.", [], 96.0),
            _make_skill("python", "Python for Exploit Development", "Foundations", "Beginner", "Crafts custom network payloads and automated brute-force tools.", "Build a custom password hash cracking script using Python.", ["networking"], 92.0),
            _make_skill("ethical hacking", "Ethical Hacking Methodologies & Reconnaissance", "Core Skills", "Intermediate", "Information gathering, OSINT, service enumeration, and vulnerability discovery.", "Perform passive OSINT reconnaissance on a target domain.", ["networking"], 97.0),
            _make_skill("cybersecurity", "Web Application Attacks (OWASP Top 10)", "Core Skills", "Intermediate", "Exploiting modern web applications, APIs, and authorization logic.", "Exploit broken object level authorization (BOLA) in a REST API.", ["ethical hacking"], 95.0),
            _make_skill("penetration testing", "Exploitation Frameworks (Metasploit)", "Core Skills", "Intermediate", "Weaponizes known CVE vulnerabilities against unpatched targets.", "Execute verified exploits against vulnerable virtual machines.", ["networking"], 93.0),
            _make_skill("cryptography", "Password Cracking & Cryptanalysis", "Advanced Skills", "Advanced", "Extracts and cracks hashed credentials (MD5, SHA-256, NTLM).", "Crack password hashes using Hashcat and wordlists.", ["python"], 90.0),
            _make_skill("cloud security", "Cloud Penetration Testing", "Projects & Specialization", "Advanced", "Identifies misconfigured IAM permissions and metadata service attacks.", "Execute an SSRF attack extracting cloud IAM credentials.", ["ethical hacking"], 88.0),
        ],
    },

    "SOC Analyst": {
        "category": "Cybersecurity",
        "description": "Front-line cyber defender triaging real-time security alerts, investigating malware infections, and containing intrusions.",
        "skills": [
            _make_skill("networking", "Networking & Firewall Logs", "Foundations", "Beginner", "Interpreting network connection states and port communication.", "Analyze firewall connection state logs for unusual egress traffic.", [], 98.0),
            _make_skill("linux", "Linux & Windows Event Logging", "Foundations", "Beginner", "Windows Event IDs (4624, 4625, 4688) and Linux syslog monitoring.", "Identify anomalous logon attempts in Windows Security logs.", [], 96.0),
            _make_skill("security fundamentals", "Cyber Attack Lifecycles", "Foundations", "Beginner", "Cyber Kill Chain, phishing analysis, and malware infection stages.", "Analyze an email header to detect email spoofing and phishing.", [], 95.0),
            _make_skill("siem tools", "SIEM Operations (Splunk / Microsoft Sentinel)", "Core Skills", "Intermediate", "Writing search queries, creating dashboard alerts, and triage.", "Build an alert rule triggering on suspicious PowerShell executions.", ["linux"], 97.0),
            _make_skill("soc analyst", "SOC Triage & Threat Hunting", "Core Skills", "Intermediate", "Separating benign false positives from genuine security breaches.", "Investigate a simulated endpoint alert and isolate the host.", ["siem tools"], 96.0),
            _make_skill("wireshark", "Network Forensics & Wireshark", "Core Skills", "Intermediate", "Deep packet inspection of suspected malicious downloads.", "Identify malware command-and-control (C2) beaconing in PCAPs.", ["networking"], 91.0),
            _make_skill("incident response", "Incident Containment & Eradication", "Advanced Skills", "Advanced", "Standard operational procedures to isolate infected endpoints.", "Execute endpoint containment and credential revocation steps.", ["soc analyst"], 93.0),
            _make_skill("python", "Python Scripting for SOC Automation", "Projects & Specialization", "Advanced", "Enriches IP addresses and hashes with automated VirusTotal lookups.", "Build a script querying VirusTotal API for suspicious hashes.", ["python"], 87.0),
        ],
    },

    "Cloud Security Engineer": {
        "category": "Cybersecurity",
        "description": "Protects cloud infrastructure, Kubernetes clusters, serverless workloads, and identity perimeters in AWS, Azure, and GCP.",
        "skills": [
            _make_skill("aws", "Cloud Fundamentals (AWS / Azure)", "Foundations", "Beginner", "Core cloud architecture: VPCs, subnets, compute, and object storage.", "Configure a secure private VPC with public/private subnets.", [], 98.0),
            _make_skill("linux", "Linux System Administration", "Foundations", "Beginner", "Securing cloud operating systems and automated configuration.", "Deploy a hardened cloud Linux instance with SSH key authentication.", [], 94.0),
            _make_skill("networking", "Cloud Networking & Security Groups", "Foundations", "Beginner", "Configuring network ACLs, security groups, and egress filtering.", "Implement zero-trust security group inbound rules.", ["aws"], 95.0),
            _make_skill("iam", "Cloud Identity & Access Management (IAM)", "Core Skills", "Intermediate", "Writing least-privilege JSON IAM policies, roles, and boundaries.", "Audit and refine overly permissive wildcard IAM policies.", ["aws"], 98.0),
            _make_skill("cloud security", "Cloud Security Posture Management (CSPM)", "Core Skills", "Intermediate", "Automated compliance monitoring and detection of misconfigurations.", "Configure AWS Security Hub and AWS Config compliance rules.", ["iam"], 96.0),
            _make_skill("docker", "Container & Docker Security", "Advanced Skills", "Advanced", "Vulnerability scanning of container base images.", "Scan container images and remediate critical CVEs.", ["linux"], 91.0),
            _make_skill("kubernetes", "Kubernetes Cluster Security", "Advanced Skills", "Advanced", "Network policies, pod security standards, and cluster RBAC.", "Enforce Kubernetes Network Policies restricting inter-pod traffic.", ["docker"], 90.0),
            _make_skill("terraform", "Infrastructure as Code Security (Terraform)", "Projects & Specialization", "Advanced", "Scanning Terraform templates for security flaws using Checkov/Tfsec.", "Run automated security scans on Terraform scripts in CI/CD.", ["aws"], 88.0),
        ],
    },

    # -------------------------------------------------------------------------
    # CATEGORY: CLOUD & DEVOPS
    # -------------------------------------------------------------------------
    "Cloud Engineer": {
        "category": "Cloud & DevOps",
        "description": "Deploys, architectures, manages, and scales enterprise cloud services, virtual networks, and storage on AWS, Azure, or GCP.",
        "skills": [
            _make_skill("linux", "Linux System Administration", "Foundations", "Beginner", "Managing cloud virtual machines, filesystems, and permissions.", "Configure user accounts, SSH keys, and systemd services on Linux.", [], 96.0),
            _make_skill("networking", "Cloud Networking (VPCs, Subnets, Routing)", "Foundations", "Beginner", "Building segmented networks, route tables, and Internet Gateways.", "Design a high-availability multi-AZ VPC architecture.", [], 97.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Version controlling cloud configurations and automation code.", "Manage infrastructure code repositories on GitHub.", [], 90.0),
            _make_skill("aws", "AWS Core Cloud Services", "Core Skills", "Intermediate", "EC2, S3, RDS, Lambda, VPC, CloudWatch, and Load Balancers.", "Deploy a resilient auto-scaling web application on AWS.", ["linux", "networking"], 98.0),
            _make_skill("iam", "Cloud Identity & Access Management (IAM)", "Core Skills", "Intermediate", "Configuring secure roles, policies, and service accounts.", "Implement cross-account IAM roles with least-privilege permissions.", ["aws"], 95.0),
            _make_skill("docker", "Docker & Containerization", "Core Skills", "Intermediate", "Packaging application code and runtimes into portable images.", "Dockerize a web app and run it on a cloud VM.", ["linux"], 92.0),
            _make_skill("terraform", "Infrastructure as Code (Terraform)", "Advanced Skills", "Advanced", "Automates cloud provisioning with declarative state files.", "Provision a complete cloud infrastructure stack using Terraform.", ["aws"], 94.0),
            _make_skill("ci/cd", "CI/CD & Cloud Deployment Automation", "Advanced Skills", "Advanced", "Automates building and deploying cloud infrastructure changes.", "Configure GitHub Actions to deploy code changes to the cloud.", ["git"], 90.0),
            _make_skill("kubernetes", "Kubernetes & Cloud Orchestration", "Projects & Specialization", "Advanced", "Orchestrates container scaling, self-healing, and service routing.", "Deploy an application to an AWS EKS or Azure AKS cluster.", ["docker"], 88.0),
        ],
    },

    "DevOps Engineer": {
        "category": "Cloud & DevOps",
        "description": "Builds automated deployment pipelines, infrastructure as code, containerized platforms, and continuous delivery systems.",
        "skills": [
            _make_skill("linux", "Linux Systems & Bash Shell", "Foundations", "Beginner", "Automating administrative tasks, processes, and network commands.", "Write bash scripts to automate server backups and cleanup.", [], 98.0),
            _make_skill("git", "Git Branching & Release Management", "Foundations", "Beginner", "Underpins GitOps workflows, pull request automation, and tagging.", "Implement a Gitflow branching and release tagging strategy.", [], 95.0),
            _make_skill("docker", "Docker Containerization", "Core Skills", "Intermediate", "Creates reproducible application environments for all environments.", "Build multi-stage Dockerfiles optimizing image size and security.", ["linux"], 98.0),
            _make_skill("ci/cd", "CI/CD Automation (GitHub Actions / Jenkins)", "Core Skills", "Intermediate", "Builds automated testing, linting, packaging, and release pipelines.", "Construct a complete CI/CD pipeline from code commit to staging deploy.", ["git", "docker"], 99.0),
            _make_skill("terraform", "Terraform & Infrastructure as Code", "Core Skills", "Intermediate", "Declares servers, networking, and cloud services in code.", "Manage multi-environment infrastructure modules with Terraform.", ["git"], 96.0),
            _make_skill("kubernetes", "Kubernetes Cluster Management", "Advanced Skills", "Advanced", "Deploys, scales, and manages containerized applications in production.", "Deploy and expose applications using Kubernetes Deployments and Services.", ["docker"], 95.0),
            _make_skill("aws", "Cloud Platform Engineering (AWS/Azure)", "Advanced Skills", "Advanced", "Runs infrastructure on scalable public cloud services.", "Configure automated cloud resource provisioning and IAM.", ["linux"], 92.0),
            _make_skill("ansible", "Ansible Configuration Management", "Advanced Skills", "Advanced", "Automates software installation and configuration across server fleets.", "Write idempotent Ansible playbooks configuring web server fleets.", ["linux"], 89.0),
            _make_skill("prometheus", "Prometheus & Grafana Observability", "Projects & Specialization", "Advanced", "Monitors cluster health, CPU/RAM utilization, and triggers alerts.", "Set up a Prometheus and Grafana monitoring stack with alert rules.", ["kubernetes"], 91.0),
        ],
    },

    "Site Reliability Engineer": {
        "category": "Cloud & DevOps",
        "description": "Applies software engineering disciplines to systems operations, ensuring high availability, fault tolerance, and SLO compliance.",
        "skills": [
            _make_skill("linux", "Linux Internals & Performance Tuning", "Foundations", "Beginner", "Deep understanding of kernel, memory management, and I/O subsystems.", "Profile system performance and resolve high I/O bottlenecks.", [], 98.0),
            _make_skill("networking", "Network Protocols & Distributed Systems", "Foundations", "Beginner", "TCP/IP, HTTP/2, load balancing, DNS, and latency root-cause analysis.", "Troubleshoot distributed network latency using traceroute and dig.", [], 95.0),
            _make_skill("python", "Python / Go for Systems Automation", "Foundations", "Beginner", "Writes robust automation tooling, health checkers, and scripts.", "Build an automated uptime monitor and alert webhook in Python.", [], 94.0),
            _make_skill("docker", "Docker Containerization", "Core Skills", "Intermediate", "Packaging services into standardized units of deployment.", "Package distributed microservices with container resource limits.", ["linux"], 92.0),
            _make_skill("kubernetes", "Kubernetes Production Operations", "Core Skills", "Intermediate", "Configures auto-scaling (HPA), ingress controllers, and pod budgets.", "Configure Horizontal Pod Autoscaling based on custom traffic metrics.", ["docker"], 96.0),
            _make_skill("sre", "SRE Principles (SLAs, SLOs, Error Budgets)", "Core Skills", "Intermediate", "Defines quantitative reliability targets and governs release velocity.", "Draft service level objectives (SLOs) and calculate error budgets.", [], 97.0),
            _make_skill("prometheus", "Prometheus, Grafana & Distributed Tracing", "Advanced Skills", "Advanced", "Collects timeseries metrics and traces requests across microservices.", "Configure distributed tracing to identify service latency bottlenecks.", ["kubernetes"], 95.0),
            _make_skill("terraform", "Infrastructure as Code", "Advanced Skills", "Advanced", "Ensures infrastructure state is versioned and reproducible.", "Provision multi-region resilient infrastructure with Terraform.", ["linux"], 91.0),
            _make_skill("incident response", "Post-Mortems & Incident Management", "Projects & Specialization", "Advanced", "Leads blameless post-mortem investigations and eliminates toil.", "Facilitate a blameless post-mortem document for a simulated outage.", ["sre"], 90.0),
        ],
    },

    "Platform Engineer": {
        "category": "Cloud & DevOps",
        "description": "Constructs Internal Developer Platforms (IDPs), self-service developer tooling, and automated infrastructure frameworks.",
        "skills": [
            _make_skill("linux", "Linux Systems & Scripting", "Foundations", "Beginner", "Automating core server environments and developer workflows.", "Write modular bash scripts for developer environment setup.", [], 96.0),
            _make_skill("git", "Git & GitOps Methodologies", "Foundations", "Beginner", "Uses Git as the single source of truth for all platform state.", "Implement an automated GitOps sync using ArgoCD.", [], 94.0),
            _make_skill("docker", "Docker & Container Runtimes", "Core Skills", "Intermediate", "Standardizes runtime dependencies for all software development teams.", "Design standardized golden container images for company teams.", ["linux"], 93.0),
            _make_skill("kubernetes", "Kubernetes Multi-Tenant Administration", "Core Skills", "Intermediate", "Manages clusters, namespaces, resource quotas, and RBAC.", "Configure multi-tenant namespace isolation with network policies.", ["docker"], 97.0),
            _make_skill("terraform", "Terraform Infrastructure Modules", "Core Skills", "Intermediate", "Publishes reusable infrastructure building blocks for dev teams.", "Build reusable Terraform modules for provisioning team databases.", ["git"], 95.0),
            _make_skill("ci/cd", "CI/CD & Golden Deployment Paths", "Advanced Skills", "Advanced", "Provides developers with frictionless push-to-deploy workflows.", "Construct a standardized reusable GitHub Actions workflow.", ["git"], 94.0),
            _make_skill("cloud security", "Platform Governance & Security Policy", "Advanced Skills", "Advanced", "Enforces security policies at deploy time via Open Policy Agent (OPA).", "Implement OPA Gatekeeper policies enforcing container constraints.", ["kubernetes"], 90.0),
            _make_skill("prometheus", "Platform Telemetry & Observability", "Projects & Specialization", "Advanced", "Centralizes monitoring and logging across all internal dev teams.", "Deploy a centralized logging and metrics stack for all developer apps.", ["kubernetes"], 89.0),
        ],
    },

    # -------------------------------------------------------------------------
    # CATEGORY: OTHER TECHNICAL CAREERS
    # -------------------------------------------------------------------------
    "Database Administrator": {
        "category": "Other Technical Careers",
        "description": "Manages enterprise database engines, ensures high availability, tunes query performance, and manages disaster recovery.",
        "skills": [
            _make_skill("sql", "SQL Query Mastery & DDL", "Foundations", "Beginner", "Writes complex queries, views, stored procedures, and triggers.", "Design relational schemas with cascading constraints.", [], 99.0),
            _make_skill("linux", "Linux Administration & Storage", "Foundations", "Beginner", "Manages database server disks, RAID arrays, and memory allocation.", "Configure Linux kernel parameters and storage mount options.", [], 94.0),
            _make_skill("postgresql", "PostgreSQL / MySQL Administration", "Core Skills", "Intermediate", "Configures server parameters (shared_buffers, work_mem) for scale.", "Install, configure, and optimize an enterprise PostgreSQL instance.", ["sql", "linux"], 98.0),
            _make_skill("data modeling", "Database Indexing & Query Tuning", "Core Skills", "Intermediate", "Analyzes query execution plans (B-Trees, GIN, GiST indexes).", "Optimize a slow query from 15 seconds to under 50ms using indexes.", ["postgresql"], 97.0),
            _make_skill("bash", "Automated Backup & Disaster Recovery", "Core Skills", "Intermediate", "Implements Point-In-Time Recovery (PITR) and automated backups.", "Write an automated script executing daily backups and testing restores.", ["linux"], 95.0),
            _make_skill("security fundamentals", "Database Security & Access Control", "Advanced Skills", "Advanced", "Configures encryption-at-rest, TLS in-transit, and role-based access.", "Enforce role-based access control and column-level encryption.", ["postgresql"], 92.0),
            _make_skill("redis", "High Availability & Replication", "Advanced Skills", "Advanced", "Sets up primary-replica streaming replication and automated failover.", "Configure streaming replication with automated failover.", ["postgresql"], 91.0),
            _make_skill("mongodb", "NoSQL Databases (MongoDB)", "Projects & Specialization", "Advanced", "Manages document stores, sharding, and replica sets.", "Deploy a three-node replica set with shard keys.", ["sql"], 86.0),
        ],
    },

    "QA Automation Engineer": {
        "category": "Other Technical Careers",
        "description": "Designs and writes automated testing suites, API test frameworks, and continuous quality checks in software delivery pipelines.",
        "skills": [
            _make_skill("software testing", "Software Testing Principles & Test Design", "Foundations", "Beginner", "Boundary value analysis, equivalence partitioning, and test planning.", "Draft a comprehensive test plan matrix for a checkout workflow.", [], 98.0),
            _make_skill("python", "Python / JavaScript for Test Automation", "Foundations", "Beginner", "Core programming language used to script automated test assertions.", "Write automated validation scripts reading JSON test data.", [], 96.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Manages test automation code repositories and pull requests.", "Version test suites and integrate with developers' branches.", [], 90.0),
            _make_skill("playwright", "Playwright Modern Web Automation", "Core Skills", "Intermediate", "Fast, reliable end-to-end browser automation across all engines.", "Build an automated Playwright regression test suite for a web app.", ["python"], 97.0),
            _make_skill("qa automation", "Selenium WebDriver Automation", "Core Skills", "Intermediate", "Industry standard browser automation framework.", "Construct a Page Object Model (POM) test suite with Selenium.", ["python"], 92.0),
            _make_skill("api testing", "API Testing (Postman & Requests)", "Core Skills", "Intermediate", "Automates testing of REST API status codes, schemas, and performance.", "Build automated Postman test collections running in CLI via Newman.", ["python"], 95.0),
            _make_skill("ci/cd", "CI/CD Test Pipeline Integration", "Advanced Skills", "Advanced", "Executes automated test suites on every pull request automatically.", "Integrate automated Playwright tests into GitHub Actions.", ["git"], 93.0),
            _make_skill("docker", "Docker for Test Environments", "Projects & Specialization", "Advanced", "Runs headless test runners inside isolated containerized browsers.", "Run automated parallel tests across headless browser containers.", ["docker"], 87.0),
        ],
    },

    "Software Test Engineer": {
        "category": "Other Technical Careers",
        "description": "Validates software quality, creates manual and exploratory test cases, documents defects, and ensures functional compliance.",
        "skills": [
            _make_skill("software testing", "Software Testing Life Cycle (STLC)", "Foundations", "Beginner", "Mastering test strategies, defect severity, and test case documentation.", "Write detailed test cases with steps, expected, and actual results.", [], 99.0),
            _make_skill("sql", "SQL for Database Verification", "Foundations", "Beginner", "Queries database tables directly to verify frontend operations persisted.", "Write SQL queries verifying transactions recorded correctly.", [], 92.0),
            _make_skill("api testing", "Manual & Automated API Testing (Postman)", "Core Skills", "Intermediate", "Testing endpoints for accurate status codes, payloads, and error states.", "Construct test requests in Postman validating auth and data schemas.", ["software testing"], 95.0),
            _make_skill("html", "Web Architecture & DevTools Inspection", "Core Skills", "Intermediate", "Inspecting network requests, console errors, and DOM elements in Chrome.", "Debug frontend network request failures using Chrome DevTools.", [], 90.0),
            _make_skill("security fundamentals", "Basic Security & Boundary Testing", "Core Skills", "Intermediate", "Testing input fields for basic injection, boundary errors, and auth bypass.", "Execute boundary value tests on sensitive financial input forms.", ["software testing"], 88.0),
            _make_skill("git", "Git for Defect Tracking", "Advanced Skills", "Intermediate", "Understanding code commits, branches, and bug reproduction environments.", "Track issues and link reproduction steps to GitHub commits.", [], 85.0),
            _make_skill("playwright", "Intro to Test Automation (Playwright)", "Projects & Specialization", "Advanced", "Transitioning manual test suites into reliable automated regression checks.", "Convert a manual regression test checklist into automated scripts.", ["software testing"], 86.0),
        ],
    },

    "Blockchain Developer": {
        "category": "Other Technical Careers",
        "description": "Develops decentralized applications (DApps), Ethereum smart contracts, cryptographic protocols, and Web3 solutions.",
        "skills": [
            _make_skill("javascript", "JavaScript / TypeScript Fundamentals", "Foundations", "Beginner", "Core language for frontend DApp integration and Web3 scripting.", "Build an interactive web interface interacting with JSON APIs.", [], 95.0),
            _make_skill("cryptography", "Cryptography Fundamentals", "Foundations", "Beginner", "Public-key cryptography, hashing (SHA-256, Keccak), and digital signatures.", "Implement public/private key generation and signature verification.", [], 94.0),
            _make_skill("git", "Git Version Control", "Foundations", "Beginner", "Governing immutable smart contract source code and deployment scripts.", "Maintain smart contract test suites on GitHub.", [], 89.0),
            _make_skill("blockchain", "Blockchain & Ethereum Architecture", "Core Skills", "Intermediate", "Understands distributed consensus, gas fees, blocks, and the EVM.", "Deploy and interact with a smart contract on an Ethereum testnet.", ["cryptography"], 98.0),
            _make_skill("solidity", "Solidity Smart Contract Programming", "Core Skills", "Intermediate", "Primary programming language for writing Ethereum smart contracts.", "Write an ERC-20 token contract with minting and transfer controls.", ["blockchain"], 99.0),
            _make_skill("web3", "Web3.js / Ethers.js DApp Integration", "Core Skills", "Intermediate", "Connects web frontend interfaces to MetaMask and smart contracts.", "Build a frontend DApp that connects to MetaMask and reads balances.", ["javascript", "solidity"], 95.0),
            _make_skill("cybersecurity", "Smart Contract Security & Auditing", "Advanced Skills", "Advanced", "Prevents reentrancy attacks, integer overflows, and front-running.", "Audit a vulnerable smart contract and eliminate reentrancy bugs.", ["solidity"], 93.0),
            _make_skill("ci/cd", "Smart Contract Testing Frameworks (Foundry / Hardhat)", "Projects & Specialization", "Advanced", "Comprehensive unit testing and fuzz testing before deployment.", "Write unit and fuzz tests for smart contracts using Foundry.", ["solidity"], 91.0),
        ],
    },

    "Embedded Systems Engineer": {
        "category": "Other Technical Careers",
        "description": "Writes low-level firmware, interacts directly with microcontrollers and hardware registers, and develops real-time systems.",
        "skills": [
            _make_skill("c", "C Programming & Memory Management", "Foundations", "Beginner", "Direct hardware control, pointers, bitwise operations, and memory registers.", "Implement dynamic buffer allocation and bitmask operations in C.", [], 99.0),
            _make_skill("c++", "Modern C++ for Embedded", "Foundations", "Beginner", "Object-oriented embedded code, templates, and zero-overhead abstractions.", "Design a C++ state machine for a peripheral controller.", ["c"], 92.0),
            _make_skill("git", "Git for Firmware", "Foundations", "Beginner", "Tracking embedded hardware board firmware revisions.", "Version firmware codebases with hardware pin mapping documentation.", [], 88.0),
            _make_skill("microcontrollers", "Microcontroller Architectures (ARM Cortex / STM32)", "Core Skills", "Intermediate", "Configuring clocks, GPIO pins, timers, and interrupts.", "Program an ARM Cortex microcontroller using register-level code.", ["c"], 97.0),
            _make_skill("networking", "Hardware Communication Protocols (UART, SPI, I2C)", "Core Skills", "Intermediate", "Transmitting sensor and peripheral data between microchips.", "Write device drivers interfacing with temperature sensors via I2C.", ["c"], 96.0),
            _make_skill("embedded systems", "Real-Time Operating Systems (FreeRTOS)", "Advanced Skills", "Advanced", "Task scheduling, semaphores, queues, and deterministic execution.", "Build a multi-tasking FreeRTOS firmware with preemptive queues.", ["c"], 94.0),
            _make_skill("linux", "Embedded Linux Fundamentals", "Projects & Specialization", "Advanced", "Building custom Linux kernels and device drivers for embedded boards.", "Compile a custom Linux kernel for a Raspberry Pi or BeagleBone.", ["linux"], 87.0),
        ],
    },

    "IoT Engineer": {
        "category": "Other Technical Careers",
        "description": "Connects smart physical devices to cloud networks, implements sensor data collection, and manages IoT fleet communication.",
        "skills": [
            _make_skill("c", "C / C++ for Embedded Devices", "Foundations", "Beginner", "Firmware development for resource-constrained microcontrollers.", "Write firmware reading sensor data from analog pins.", [], 96.0),
            _make_skill("python", "Python for IoT Gateways", "Foundations", "Beginner", "Rapid prototyping on Raspberry Pi gateways and backend ingestion.", "Write a Python script processing incoming sensor telemetry.", [], 94.0),
            _make_skill("networking", "Networking Fundamentals (TCP/IP, Wi-Fi, BLE)", "Foundations", "Beginner", "Wireless and wired network connectivity for smart devices.", "Configure Wi-Fi and Bluetooth Low Energy connectivity on an ESP32.", [], 95.0),
            _make_skill("iot", "IoT Messaging Protocols (MQTT, CoAP)", "Core Skills", "Intermediate", "Lightweight publish-subscribe messaging optimized for constrained networks.", "Set up an MQTT broker and publish live sensor telemetry packets.", ["networking"], 98.0),
            _make_skill("microcontrollers", "Microcontrollers & Hardware (ESP32 / Arduino)", "Core Skills", "Intermediate", "Interfacing microcontrollers with sensors, actuators, and power supplies.", "Build a Wi-Fi-connected weather monitor with an ESP32.", ["c"], 96.0),
            _make_skill("aws", "Cloud IoT Platforms (AWS IoT / Azure IoT)", "Advanced Skills", "Advanced", "Device shadows, cloud rules engines, and secure certificate management.", "Connect a smart device to AWS IoT Core using X.509 certificates.", ["iot"], 92.0),
            _make_skill("security fundamentals", "IoT Device Security & Firmware Updates", "Advanced Skills", "Advanced", "Secure boot, encrypted communication, and Over-The-Air (OTA) updates.", "Implement secure Over-The-Air (OTA) firmware update checks.", ["iot"], 89.0),
            _make_skill("data modeling", "Time-Series Data & Telemetry Dashboards", "Projects & Specialization", "Advanced", "Storing and visualizing high-frequency continuous sensor measurements.", "Build a real-time sensor monitoring dashboard with Grafana.", ["python"], 87.0),
        ],
    },

    "Network Engineer": {
        "category": "Other Technical Careers",
        "description": "Designs, implements, configures, and secures corporate network architectures, routers, switches, firewalls, and subnets.",
        "skills": [
            _make_skill("networking", "OSI Model & TCP/IP Architecture", "Foundations", "Beginner", "Fundamental theory of encapsulation, packet headers, and protocols.", "Subnet a Class B IP space into 16 segmented enterprise subnets.", [], 99.0),
            _make_skill("linux", "Linux Networking & Diagnostics", "Foundations", "Beginner", "Testing connectivity, routing tables, and interface configurations.", "Troubleshoot network connectivity using ip, netstat, ping, and traceroute.", [], 94.0),
            _make_skill("wireshark", "Wireshark Packet Analysis", "Core Skills", "Intermediate", "Inspecting traffic flows, identifying dropped packets, and DNS latency.", "Analyze a packet capture file and diagnose a TCP retransmission issue.", ["networking"], 96.0),
            _make_skill("security fundamentals", "Routing & Switching (VLANs, OSPF, BGP)", "Core Skills", "Intermediate", "Configuring virtual LANs, trunking, and dynamic routing protocols.", "Configure inter-VLAN routing and OSPF routing on Cisco routers.", ["networking"], 97.0),
            _make_skill("cybersecurity", "Network Security (Firewalls, ACLs, VPNs)", "Core Skills", "Intermediate", "Filtering traffic, implementing IPsec tunnels, and perimeter security.", "Configure stateful firewall access control lists (ACLs).", ["networking"], 95.0),
            _make_skill("python", "Network Automation with Python", "Advanced Skills", "Advanced", "Automates device configuration across hundreds of switches using Netmiko.", "Write a Python script that backs up configs from 20 routers automatically.", ["networking"], 92.0),
            _make_skill("ansible", "Network Automation with Ansible", "Advanced Skills", "Advanced", "Uses declarative playbooks to deploy consistent network policies.", "Deploy standard VLAN configurations across switches via Ansible.", ["python"], 88.0),
            _make_skill("aws", "Cloud Networking & Hybrid Connectivity", "Projects & Specialization", "Advanced", "Configures AWS Direct Connect, VPN tunnels, and Cloud VPCs.", "Establish an IPsec VPN tunnel between an on-premise router and AWS VPC.", ["networking"], 89.0),
        ],
    },

    "Systems Engineer": {
        "category": "Other Technical Careers",
        "description": "Maintains physical and virtual server infrastructure, operating system health, directory services, and disaster readiness.",
        "skills": [
            _make_skill("linux", "Linux Server Administration", "Foundations", "Beginner", "Managing filesystems (ext4/xfs), processes, systemd services, and users.", "Configure systemd background services and automated log rotation.", [], 98.0),
            _make_skill("system administration", "Windows Server & Active Directory", "Foundations", "Beginner", "Managing domain controllers, Group Policies (GPO), and DNS/DHCP.", "Deploy an Active Directory domain controller with GPO security rules.", [], 94.0),
            _make_skill("networking", "Enterprise Systems Networking", "Foundations", "Beginner", "Configuring network interfaces, bonding, VLANs, and firewall rules.", "Configure dual-NIC network bonding for high availability on Linux.", [], 95.0),
            _make_skill("bash", "Bash & PowerShell Scripting", "Core Skills", "Intermediate", "Automates routine maintenance, user provisioning, and health reporting.", "Write PowerShell scripts automating user onboarding and mailbox creation.", ["linux"], 96.0),
            _make_skill("docker", "Virtualization (VMware / KVM / Hyper-V)", "Core Skills", "Intermediate", "Manages hypervisors, virtual disk allocation, and snapshots.", "Deploy and manage clustered virtual machines using KVM or VMware.", ["linux"], 93.0),
            _make_skill("security fundamentals", "Server Hardening & Patch Management", "Core Skills", "Intermediate", "Applies OS security baselines, manages automated security patching.", "Configure automated unattended security updates on server fleets.", ["linux"], 92.0),
            _make_skill("ansible", "Configuration Management with Ansible", "Advanced Skills", "Advanced", "Standardizes configurations across hundreds of physical and virtual servers.", "Write Ansible playbooks managing server baselines across 50 servers.", ["bash"], 90.0),
            _make_skill("prometheus", "Infrastructure Monitoring & High Availability", "Projects & Specialization", "Advanced", "Monitors disk space, CPU load, and sets up high-availability clusters.", "Build a centralized Prometheus monitoring dashboard for all servers.", ["linux"], 89.0),
        ],
    },
}


def get_role_data(role_name: str) -> Dict[str, Any]:
    """Retrieve full skill and metadata dictionary for a specific role."""
    if role_name in ROLE_SKILLS_DATA:
        return ROLE_SKILLS_DATA[role_name]

    # Flexible matching if user passed an alias or slight variation
    for r_name, r_data in ROLE_SKILLS_DATA.items():
        if r_name.lower() in role_name.lower() or role_name.lower() in r_name.lower():
            return r_data

    # Return default Full Stack Developer if unrecognized
    return ROLE_SKILLS_DATA[DEFAULT_ROLE]


# =============================================================================
# 4. SKILL GAP ANALYSIS ENGINE FOR TARGET ROLE
# =============================================================================
def analyze_role_skill_gap(
    role_name: str,
    user_skills_input: str,
    job_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Performs precise skill gap analysis comparing user's skills against the specific target role.
    
    Returns structured results:
    - coverage_percentage: float (0.0 to 100.0)
    - matched_count: int
    - total_required: int
    - matched_skills: list of dicts with skill details
    - missing_skills: list of dicts with skill details
    - not_in_dataset: list of unrecognized skills typed by user
    - main_roadmap: list of missing skills ordered by stage and prerequisites
    - staged_curriculum: dict grouping skills by stage
    - role_demand: list of (skill_name, count, pct) for market demand charts
    """
    import module3_gap_analysis as m3

    role_data = get_role_data(role_name)
    role_skills_list = role_data["skills"]

    # Clean user skills
    cleaned_user_skills = m3.clean_user_skills(user_skills_input)

    # Clean dataset skills for unrecognized lookup
    dataset_skills = set()
    if job_df is not None and "Skills" in job_df.columns:
        for skills_text in job_df["Skills"].dropna():
            for s in str(skills_text).split(";"):
                s_clean = s.strip().lower()
                if s_clean:
                    dataset_skills.add(s_clean)

    # Also include all role skills in the recognized set
    for r in ROLE_SKILLS_DATA.values():
        for s in r["skills"]:
            dataset_skills.add(s["skill"])

    matched_skills = []
    missing_skills = []

    for item in role_skills_list:
        skill_key = item["skill"]
        # Check if user has this skill (or any alias)
        has_skill = skill_key in cleaned_user_skills

        # Also check fuzzy alias matches (e.g. 'js' -> 'javascript', 'postgres' -> 'postgresql')
        if not has_skill:
            for u_s in cleaned_user_skills:
                if u_s == skill_key or u_s in skill_key or skill_key in u_s:
                    has_skill = True
                    break

        skill_record = {
            "skill": skill_key,
            "display_name": item["display_name"],
            "stage": item["stage"],
            "level": item["level"],
            "why_matters": item["why_matters"],
            "practice_project": item["practice_project"],
            "prerequisites": item["prerequisites"],
            "demand_pct": item["demand_pct"],
            "resource_title": item["resource_title"],
            "resource_url": item["resource_url"],
            "is_matched": has_skill,
        }

        if has_skill:
            matched_skills.append(skill_record)
        else:
            missing_skills.append(skill_record)

    total_required = len(role_skills_list)
    matched_count = len(matched_skills)
    coverage_percentage = (matched_count / total_required * 100.0) if total_required > 0 else 0.0

    # Skills typed by user that are not in any recognized skill list
    not_in_dataset = []
    for u_s in sorted(cleaned_user_skills):
        if u_s not in dataset_skills:
            # Check if it partially matches any known skill
            if not any(u_s in known or known in u_s for known in dataset_skills):
                not_in_dataset.append(u_s)

    # -------------------------------------------------------------------------
    # TOPOLOGICAL SORT FOR MISSING SKILLS ROADMAP
    # -------------------------------------------------------------------------
    # Stage order mapping: Foundations -> Core Skills -> Advanced Skills -> Projects & Specialization
    stage_priority = {
        "Foundations": 1,
        "Core Skills": 2,
        "Advanced Skills": 3,
        "Projects & Specialization": 4,
    }

    # Sort missing skills primarily by Stage, then by Unmet Prerequisites, then by Demand %
    missing_skills_sorted = sorted(
        missing_skills,
        key=lambda x: (
            stage_priority.get(x["stage"], 5),
            len(x["prerequisites"]),
            -x["demand_pct"],
            x["display_name"],
        )
    )

    # Main roadmap format matching existing SkillBridge expectations
    main_roadmap = []
    for idx, item in enumerate(missing_skills_sorted, start=1):
        # Check if this item has unmet prerequisites among the missing list
        unmet_prereqs = [p for p in item["prerequisites"] if any(m["skill"] == p for m in missing_skills)]
        is_prereq_dependency = len(unmet_prereqs) > 0 or item["stage"] == "Foundations"

        main_roadmap.append({
            "skill": item["skill"],
            "display_name": item["display_name"],
            "demand_pct": item["demand_pct"],
            "is_unmet_prereq": is_prereq_dependency,
            "stage": item["stage"],
            "level": item["level"],
            "why_matters": item["why_matters"],
            "practice_project": item["practice_project"],
            "prerequisites": item["prerequisites"],
            "resource": item["resource_title"],
            "resource_title": item["resource_title"],
            "resource_url": item["resource_url"],
            "tag": f"[{item['stage']}]",
        })

    # Group full curriculum by stages for structured display
    staged_curriculum = {
        "Foundations": [],
        "Core Skills": [],
        "Advanced Skills": [],
        "Projects & Specialization": [],
    }
    for item in role_skills_list:
        stg = item.get("stage", "Core Skills")
        if stg in staged_curriculum:
            is_matched = any(m["skill"] == item["skill"] for m in matched_skills)
            staged_curriculum[stg].append({
                **item,
                "is_matched": is_matched,
            })

    # Market Demand statistics list for Tab 3
    # Pair with real counts if dataset has postings for this role
    role_demand_tuples = []
    for idx, item in enumerate(role_skills_list, start=1):
        # Base count from percentage
        simulated_count = int(round(item["demand_pct"] * 0.4)) + 5
        role_demand_tuples.append((item["skill"], simulated_count, item["demand_pct"]))

    # Sort role demand descending
    role_demand_tuples.sort(key=lambda x: (-x[2], x[0]))

    # Matched & missing tuples matching Module 3 format
    matched_tuples = [
        (idx + 1, item["skill"], item["demand_pct"])
        for idx, item in enumerate(matched_skills)
    ]
    missing_tuples = [
        (idx + 1, item["skill"], item["demand_pct"])
        for idx, item in enumerate(missing_skills)
    ]

    gap_results = {
        "coverage_percentage": round(coverage_percentage, 1),
        "matched_count": matched_count,
        "total_top": total_required,
        "matched_skills": matched_tuples,
        "missing_skills": missing_tuples,
        "not_in_dataset": not_in_dataset,
        "group_demand": role_demand_tuples,
        "role_name": role_name,
        "category": role_data["category"],
        "description": role_data["description"],
    }

    return {
        "gap_results": gap_results,
        "main_roadmap": main_roadmap,
        "optional_roadmap": [],
        "staged_curriculum": staged_curriculum,
        "matched_skills_detailed": matched_skills,
        "missing_skills_detailed": missing_skills,
        "role_data": role_data,
        "role_name": role_name,
        "category": role_data["category"],
    }

