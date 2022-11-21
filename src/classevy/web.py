# A very simple Flask Hello World app for you to get started with...

import os
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    send_from_directory,
    render_template,
)
from werkzeug.utils import secure_filename
import pandas as pd
from classevy import StudentGroup, Klas, Plan


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
            df = import_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return render_template(
                "simple.html",
                tables=[df.to_html(classes="data")],
                titles=df.columns.values,
            )

    return render_template(
        "forms.html",
        page=request.url
    )


@app.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
