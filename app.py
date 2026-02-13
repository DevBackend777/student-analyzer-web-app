from flask import Flask, render_template, request, url_for, redirect
from sklearn.linear_model import LogisticRegression
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    model = train_model()
    students = []

    try:
        with open("students.csv", "r") as f:
            for line in f:
                name, math, english, science = line.strip().split(",")

                math = int(math)
                english = int(english)
                science = int(science)

                average = round((math + english + science) / 3, 2)
                status = "PASS" if average >= 50 else "FAIL"

                students.append([
                    name,
                    math,
                    english,
                    science,
                    average,
                    status
                ])
            students.sort(key=lambda s: s[4], reverse=True)
    except FileNotFoundError:
        pass

    count = len(students)

    if count > 0:
        class_avg = round(sum(s[4] for s in students) / count, 2)
        best_student = students[0][0]
        pass_count = sum(1 for s in students if s[5] == "PASS")
        fail_count = sum(1 for s in students if s[5] == "FAIL")
    
    else:
        class_avg = 0
        best_student = ""
        pass_count = 0
        fail_count = 0

    prediction = None

    if model and count > 0:
        best = students[0]
        pred = model.predict([[best[1], best[2], best[3]]])
        prediction = "PASS" if pred[0] == 1 else "FAIL"

    return render_template(
        "index.html",
        students=students,
        count=count,
        class_avg=class_avg,
        best_student=best_student,
        pass_count=pass_count,
        fail_count=fail_count,
        prediction=prediction
    )


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        math = request.form["math"]
        english = request.form["english"]
        science = request.form["science"]

        with open("students.csv", "a") as f:
            f.write(f"{name},{math},{english},{science}\n")

        return redirect(url_for("index"))

    return render_template("add_student.html")

@app.route("/delete/<int:index>")
def del_student(index):
    students = []

    with open("students.csv", "r") as f:
        students = f.readlines()

    if 0 <= index < len(students):
        students.pop(index)

    with open("students.csv", "w") as f:
        f.writelines(students)

    return redirect(url_for("index"))

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_student(index):
    with open("students.csv", "r") as f:
        students = f.readlines()

    if request.method == "POST":
        name = request.form["name"]
        math = request.form["math"]
        english = request.form["english"]
        science = request.form["science"]

        students[index] = f"{name},{math},{english},{science}\n"

        with open("students.csv", "w") as f:
            f.writelines(students)
        
        return redirect(url_for("index"))
    data = students[index].strip().split(",")

    return render_template(
        "edit_student.html",
        student=data,
        index=index
    )

def train_model():
    try:
        df = pd.read_csv(
            "students.csv",
            names=["name", "math", "english", "science"]
        )

    except:
        return None
    
    df["average"] = df[["math", "english", "science"]].mean(axis=1)
    df["passed"] = (df["average"] >= 50).astype(int)

    if df["passed"].nunique() < 2:
        return None

    X = df[["math", "english", "science"]]
    y = df["passed"]

    model = LogisticRegression()
    model.fit(X,y)
    
    return model

if __name__ == "__main__":
    app.run(debug=True)
