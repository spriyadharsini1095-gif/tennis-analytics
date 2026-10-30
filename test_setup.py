import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(override=True)
print("PORT =", os.getenv("DB_PORT"))
print("DB   =", os.getenv("DB_NAME"))
print("USER =", os.getenv("DB_USER"))
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"))
print("Connected to PostgreSQL!")
conn.close()