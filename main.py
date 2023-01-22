import hashlib
import sqlite3
from onetimepass import valid_totp
from secrets import choice


def sqllitefile():
    global conn
    conn = sqlite3.connect('identifier.sqlite')
    global c
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user(
                  userid integer primary key autoincrement NOT NULL ,
                  name varchar(20) NOT NULL,
                  password varchar(25) NOT NULL,
                  code varchar(16) not null
                );''')


# For choosing between register and login
def choose():
    sqllitefile()
    nc = True
    while nc:
        print('Register or login: ')
        lor = input('(r/l)')
        if lor == 'l' or lor == 'L':
            nc = False
            return login()
        elif lor == 'r' or lor == 'R':
            nc = False
            return register()
        else:
            print('---------------------------------------------')


def generate_secret():  # Function to return a random string with length 16.
    secret = ''
    while len(secret) < 16:
        secret += choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')
    return secret


# Registeration
def register():
    user = input('Podaj login: ')

    # If username already exists
    exist = conn.execute("select NAME from user where NAME like ?", (user,)).fetchone()
    if exist:
        print('------------------------------------------')
        print('user name not available')
        print('Please use different user name to register')
        register()

    # Password
    np = True
    while np:
        print('----------------------------')
        password = input('Enter password to register: ')
        if 3 < len(password) < 16:
            np = False

    currentPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
    secret = generate_secret()
    print('------------------------')
    print('Enter the following secret in your authenticator app: ', secret)
    print("""
    Instructions for saving this secret it Google Authenticator:
    1. Open Google Authenticator.
    2. Click plus icon at the right bottom.
    3. Click Enter a setup key.
    4. Enter an Account name of your choice and enter the secret provided above.
    5. Click Add.
    """)

    c.execute("INSERT INTO user (USERID, NAME, PASSWORD, CODE) \
          VALUES (NULL, ?, ?, ?)", (user, currentPassword, secret))
    conn.commit()
    c.close()
    conn.close()
    print('------------------------')
    print('Registration is complete')


def auth():
    t = (user,)
    c.execute('SELECT code FROM user WHERE name=?', t)
    row = c.fetchone()
    if row is None:
        print("Code not found")
    else:
        fetchedCode = row[0]

    np = True
    while np:
        otp = input('Please enter the otp generated by your authenticator app: ')
        authenticated = valid_totp(otp, fetchedCode)
        if authenticated:
            print('Correct otp, Authenticated!')
            np = False
        elif not authenticated:
            print('Wrong otp, please try again.')


# For Password in Login
def login_password():
    # Password
    print('-------------------------------------------------------------------------------------')
    currentPass = input("Enter password: ")
    currentHash = hashlib.sha256(currentPass.encode('utf-8')).hexdigest()
    t = (user,)
    c.execute('SELECT password FROM user WHERE name=?', t)
    row = c.fetchone()
    if row is None:
        print("Account not found")
    else:
        fetchedHash = row[0]

    if fetchedHash == currentHash:
        auth()
        print("Login Success")
    else:
        print("Login Fail")
        login_password()


# For Username in Login
def login():
    # User Name
    global unchoice
    unchoice, re = 1, 1
    global user
    print('------------------------------------')
    user = input('Enter username/email to login: ')
    user_exists = c.execute("select name from user where name like ?", (user,)).fetchone()
    if not user_exists:
        print('------------------------------------------------------------------')
        print('user name does not exist, Please Register first')
        print('choose 1 to register or choose any other number to try login again')
        unlchoice = input()
        if unlchoice != '1':
            login()
            re = 0
        else:
            unchoice = 0
            register()
    # password
    if unchoice and re:
        login_password()


if __name__ == '__main__':
    choose()

# CREATE TABLE IF NOT EXISTS user(
#                   userid integer primary key autoincrement NOT NULL ,
#                   name varchar(20) NOT NULL,
#                   password varchar(255) NOT NULL,
#                   code varchar(16) not null
#                 );
#
# select * from user;
#
# INSERT INTO user (USERID, NAME, PASSWORD, CODE) VALUES (1, 'admin', 'admin', 1)
