import os,re,sqlite3
from datetime import date
from flask import Flask,request,redirect,url_for,render_template,flash
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from docx import Document

BASE=os.path.dirname(os.path.abspath(__file__))
UPLOADS=os.path.join(BASE,"uploads"); DB=os.path.join(BASE,"data","gaplens.db")
os.makedirs(UPLOADS,exist_ok=True); os.makedirs(os.path.dirname(DB),exist_ok=True)
app=Flask(__name__); app.secret_key=os.environ.get("SECRET_KEY","change-this-before-deployment")
app.config["MAX_CONTENT_LENGTH"]=8*1024*1024
SKILLS=["python","java","javascript","sql","html","css","flask","django","react","node.js","machine learning","deep learning","data analysis","pandas","numpy","matplotlib","scikit-learn","tensorflow","pytorch","git","github","rest api","communication","problem solving","excel","power bi","tableau","statistics","aws","docker","linux","data structures","algorithms","prompt engineering","nlp","computer vision","project management","agile"]
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 with conn() as c:
  c.execute("CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY,company TEXT,role TEXT,status TEXT,applied_on TEXT,notes TEXT)")
  c.execute("CREATE TABLE IF NOT EXISTS interview_scores(id INTEGER PRIMARY KEY,role TEXT,question TEXT,relevance INTEGER,accuracy INTEGER,evidence INTEGER,clarity INTEGER)")
def extract(path):
 if path.lower().endswith(".pdf"):
  return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
 return "\n".join(p.text for p in Document(path).paragraphs)
def skills(text):
 t=text.lower()
 return sorted(s for s in SKILLS if re.search(r"(?<![a-z0-9])"+re.escape(s)+r"(?![a-z0-9])",t))
def analyze(resume,jd):
 have=skills(resume); need=skills(jd); matched=[s for s in need if s in have]; missing=[s for s in need if s not in have]
 return {"resume_skills":have,"required_skills":need,"matched_skills":matched,"missing_skills":missing,"match_score":round(len(matched)*100/len(need)) if need else 0}
RESOURCE_MAP = {
 "python": ("Python Tutorial", "https://docs.python.org/3/tutorial/", "Write a script that reads a CSV file, cleans missing values and prints a summary."),
 "java": ("Java Tutorials", "https://dev.java/learn/", "Create a console-based student grade manager using classes and collections."),
 "javascript": ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "Build a searchable task list with add, complete and filter actions."),
 "sql": ("SQLBolt interactive lessons", "https://sqlbolt.com/", "Create tables for companies and applications; write SELECT, JOIN, GROUP BY and ORDER BY queries."),
 "html": ("MDN HTML", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content", "Build an accessible multi-section portfolio page using semantic HTML."),
 "css": ("MDN CSS", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics", "Style the portfolio page with responsive layouts, reusable colors and clear typography."),
 "flask": ("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/", "Build a Flask app with a form, two routes and server-side validation."),
 "django": ("Django Getting Started", "https://docs.djangoproject.com/en/stable/intro/", "Create a small CRUD app for tracking learning tasks."),
 "react": ("React Learn", "https://react.dev/learn", "Build a component-based dashboard with a filterable list and form state."),
 "node.js": ("Node.js Learn", "https://nodejs.org/en/learn", "Create a small Node.js server with two JSON endpoints."),
 "machine learning": ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course", "Train a simple classification model on a public beginner dataset and record its evaluation metrics."),
 "deep learning": ("PyTorch Tutorials", "https://pytorch.org/tutorials/", "Follow a beginner tensor and neural-network tutorial; document the model inputs and outputs."),
 "data analysis": ("Kaggle Learn: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning", "Clean a small public dataset and write five evidence-based observations."),
 "pandas": ("pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/index.html", "Load a CSV, filter rows, group by a category and export a summary."),
 "numpy": ("NumPy Learn", "https://numpy.org/learn/", "Create arrays and calculate mean, minimum, maximum and standard deviation."),
 "matplotlib": ("Matplotlib Tutorials", "https://matplotlib.org/stable/tutorials/", "Create a labelled line chart and bar chart from a small dataset."),
 "scikit-learn": ("scikit-learn Getting Started", "https://scikit-learn.org/stable/getting_started.html", "Train a baseline model, split data into train/test sets and report one metric."),
 "tensorflow": ("TensorFlow Tutorials", "https://www.tensorflow.org/tutorials", "Run a beginner classification tutorial and explain its evaluation output."),
 "pytorch": ("PyTorch Tutorials", "https://pytorch.org/tutorials/", "Build a small tensor workflow and run a beginner model tutorial."),
 "git": ("Git Book", "https://git-scm.com/book/en/v2", "Create a repository, make three meaningful commits and practice branching and merging."),
 "github": ("GitHub Skills", "https://skills.github.com/", "Complete an introductory GitHub Skills course and open a practice pull request."),
 "rest api": ("MDN: HTTP overview", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "Create or test a JSON endpoint; document GET/POST requests and status codes."),
 "communication": ("University of Minnesota: Communication", "https://open.lib.umn.edu/communication/", "Record a 90-second explanation of one project using problem, action and result."),
 "problem solving": ("HackerRank Problem Solving", "https://www.hackerrank.com/domains/algorithms", "Solve two beginner problems and write down the approach and complexity."),
 "excel": ("Microsoft Excel Help", "https://support.microsoft.com/excel", "Create a spreadsheet with filters, formulas, conditional formatting and a pivot table."),
 "power bi": ("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/", "Import a sample dataset and build a report with three visuals and one slicer."),
 "tableau": ("Tableau Free Training", "https://www.tableau.com/learn/training", "Create a simple interactive dashboard with two charts and a filter."),
 "statistics": ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "Calculate mean, median and spread for a dataset and explain what each tells you."),
 "aws": ("AWS Skill Builder", "https://skillbuilder.aws/", "Complete an introductory cloud module and draw a basic architecture diagram."),
 "docker": ("Docker Get Started", "https://docs.docker.com/get-started/", "Containerize a small sample web app and document how to run it."),
 "linux": ("Linux Journey", "https://linuxjourney.com/", "Practice file navigation, permissions and basic process commands in a safe local environment."),
 "data structures": ("VisuAlgo", "https://visualgo.net/en", "Trace array, stack, queue and hash-table operations; implement one structure."),
 "algorithms": ("VisuAlgo", "https://visualgo.net/en", "Implement linear search and binary search; compare their time complexity."),
 "prompt engineering": ("OpenAI Prompt Engineering Guide", "https://platform.openai.com/docs/guides/prompt-engineering", "Write three versions of a prompt for one task and compare output quality using a fixed rubric."),
 "nlp": ("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course", "Run a basic text-classification pipeline and inspect a few predictions."),
 "computer vision": ("OpenCV Tutorials", "https://docs.opencv.org/4.x/d9/df8/tutorial_root.html", "Load an image, resize it, convert color spaces and document the transformations."),
 "project management": ("Atlassian Agile Coach", "https://www.atlassian.com/agile", "Break a small project into user stories, priorities and a one-week sprint board."),
 "agile": ("Atlassian Agile Coach", "https://www.atlassian.com/agile", "Write five user stories, estimate effort and run a short retrospective.")
}

PROJECT_MAP = {
 "sql": ("Job Application Analytics Dashboard", "A dashboard that turns application records into useful job-search insights.", ["Store company, role, date and status in relational tables", "Write JOIN, GROUP BY and filtering queries", "Show applications by status and weekly activity"], "SQL: schema design, joins, aggregation and filtering"),
 "rest api": ("Career Opportunities API", "A small API for managing target roles, job posts and application records.", ["Create GET and POST endpoints", "Validate request data and return useful status codes", "Document endpoints with example JSON"], "REST API: endpoints, HTTP methods, JSON and validation"),
 "javascript": ("Interactive Career Roadmap", "A browser-based roadmap where users can check off weekly learning tasks.", ["Add and complete tasks interactively", "Filter tasks by status or week", "Save progress in browser storage"], "JavaScript: DOM, events, arrays and state"),
 "python": ("Resume Skill Extractor", "A Python utility that extracts text and reports recognized skills from a resume.", ["Read PDF or DOCX text", "Normalize and identify skills", "Export a structured JSON report"], "Python: file handling, functions, parsing and data structures"),
 "flask": ("Learning Progress Tracker", "A small web app to record skills, weekly goals and completion evidence.", ["Build Flask routes and forms", "Validate input and save records in SQLite", "Display progress on a dashboard"], "Flask: routing, templates, forms and database integration"),
 "html": ("Career Portfolio Website", "A responsive portfolio that presents projects, skills and learning milestones.", ["Use semantic page sections", "Add project cards and contact details", "Make navigation keyboard-friendly"], "HTML: semantic structure and accessible content"),
 "css": ("Responsive Portfolio UI", "A polished portfolio interface that adapts to phone and desktop screens.", ["Create responsive layouts", "Use consistent spacing and typography", "Add accessible hover and focus states"], "CSS: layout, responsive design and visual hierarchy"),
 "git": ("Collaborative Project Workflow Demo", "A sample project showing a clean version-control workflow.", ["Create feature branches", "Make focused commits", "Resolve a practice merge conflict and document the process"], "Git: commits, branches, merges and collaboration"),
 "github": ("Open-Source Contribution Portfolio", "A repository that demonstrates project documentation and contribution workflow.", ["Write a useful README", "Create issues and project milestones", "Submit a pull request in a practice repository"], "GitHub: repositories, issues, pull requests and documentation"),
 "pandas": ("Student Performance Insights", "An analysis project that explores a public student-performance dataset.", ["Clean missing or inconsistent values", "Group and summarize performance data", "Export a concise findings report"], "Pandas: DataFrames, cleaning, grouping and aggregation"),
 "data analysis": ("Public Dataset Storyboard", "A reproducible analysis that answers a focused question using public data.", ["Choose a documented public dataset", "Clean and summarize the data", "Present three findings supported by charts"], "Data analysis: cleaning, exploration and evidence-based insights"),
 "power bi": ("Job Market Skills Dashboard", "A dashboard that summarizes skills from a collected set of job descriptions.", ["Prepare a tidy skills dataset", "Build role and skill charts", "Add filters for role and experience level"], "Power BI: data modelling, visuals and filters"),
 "machine learning": ("Entry-Level Role Matcher", "A learning prototype that compares a profile with role descriptions using a simple baseline model.", ["Prepare a small labelled dataset", "Train and evaluate a baseline classifier", "Explain limitations and possible bias"], "Machine learning: features, train/test split and evaluation"),
 "data structures": ("Algorithm Visualizer", "A visual demo that explains how common data structures behave.", ["Demonstrate stack and queue operations", "Show array search steps", "Explain operation costs"], "Data structures: arrays, stacks, queues and complexity"),
 "algorithms": ("Algorithm Challenge Notebook", "A collection of solved beginner problems with explanations and complexity notes.", ["Solve search and sorting tasks", "Compare two approaches", "Document time and space complexity"], "Algorithms: searching, sorting and complexity"),
 "communication": ("Project Demo Storyboard", "A concise presentation that explains a project to a non-technical audience.", ["Define the user problem", "Explain the solution with a simple diagram", "Present measurable results and lessons learned"], "Communication: structure, clarity and audience awareness")
}

def make_plan(missing):
    selected = missing[:8] or ["python", "project management"]
    plan = []
    for i, skill in enumerate(selected):
        title, url, exercise = RESOURCE_MAP.get(
            skill, ("Official documentation search", "https://www.google.com/search?q="+skill.replace(" ","+")+"+official+documentation",
                    f"Complete one beginner exercise using {skill} and write down the steps and result.")
        )
        plan.append({
            "week": i + 1, "skill": skill, "resource_name": title,
            "resource_url": url, "exercise": exercise,
            "milestone": f"By the end of week {i+1}, complete the exercise and save a working example or short evidence note for {skill}."
        })
    return plan

def make_projects(missing, role):
    selected = missing[:5]
    projects = []
    seen = set()
    for skill in selected:
        if skill in PROJECT_MAP:
            title, summary, features, addresses = PROJECT_MAP[skill]
        else:
            title = f"{skill.title()} Mini Case Study"
            summary = f"A focused, demonstrable mini-project applying {skill} to a realistic {role} task."
            features = [f"Define a realistic problem involving {skill}", "Build a small working solution", "Document the approach, result and limitations"]
            addresses = f"{skill}: practical application and evidence"
        if title not in seen:
            projects.append({"title": title, "summary": summary, "features": features, "addresses": addresses})
            seen.add(title)
    if not projects:
        projects.append({
            "title": f"{role.title()} Portfolio Case Study",
            "summary": f"An end-to-end project demonstrating the core responsibilities of a {role}.",
            "features": ["Define a user problem and success criteria", "Build and document a working prototype", "Present a short demo and lessons learned"],
            "addresses": "Role-specific skills and project communication"
        })
    return projects

@app.route("/",methods=["GET","POST"])
def index():
 if request.method=="POST":
  f=request.files.get("resume"); role=request.form.get("target_role","").strip(); jd=request.form.get("job_description","").strip()
  if not f or not f.filename or not role or not jd: flash("Provide a resume, target role and job description.","error"); return redirect(url_for("index"))
  ext=os.path.splitext(f.filename)[1].lower()
  if ext not in [".pdf",".docx"]: flash("Only PDF and DOCX files are supported.","error"); return redirect(url_for("index"))
  path=os.path.join(UPLOADS,secure_filename(f.filename)); f.save(path)
  try: text=extract(path)
  except Exception as e: flash("Resume could not be read: "+str(e),"error"); return redirect(url_for("index"))
  if not text.strip(): flash("No readable text found. Try a text-based PDF or DOCX.","error"); return redirect(url_for("index"))
  result=analyze(text,jd); missing=result["missing_skills"]
  projects=make_projects(missing, role)
  return render_template("results.html",role=role,a=result,plan=make_plan(missing),projects=projects)
 return render_template("index.html")
@app.route("/tracker",methods=["GET","POST"])
def tracker():
 if request.method=="POST":
  with conn() as c: c.execute("INSERT INTO applications(company,role,status,applied_on,notes) VALUES(?,?,?,?,?)",(request.form["company"],request.form["role"],request.form["status"],request.form.get("applied_on",""),request.form.get("notes","")))
  flash("Application saved.","success"); return redirect(url_for("tracker"))
 with conn() as c: rows=c.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
 return render_template("tracker.html",rows=rows,today=date.today().isoformat())
@app.route("/interview",methods=["GET","POST"])
def interview():
 qs=["Describe a project relevant to your target role.","Explain a technical challenge and how you solved it.","Which skill gap are you working to close, and how?","How would you approach a typical task in this role?"]
 if request.method=="POST":
  try: vals=[int(request.form[k]) for k in ["relevance","accuracy","evidence","clarity"]]; assert all(1<=v<=5 for v in vals)
  except: flash("Select a score from 1 to 5 for each rubric category.","error"); return redirect(url_for("interview"))
  with conn() as c: c.execute("INSERT INTO interview_scores(role,question,relevance,accuracy,evidence,clarity) VALUES(?,?,?,?,?,?,?)".replace("VALUES(?,?,?,?,?,?,?)","VALUES(?,?,?,?,?,?)"),(request.form["role"],request.form["question"],*vals))
  flash(f"Self-assessment saved: {sum(vals)}/20.","success"); return redirect(url_for("interview"))
 with conn() as c: scores=c.execute("SELECT * FROM interview_scores ORDER BY id DESC LIMIT 10").fetchall()
 return render_template("interview.html",questions=qs,scores=scores)
@app.get("/health")
def health(): return {"status":"ok","application":"GapLens AI"}
@app.errorhandler(413)
def too_large(e): flash("Maximum upload size is 8 MB.","error"); return redirect(url_for("index"))
if __name__=="__main__": init_db(); app.run(host="127.0.0.1",port=int(os.environ.get("PORT",5000)),debug=False)
