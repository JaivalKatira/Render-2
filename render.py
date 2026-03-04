from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id SERIAL PRIMARY KEY,
name TEXT,
age INT,
grade TEXT
)
""")

conn.commit()

HTML_PAGE = """
<h2>Student Database</h2>

<form action="/add" method="post">
Name:<input name="name"><br>
Age:<input name="age"><br>
Grade:<input name="grade"><br>
<button>Add Student</button>
</form>

<hr>

<form action="/search" method="get">
Search Name:<input name="name">
<button>Search</button>
</form>
"""

@app.route("/")
def home():
    return HTML_PAGE


@app.route("/add", methods=["POST"])
def add_student():

    name=request.form["name"]
    age=request.form["age"]
    grade=request.form["grade"]

    cursor.execute(
        "INSERT INTO students(name,age,grade) VALUES(%s,%s,%s)",
        (name,age,grade)
    )

    conn.commit()

    return "Student Added"


@app.route("/search")
def search():

    name=request.args.get("name")

    cursor.execute(
        "SELECT name,age,grade FROM students WHERE name=%s",
        (name,)
    )

    student=cursor.fetchone()

    if student:
        return jsonify({
            "name":student[0],
            "age":student[1],
            "grade":student[2]
        })

    return jsonify({"error":"Student not found"})


if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
