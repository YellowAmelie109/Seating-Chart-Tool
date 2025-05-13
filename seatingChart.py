#Window needs to be resized when going to pages
#Styling
#Password format, with label to tell user password format

import tkinter 
from tkinter import ttk
import sqlite3 as sql
import bcrypt
import re

connection = sql.connect("seatingChartData.db")
cur = connection.cursor()

domains=["exe-coll.ac.uk","exetermathematicsschool.ac.uk"]
#At least 1 letter, any number of numbers, one or no (+, least one alphanumeric character), one @
#eg. EdHorncastle183+f8h_6f@
emailFormat="[A-z]+\d*(\+\w+)?@" 

class Page:
    def __init__(self):
        self.frame = ttk.Frame(root)
        self.frame.grid()
    def goto(self, page):
        self.frame.destroy()
        page.frame = ttk.Frame(root)
        page.frame.grid()
        page.display()


class LoggedOutPage(Page):
    def display(self):
        ttk.Label(self.frame, text="Please register or log in to access your seating charts").grid(column=1,row=0,sticky=(tkinter.W,tkinter.E))
        ttk.Button(self.frame, text="Register", command=lambda:self.goto(RegisterPage())).grid(column=1,row=1)
        ttk.Button(self.frame, text="Log in", command=lambda:self.goto(LoginPage())).grid(column=1,row=2,sticky=tkinter.S)
        #Add whitespace, looks weird don't like it and style it ig

class RegisterPage(Page):
    def display(self):
        self.firstName = tkinter.StringVar()
        self.lastName= tkinter.StringVar()
        self.email = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.password2 = tkinter.StringVar()
        self.invalid = tkinter.StringVar()

        #Add validation and whitespace and a back button
        ttk.Label(self.frame, text="First name:").grid(column=0,row=0,padx=10,pady=10)
        ttk.Entry(self.frame, textvariable = self.firstName).grid(column=1,row=0,columnspan=2)
        ttk.Label(self.frame, text="Last name:").grid(column=0,row=1)
        ttk.Entry(self.frame, textvariable=self.lastName).grid(column=1,row=1,columnspan=2)
        ttk.Label(self.frame, text="Email:").grid(column=0,row=2)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=1,row=2,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=0,row=3)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=1,row=3,columnspan=2)
        ttk.Label(self.frame, text="Confirm password:").grid(column=0,row=4)
        ttk.Entry(self.frame, textvariable=self.password2,show='*').grid(column=1,row=4,columnspan=2)
        ttk.Button(self.frame, text="Register",command=self.addtoDatabase).grid(column=1,row=5)
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=6)

    def addtoDatabase(self):
        query="INSERT INTO Teachers (FirstName, LastName, Email, Password) VALUES (?, ?, ?, ?)"
        #Checking email is at one of the allowed domains and follows the regex format at the top
        validEmail=False
        for domain in domains:
            if re.search(emailFormat+domain,self.email.get()):
                validEmail=True
        if validEmail:
            #Checking password fields are valid
            if self.password.get()==self.password2.get() and self.password.get()!="":
                self.password = bcrypt.hashpw(self.password.get().encode('utf-8') , bcrypt.gensalt() )
                #Prevents emails being registered multiple times
                try:
                    #Adding to the database
                    cur.execute(query,(self.firstName.get(),self.lastName.get(),self.email.get(),self.password))
                    connection.commit()
                    self.goto(MainPage())
        #Error messages
                except sql.IntegrityError:
                    self.invalid.set("Email already registered")
                except:
                    self.invalid.set("An error occurred")
            else:
                if self.password.get()=="":
                    self.invalid.set("Enter a password")
                elif self.password.get()!=self.password2.get():
                    self.invalid.set("Passwords do not match")
                else:
                    self.invalid.set("Password not in correct format")
        else:
            self.invalid.set("Invalid email")



        
class LoginPage(Page):
    def display(self):
        self.email = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.invalid=tkinter.StringVar()
        #Add back button
        ttk.Label(self.frame, text="Email:").grid(column=0,row=0)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=1,row=0,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=0,row=1)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=1,row=1,columnspan=2)
        ttk.Button(self.frame, text="Login",command=self.validate).grid(column=1,row=2)
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=3)
    def validate(self):
        #Fetches encrypted correct password from databse
        cur.execute("SELECT Password from Teachers WHERE Email = ?",(self.email.get(),))
        correctPass=cur.fetchone()
        #correctPass is NoneType when the email entered is not in the database
        try:
            correctPass=correctPass[0]
            #Checks that the password entered matches the encrypted correct password
            if bcrypt.checkpw(self.password.get().encode('utf-8'), correctPass):
                self.goto(MainPage())
        #Error messages
            else:
                self.invalid.set("Password incorrect.")
        except:
            self.invalid.set("Email is not registered.")




class MainPage(Page):
    def display(self):
        self.CanvasWidth = 500
        self.CanvasHeight = 500
        ttk.Button(self.frame, text="Class",command="").grid(column=0,row=0)
        ttk.Button(self.frame, text="Student",command="").grid(column=1,row=0)
        ttk.Button(self.frame,text="Arrange",command="").grid(column=2,row=0)
        ttk.Button(self.frame,text="Hide images",command="").grid(column=4,row=0)
        ttk.Button(self.frame,text="Hide names",command="").grid(column=5,row=0)
        tkinter.Canvas(self.frame,
                       width=self.CanvasWidth,
                       height=self.CanvasHeight,
                       background='white').grid(column=0,row=1,columnspan=5,rowspan=5)




root = tkinter.Tk()
root.title( "Seating Planner" )
LoggedOutPage().display()
root.mainloop()
connection.close()
