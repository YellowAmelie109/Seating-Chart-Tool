#Window needs to be resized when going to pages
#Styling
#Create the database

import tkinter 
from tkinter import ttk
import sqlite3 as sql
import bcrypt

connection = sql.connect("seatingChartData.db")
cur = connection.cursor()
#password = bcrypt.hashpw("h".encode('utf-8') , bcrypt.gensalt() )
#query = "INSERT INTO Teachers (FirstName, LastName, Email, Password) VALUES ('Bob', 'Marley', 'bob.marley@gmail.com', ?)"
#cur.execute(query,(password,))
#connection.commit()
#for row in cur.execute("SELECT * FROM Teachers"):
#    print(row)

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
        ttk.Button(self.frame, text="Register",command="").grid(column=1,row=5)

class LoginPage(Page):
    def display(self):
        self.email = tkinter.StringVar()
        self.password = tkinter.StringVar()
        #Add back button
        ttk.Label(self.frame, text="Email:").grid(column=0,row=0)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=1,row=0,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=0,row=1)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=1,row=1,columnspan=2)
        ttk.Button(self.frame, text="Login",command=self.validate).grid(column=1,row=2)
    def validate(self):
        #Fetches encrypted correct password from databse
        cur.execute("SELECT Password from Teachers WHERE Email = ?",(self.email.get(),))
        correctPass=cur.fetchone()[0]
        #Checks that the password entered matches the encrypted correct password
        if bcrypt.checkpw(self.password.get().encode('utf-8'), correctPass):
            self.goto(MainPage())
        else:
            print("nuhuh") #Appropiate message on GUI

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
