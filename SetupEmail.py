#####################################################################
# Stores emails used in newsAgri_email.py with their encrypted      #
# passwords. It is always good practice to store a password hash    #
# instead of keeping your plain text password in a program.         #
#####################################################################

# import
import re
from cryptography.fernet import Fernet

# generate a key and save it as a file
key = Fernet.generate_key()
print("key generated!")
with open("key.key", "wb") as f:
    f.write(key)

def get_email():
    """
        Asks user to input their email, password and recipient email address.
    """
    sendEmail = input(str("Enter your email address: "))
    password = input(str("Enter your email password: "))
    recieveEmail = []
    additional = ""
    while True:
        recieveEmail.append(input(str("Enter the recipient email address: ")))
        additional = input(str("Would you like to add another recipient? (y/n): "))
        if additional == "n":
            break

    check_email(sendEmail, recieveEmail)
    encrypt_email(sendEmail, password, recieveEmail)


def check_email(sendEmail, recieveEmail):
    """
        Checks that the emails the user has entered are gmail accounts
        Args:
            sendEmail: a string containing the users gmail address
            recieveEmail: a string containing the recipients gmail address
        Returns:
            when the user has entered valid email addresses
    """
    # checks sender email is @gmail.com and recipient emails are valid 
    regrex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$' 
    if len(sendEmail) > 10:
        if sendEmail[-10:] == "@gmail.com":
            for email in recieveEmail:
                if len(email) >= 0 and re.search(regrex, email):
                    print(email, " - accepted")  
                else:
                    print("Invalid email: ", email)
            return
        else:
            print("Your email must be a @gmail.com account!")
    else:
        print("Enter a valid email address!")
    get_email()


def encrypt_email(sendEmail, password, recieveEmail):
    """
        Hashes the password using the key and saves it to a text
        file with the two emails.
        Args:
            sendEmail: a string containing the users gmail address
            recieveEmail: a string containing the recipients gmail address
            password: a string containing the users gmail password
    """
    # converts email strings into bytes
    sendEmail = bytes(sendEmail + "\n", encoding="utf8")
    recpEmail = ""
    for email in recieveEmail:
        recpEmail += (str(email) + "\n")
    recieveEmail = bytes(recpEmail, encoding="utf8")
    password = bytes(password, encoding="utf8")

    # hashes the password with the generated key
    f = Fernet(key)
    encrypted = f.encrypt(password)
    print("password encrypted!")

    # writes hashed password and email list to text file
    with open("password.txt", "w"): pass
    with open("password.txt", "ab") as f:
        f.write(sendEmail)
        f.write(recieveEmail)
        f.write(encrypted)
        

get_email()
print("Press any key to end!")
input()
