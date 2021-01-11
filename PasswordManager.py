import mysql.connector
from mysql.connector import Error
import time
from os import system
import string
import secrets
import pyperclip

def print_table(data):
    system("cls")
    if len(data)==0:
        print("No passwords stored in the database")
        return
    
    result=""

    result+="+--------------------------------------------------------------+\n"
    result+="|      service       |      user_id       |      password      |\n"
    result+="|--------------------------------------------------------------|\n"

    for row in data:
        result+="|"
        for entry in row:
            spaces=int((20-len(entry))/2)
            # add spaces before value
            for i in range(0,spaces):
                result+=" "
            # add value
            result+=entry
            # add spaces after value
            for i in range(0,spaces):
                result+=" "
            
            if (len(entry)+2*spaces)<20:
                result+=" "
            result+="|"
        result+="\n"
        result+="|--------------------------------------------------------------|\n"

    print(result)

def create_db_connection(host_name,por,user_name, user_password,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=por,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query,type="select"):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if type=="select":
            results=cursor.fetchall()
            print_table(results)
        
        connection.commit()
        cursor.close()
        if type!="select":
            print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def close_connection(connection):
    connection.close()
    print("Connection Closed. Exiting the program...",end="")
    time.sleep(1)

def new_password(connection):
    print("Write in order Service, Username, Password (separated by a space): ", end="")
    params=input()
    params=params.split()
    query= f"INSERT INTO psw_table VALUES ('{params[0]}','{params[1]}','{params[2]}');"
    execute_query(connection,query,"insert")

def delete_row(connection):
    print("Write in order Service, Username, Password you want to delete(separated by a space): ", end="")
    params=input()
    params=params.split()

    query=f"DELETE FROM psw_table WHERE service='{params[0]}' AND user_id='{params[1]}' AND password='{params[2]}';"
    execute_query(connection,query,"delete")

def get_passwords(connection):
    query="SELECT * FROM psw_table"
    execute_query(connection,query)

def passwords_from_username(connection):
    print("Write the username you want to search (case sensitive): ")
    user=input()
    query=f"SELECT * FROM psw_table WHERE user_id='{user}'"
    execute_query(connection,query)

def usernames_from_password(connection):
    print("Write the password you want to search (case sensitive): ")
    psw=input()
    query=f"SELECT * FROM psw_table WHERE password='{psw}'"
    execute_query(connection,query)

def passwords_from_service(connection):
    print("Write the service you want to search (case sensitive): ")
    service=input()
    query=f"SELECT * FROM psw_table WHERE service='{service}'"
    execute_query(connection,query)

def generate_password(connection,type="new_row",service="",user_id=""):
    while True:
        try:
            print("Write the length of the Password (minimum 8): ",end="")
            length=int(input())
            break
        except ValueError:
            print("Error. Incorrect length")

    characters_set = string.ascii_letters + string.digits + string.punctuation
    password = secrets.SystemRandom().choice(string.ascii_lowercase)
    password += secrets.SystemRandom().choice(string.ascii_uppercase)
    password += secrets.SystemRandom().choice(string.digits)
    password += secrets.SystemRandom().choice(string.punctuation)

    password += ''.join(secrets.SystemRandom().sample(characters_set,length-4))
    password.replace("'","!")

    print("Your new Safe Password is:", password)
    while True:
        print("Do you want to save it? (y/n): ",end="")
        answer=input()
        if answer[0]=='y':
            if type=="new_row":
                print("Write in order Service and Username (separated by a space): ",end="")
                params=input()
                params=params.split()
                query= f"INSERT INTO psw_table VALUES ('{params[0]}','{params[1]}','{password}');"
                execute_query(connection,query,"insert")
                break
            else:
                query= f"UPDATE psw_table SET password='{password}' WHERE service='{service}' AND user_id='{user_id}';"
                execute_query(connection,query,"update")
                break
        else:
            if answer[0]=='n':
                break
            else:
                print("Wrong command. Try Again")

    pyperclip.copy(password)
    print("Password Copied to your clipboard")


def modify_password(connection):
    print("These are your saved passwords:")
    get_passwords(connection)
    print("Write in order Service and Username (separated by a space) of the Password you want to change: ", end="")
    params=input()
    params=params.split()
    print("Write the new Password (press 0 to generate a new password): ",end="")
    answ=input()
    if answ=='0':
        generate_password(connection,"update",params[0],params[1])
    else:
        query= f"UPDATE psw_table SET password='{answ}' WHERE service='{params[0]}' AND user_id='{params[1]}';"
        execute_query(connection,query,"update")



def main():
    
    connection=None
    while connection is None:
        print("Insert your master password: ", end="")
        pw=input()
        connection = create_db_connection("127.0.0.1",3306,"root",pw,"pswdb")

    cmd=''
    switcher={
        '0': "close_connection(connection)",
        '1': "new_password(connection)",
        '2': "delete_row(connection)",
        '3': "get_passwords(connection)",
        '4': "passwords_from_username(connection)",
        '5': "usernames_from_password(connection)",
        '6': "passwords_from_service(connection)",
        '7': "generate_password(connection)",
        '8': "modify_password(connection)"
    }
    
    while cmd!='0':
        print("\n**********Menu**********")
        print("Select a number:")
        print("1) Add a New Password")
        print("2) Delete a saved Password")
        print("3) Get all Passwords")
        print("4) Get all the Passwords from a Username")
        print("5) Get all the Usernames from a Password")
        print("6) Get all the Passwords from a Service")
        print("7) Generate a Safe Password")
        print("8) Modify an existing password") 
        print("0) Exit")
        
        cmd=input()
        eval(switcher.get(cmd,"print('Invalid Command. Try Again')"))


if __name__=="__main__":
    main()
