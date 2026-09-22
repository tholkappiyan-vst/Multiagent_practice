# -*- coding: utf-8 -*-

# ============================================================
# 1. INSTALL REQUIRED PACKAGE
# ============================================================

!pip install -U langchain-google-genai


# ============================================================
# 2. IMPORTS
# ============================================================

import os
import sqlite3
import ast
import operator as op

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool


# ============================================================
# 3. GOOGLE API KEY
# ============================================================

os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"


# ============================================================
# 4. CREATE GEMINI MODEL
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)


# ============================================================
# 5. CREATE SQLITE DATABASE
# ============================================================

database_path = "students.db"

db_connection = sqlite3.connect(database_path)
db_cursor = db_connection.cursor()


# Create students table
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    python INTEGER NOT NULL,
    database_mark INTEGER NOT NULL,
    ai INTEGER NOT NULL,
    web INTEGER NOT NULL
)
""")

db_connection.commit()


# ============================================================
# 6. INSERT STUDENT DATA
# ============================================================

# Clear old data
db_cursor.execute("DELETE FROM students")


student_records = [
    ("22CS045", "Dhanushya", "Computer Science", 85, 72, 90, 78),
    ("22CS046", "Rahul", "Computer Science", 65, 70, 68, 72),
    ("22CS047", "Priya", "Information Technology", 92, 88, 95, 90),
    ("22CS048", "Arun", "Information Technology", 55, 60, 58, 62),
    ("22CS049", "Meena", "Computer Science", 78, 85, 80, 88)
]


db_cursor.executemany("""
INSERT INTO students
(student_id, name, department, python, database_mark, ai, web)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", student_records)

db_connection.commit()
db_connection.close()

print("Student database created successfully!")


# ============================================================
# 7. TOOL 1 - GET STUDENT INFORMATION
# ============================================================

@tool
def get_student_info(student_id: str) -> str:
    """
    Get the student's name and department using their student ID.

    Use this tool when the user asks for:
    - student name
    - department
    - student information
    """

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, department
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student_data = cursor.fetchone()

    connection.close()

    if student_data is None:
        return f"No student found with ID {student_id}."

    student_name, student_department = student_data

    return (
        f"Student ID: {student_id}\n"
        f"Name: {student_name}\n"
        f"Department: {student_department}"
    )


# ============================================================
# 8. TOOL 2 - GET STUDENT MARKS
# ============================================================

@tool
def get_student_marks(student_id: str) -> str:
    """
    Get the marks of a student in Python, Database, AI and Web.

    Use this tool when the user asks about:
    - marks
    - scores
    - total
    - average
    - passing eligibility
    """

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT python, database_mark, ai, web
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    marks_data = cursor.fetchone()

    connection.close()

    if marks_data is None:
        return f"No student found with ID {student_id}."

    python_score, database_score, ai_score, web_score = marks_data

    return (
        f"Student ID: {student_id}\n"
        f"Python: {python_score}\n"
        f"Database: {database_score}\n"
        f"AI: {ai_score}\n"
        f"Web: {web_score}"
    )


# ============================================================
# 9. SAFE CALCULATOR
# ============================================================

SUPPORTED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg
}


def evaluate_math_node(node):
    """
    Safely evaluate a mathematical expression.
    """

    # Number
    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Invalid number")


    # Binary operation
    if isinstance(node, ast.BinOp):

        operation = SUPPORTED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Operator not allowed")

        left_value = evaluate_math_node(node.left)
        right_value = evaluate_math_node(node.right)

        return operation(left_value, right_value)


    # Unary operation
    if isinstance(node, ast.UnaryOp):

        operation = SUPPORTED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Operator not allowed")

        return operation(
            evaluate_math_node(node.operand)
        )


    raise ValueError("Invalid expression")


def safe_calculate(math_expression):
    """
    Safely calculate a basic mathematical expression.
    """

    parsed_expression = ast.parse(
        math_expression,
        mode="eval"
    )

    return evaluate_math_node(
        parsed_expression.body
    )


# ============================================================
# 10. TOOL 3 - CALCULATOR
# ============================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Examples:
    85 + 72 + 90 + 78

    (85 + 72 + 90 + 78) / 4

    Use this tool when a numerical calculation is required.
    """

    try:

        calculated_value = safe_calculate(expression)

        return f"Result: {calculated_value}"

    except Exception as error:

        return (
            f"Could not calculate the expression: {error}"
        )


# ============================================================
# 11. TOOL 4 - GET PASSING RULES
# ============================================================

@tool
def get_passing_rules() -> str:
    """
    Get the university rules required for a student to pass.

    Rules:
    - Minimum overall average: 40%
    - Minimum mark in every subject: 35%

    Use this tool when the user asks about:
    - passing
    - eligibility
    - pass requirements
    """

    return (
        "Passing Rules:\n"
        "1. Minimum overall average: 40%\n"
        "2. Minimum mark in every subject: 35%"
    )


# ============================================================
# 12. ADD ALL TOOLS
# ============================================================

agent_tools = [
    get_student_info,
    get_student_marks,
    calculator,
    get_passing_rules
]


# ============================================================
# 13. CREATE LANGCHAIN AGENT
# ============================================================

student_agent = create_agent(
    model=llm,
    tools=agent_tools,

    system_prompt="""
You are a Student Information Assistant.

Your job is to answer questions about students using
the available tools.

IMPORTANT RULES:

1. Always use tools to obtain student information.

2. Never invent student data.

3. Use get_student_info when the user asks for:
   - name
   - department
   - student information

4. Use get_student_marks when the user asks for:
   - marks
   - scores
   - subject marks

5. Use calculator whenever a numerical calculation
   such as total or average is required.

6. Use get_passing_rules when the user asks about
   passing or eligibility.

7. You may call multiple tools when necessary.

8. Decide dynamically which tools are needed based
   on the user's question.

9. Results returned by one tool can be used as
   information for another tool.

10. For passing eligibility:
    - obtain the student's marks
    - obtain the passing rules
    - calculate the average when required
    - check every subject against the minimum mark
    - provide the final eligibility result

11. Do not manually follow a fixed tool sequence.
    Decide what is required for each question.

12. Give the final answer clearly and concisely.
"""
)


# ============================================================
# 14. GET USER QUESTION
# ============================================================

user_question = input(
    "Ask something about a student: "
)


# ============================================================
# 15. INVOKE AGENT
# ============================================================

agent_result = student_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": user_question
            }
        ]
    }
)


# ============================================================
# 16. GET FINAL ANSWER
# ============================================================

final_answer = agent_result["messages"][-1].content


# Gemini may sometimes return structured content
if isinstance(final_answer, list):

    final_answer = "\n".join(
        item["text"]
        for item in final_answer
        if isinstance(item, dict) and "text" in item
    )


# ============================================================
# 17. DISPLAY RESULT
# ============================================================

print("\n" + "=" * 60)

print("QUESTION")
print(user_question)

print("=" * 60)

print("ANSWER")
print(final_answer)

print("=" * 60)