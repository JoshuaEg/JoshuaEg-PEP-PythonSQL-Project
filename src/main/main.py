import csv
import os
import functools
import sqlite3

# Resolve the resources folder relative to this file, so paths work
# no matter what directory the script is run from.
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources')

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users(os.path.join(_RESOURCES_DIR, 'users.csv'))
    load_and_clean_call_logs(os.path.join(_RESOURCES_DIR, 'callLogs.csv'))
    write_user_analytics(os.path.join(_RESOURCES_DIR, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(_RESOURCES_DIR, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.

def forall(lis: list, predicate):
    for a in lis:
        if not predicate(a): return False
    return True
def exist(lis: list, predicate):
    for a in lis:
        if predicate(a): return True
    return False
# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    cursor.execute("DELETE FROM users")
    with open(file_path, 'r') as f:
        f.readline()
        line = f.readline()
        while(line):
            dat = line.split(',')
            dat[-1] = dat[-1].removesuffix('\n')
            if len(dat) != 2 or not (dat[0].isalpha() and dat[1].isalpha()):
                line = f.readline()
                continue
            cursor.execute(f"""
                INSERT INTO users(firstName, lastName) VALUES
                ('{dat[0]}','{dat[1]}')
            """)
            line = f.readline()


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    cursor.execute("DELETE FROM callLogs")
    with open(file_path, 'r') as f:
        f.readline()
        lines = f.readlines()
        for l in lines:
            dat = l.split(',')
            dat[-1] = dat[-1].removesuffix('\n')
            if len(dat) != 5: continue
            if exist(dat, lambda x: (not x) or x.isspace() ): continue
            if not forall([dat[1],dat[2],dat[4]], lambda x: x.isnumeric()): continue
            if not (dat[3] == 'inbound' or 'outbound'): continue
            cursor.execute(f"""
                INSERT INTO callLogs(phoneNumber, startTime, endTime, direction, userId) VALUES
                ('{dat[0]}',{dat[1]}, {dat[2]}, '{dat[3]}', {dat[4]})
            """)


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    cursor.execute("""
        SELECT userId, AVG(endTime - startTime) as duration, COUNT(*) as numCalls
        FROM callLogs GROUP BY userId
        """)
    dat = cursor.fetchall()
    with open(csv_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(dat)
    # print(dat)


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):

    cursor.execute("""
        SELECT *
        FROM calllogs ORDER BY userId, startTime
        """)
    dat = cursor.fetchall()
    with open(csv_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(dat)


# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()