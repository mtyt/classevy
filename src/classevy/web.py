# A very simple Flask Hello World app for you to get started with...

import os
from flask import (
    Flask,
    flash,
    request,
    redirect,
    send_from_directory,
    render_template,
    url_for
)
from werkzeug.utils import secure_filename
from classevy.klas import StudentGroup, PlanPopulation
import pandas as pd


UPLOAD_FOLDER = "/Users/mtytgat/code/classevy/data"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DATA_FOLDER"] = UPLOAD_FOLDER
app.add_url_rule(
    "/data/<name>", endpoint="download_file", build_only=True
)


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
            STUDENTS.index.names = [None]  # to remove empty row when displaying
            return redirect(url_for('read'))

    return render_template("forms.html")


@app.route("/read", methods=["GET", "POST"])
def read():
    global pop
    pop = PlanPopulation(
        STUDENTS,
        20,
        2,
    )
    default_goals = pop.default_goals_dict
    # create a dict to pass to the html template.
    # the keys are valid variable names (without spaces) and the values are strings
    # that combine the default goals key + value, like "spread_score: min"
    options = {
        op.replace(" ", "_").lower(): op + ": " + val
        for op, val in default_goals.items()
    }
    if request.method == "POST":
        # obtain the values from the checkboxes:
        input_dict = {}
        for op in options:
            input_dict[op] = request.form.get(
                op
            )  # looks like {spread_score:spread_score, spread_size:None}
            # temp_string = ', '.join([': '.join([key, str(val)]) for key, val in
            # input_dict.items()])
            selected_goals_names = [
                key for key, val in input_dict.items() if val is not None
            ]
            selected_goals_dict = {
                key: val
                for key, val in default_goals.items()
                if key in selected_goals_names
            }
            pop.goals_dict = selected_goals_dict
        return render_template(
            "running.html",
            run_page="run",
            done_page="done",
            selected_goals=selected_goals_dict,
        )
    return render_template("read.html", students=STUDENTS.to_html(),
                           target_limits=pop.df_all_students_goals_limits.to_html(),
                           page_start="/start", options=options)


@app.route("/run")
def run_algo():
    # filename = os.path.join(app.config["UPLOAD_FOLDER"], "students.csv")  # hard-coded
    # students = StudentGroup(filename)
    pop.run(n_gen=2, verbose=True)
    front = pop.pareto()
    front["sum"] = sum([front[col] for col in pop.goals_names])
    global best_plan
    best_plan = front.sort_values("sum").iloc[0].values[0]
    global best_students
    best_students = best_plan.students
    return "Done"


@app.route("/done")
def present_result():
    best_students.index.names = [None]
    best_plan_classes = {}
    for i, k in enumerate(best_plan.classes):
        df = pd.concat([best_plan.classes_df_output[i], best_plan.df_means_classes[i]])
        best_plan_classes[k.name] = df.to_html(na_rep='')
        
    pareto = pop.pareto().drop(columns=["Individual"])
    return render_template(
        "results_table.html",
        class_list=best_plan_classes,
        target_limits=pop.df_all_students_goals_limits.to_html(na_rep=''),
        opt_targets=best_plan.df_summary.to_html(na_rep=''),
        pareto=pareto.to_html(na_rep=''),
        title="Best solution found",
    )


@app.route("/download_best_plan")
def download_plan():
    filename = "web_best_plan.xlsx"
    filepath = os.path.join(app.config["DATA_FOLDER"], filename)
    best_plan.write_excel(filepath)
    return redirect(url_for('download_file', name=filename))


@app.route('/data/<name>')
def download_file(name):
    return send_from_directory(app.config["DATA_FOLDER"], name, as_attachment=True)
