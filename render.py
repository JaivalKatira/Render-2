from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Get database URL from Render environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    print("Database connected successfully")
except Exception as e:
    print("Database connection failed:", e)
    raise e

# Create table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT,
    age INTEGER,
    grade TEXT
)
""")
conn.commit()

# Simple UI
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Student Database</title>

<style>

body{
background:black;
color:white;
font-family:Arial;
text-align:center;
}

.container{
width:500px;
margin:auto;
margin-top:50px;
}

input,button{
padding:10px;
margin:8px;
width:90%;
border:none;
border-radius:5px;
}

button{
background:white;
color:black;
font-weight:bold;
cursor:pointer;
}

.result{
margin-top:20px;
padding:15px;
border:1px solid white;
}

</style>

</head>

<body>

<div class="container">

<h2>Student Database</h2>

<h3>Add Student</h3>

<input id="name" placeholder="Name">
<input id="age" placeholder="Age">
<input id="grade" placeholder="Grade">

<button onclick="addStudent()">Save Student</button>

<hr>

<h3>Search Student</h3>

<input id="searchName" placeholder="Enter student name">
<button onclick="searchStudent()">Search</button>

<div id="result" class="result"></div>

</div>

<script>

async function addStudent(){

let name=document.getElementById("name").value
let age=document.getElementById("age").value
let grade=document.getElementById("grade").value

let res=await fetch("/add_student",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({name,age,grade})
})

let data=await res.json()

alert(data.message)

}

async function searchStudent(){

let name=document.getElementById("searchName").value

let res=await fetch("/get_student?name="+name)

let data=await res.json()

let resultDiv=document.getElementById("result")

if(data.error){
resultDiv.innerHTML="Student not found"
}else{

resultDiv.innerHTML=`
<b>Name:</b> ${data.name}<br>
<b>Age:</b> ${data.age}<br>
<b>Grade:</b> ${data.grade}
`

}

}

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/add_student", methods=["POST"])
def add_student():

    data = request.json

    name = data.get("name")
    age = data.get("age")
    grade = data.get("grade")

    cursor.execute(
        "INSERT INTO students(name, age, grade) VALUES(%s,%s,%s)",
        (name, age, grade)
    )

    conn.commit()

    return jsonify({"message": "Student saved successfully"})


@app.route("/get_student")
def get_student():

    name = request.args.get("name")

    cursor.execute(
        "SELECT name, age, grade FROM students WHERE name=%s",
        (name,)
    )

    student = cursor.fetchone()

    if student:
        return jsonify({
            "name": student[0],
            "age": student[1],
            "grade": student[2]
        })

    return jsonify({"error": "Student not found"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

