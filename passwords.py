
import asyncio
import json
import uuid
import random
import subprocess

from flask import Flask
from flask_mysqldb import MySQL
from enum import Enum

class StatusCodes(Enum):
    OK = "200"
    BAD_REQUEST = "400"
    NOT_FOUND = "404"

app = Flask(__name__)
app.config["MYSQL_USER"] = "jeremy"
app.config["MYSQL_PASSWORD"] = "s66757NH"
app.config["MYSQL_DB"] = "Careers"
database = MySQL(app)

def generatePassword(copy: bool=True) -> str:
    '''
    Generate a unique password (of length 16 and with special characters)
    If copy is set to True --> copy password to clipboard
    '''
    delimiter = "-"
    specialCharacters = ("!", "?", "%", "$")
    password = str(uuid.uuid4())                    # [0-9]{0-9}-[0-9]{0-9}...
    password = password.partition(delimiter)[0]     # Get only string of digits before first "-"

    # Randomly insert special character
    i = random.randint(0, len(password) - 1)
    j = random.randint(0, len(specialCharacters) - 1)
    password = password[:i] + specialCharacters[j] + password[i:]

    # Copy to clipboard if true
    if (copy):
        subprocess.run("pbcopy", text=True, input=password)
    return password

@app.route("/company/<companyName>", methods=["POST"])
@app.route("/company/<companyName>/<username>", methods=["POST"])
async def addCompany(companyName: str, username: str="") -> str:
    '''
    Insert new company name and password into database
    Password is automatically copied to clipboard
    '''
    connection = database.connect
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO Passwords VALUES ('%s', '%s', '%s')" % (companyName.capitalize(), generatePassword(), username))
        connection.commit()
    except:
        return StatusCodes.NOT_FOUND
    else:
        connection.close()
        return StatusCodes.OK

@app.route("/company/<companyName>", methods=["GET"])
async def getCompany(companyName: str) -> dict[str, str]:
    '''
    Get record from database by company name
    '''
    connection = database.connect
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Passwords WHERE companyName='%s'" % companyName.capitalize())
    data = cursor.fetchall()
    connection.close()
    return json.dumps(data)

@app.route("/ping", methods=["GET"])
async def ping() -> str:
    '''
    Health check database to verify if it is online
    '''
    connection = database.connect
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM Passwords LIMIT 1")
    except:
        return StatusCodes.BAD_REQUEST
    finally:
        connection.close()
        return "Success"


@app.route("/")
async def root() -> str:
    return "Hello World"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
