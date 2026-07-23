import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kiran@12345",
    database="StudentDB"
)

cursor = db.cursor(dictionary=True)