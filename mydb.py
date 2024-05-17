import mysql.connector

dataBase = mysql.connector.connect(
	host = 'localhost',
	user = 'root',
	passwd = 'password123@'
	
	)

# cursor object
cursorObject = dataBase.cursor()

# creating database
cursorObject.execute("CREATE DATABASE inventory")

print("Done!")