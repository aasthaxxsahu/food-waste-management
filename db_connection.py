import mysql.connector

def get_connection():

    conn = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="root123",
        database="food_waste_management"
    )

    return conn