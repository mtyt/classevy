# A very simple Flask Hello World app for you to get started with...

import os
from flask import (
    Flask,
    flash,
    request,
    redirect,
    send_from_directory,
    render_template,
)
from werkzeug.utils import secure_filename
from classevy.klas import StudentGroup, PlanPopulation


UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def import_csv(file):
    df = StudentGroup(file)
    return df


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # return redirect(url_for('download_file', name=filename))
            global STUDENTS
            STUDENTS = import_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return render_template(
                "table.html",
                tables=[STUDENTS.to_html(classes="data")],
                titles=STUDENTS.columns.values,
                page_restart="/",
                page_read="/read",
            )

    return render_template("forms.html", page_restart=request.url)


@app.route('/read')
def read():
    global pop
    pop = PlanPopulation(
        STUDENTS,
        20,
        2,
    )
    default_goals = pop.default_goals_dict
    options = {op.replace(' ','_').lower():op + ': ' + val for op, val in default_goals.items()}
    return render_template('read.html', page_restart='/', page_start='/start', options=options)


@app.route("/start")
def start():
    return render_template("running.html", run_page='run', done_page='done')


@app.route("/run")
def run_algo():
    # filename = os.path.join(app.config["UPLOAD_FOLDER"], "students.csv")  # hard-coded
    # students = StudentGroup(filename)
    pop.run(n_gen=2, verbose=True)
    front = pop.pareto()
    front["sum"] = sum([front[col] for col in pop.goals_names])
    best_plan = front.sort_values("sum").iloc[0].values[0]
    global BEST_PLAN
    BEST_PLAN = best_plan.students
    return "Done"


@app.route("/done")
def present_result():
    return render_template(
        "table.html",
        tables=[BEST_PLAN.to_html(classes="data")],
        titles=BEST_PLAN.columns.values,
        page_restart="/",
    )


@app.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
