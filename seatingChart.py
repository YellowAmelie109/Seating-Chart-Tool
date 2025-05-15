#Add seats
#Add databases
#Students pop-up
#POI
#Students

#Window needs to be resized when going to pages and text display(password invalid format text)
#Styling

import tkinter 
from tkinter import ttk
import sqlite3 as sql
import bcrypt
import re

connection = sql.connect("seatingChartData.db")
cur = connection.cursor()

DOMAINS=("exe-coll.ac.uk","exetermathematicsschool.ac.uk")
#At least 1 letter, any number of numbers, one or no (+, least one alphanumeric character), one @
#eg. EdHorncastle183+f8h_6f@
EMAILFORMAT="[A-z]+\d*(\+\w+)?@" 



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

        #Add styling
        ttk.Button(self.frame, text="< Back", command=lambda:self.goto(LoggedOutPage())).grid(column=0,row=0)
        ttk.Label(self.frame,text="Register:").grid(column=1,row=0)
        ttk.Label(self.frame, text="First name:").grid(column=1,row=1,padx=10,pady=10)
        ttk.Entry(self.frame, textvariable = self.firstName).grid(column=2,row=1,columnspan=2)
        ttk.Label(self.frame, text="Last name:").grid(column=1,row=2)
        ttk.Entry(self.frame, textvariable=self.lastName).grid(column=2,row=2,columnspan=2)
        ttk.Label(self.frame, text="Email:").grid(column=1,row=3)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=2,row=3,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=1,row=4)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=2,row=4,columnspan=2)
        ttk.Label(self.frame,text="Passwords must contain at least one each of capital letter, symbol, and number and be between 8-16 characters"
                  ).grid(column=1,row=5,columnspan=10)
        ttk.Label(self.frame, text="Confirm password:").grid(column=1,row=6)
        ttk.Entry(self.frame, textvariable=self.password2,show='*').grid(column=2,row=6,columnspan=2)
        ttk.Button(self.frame, text="Register",command=self.addtoDatabase).grid(column=1,row=7)
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=8,columnspan=10) #columnspan?

    def addtoDatabase(self):
        query="INSERT INTO Teachers (FirstName, LastName, Email, Password) VALUES (?, ?, ?, ?)"
        #Checking email is at one of the allowed domains and follows the regex format at the top
        validEmail=False
        for domain in DOMAINS:
            if re.search(EMAILFORMAT+domain,self.email.get()):
                validEmail=True
        if validEmail:
            #Checking password fields are valid
            password=self.password.get()
            if password==self.password2.get() and password!="":
                #At least one each of symbol, capital letter, and number between 8-16 characters
                if re.search("[^\w\s]+",password) and re.search("[A-Z]+",password) and re.search("\d+",
                password) and len(password)>=8 and len(password)<=16:
                    self.password = bcrypt.hashpw(password.encode('utf-8') , bcrypt.gensalt() )
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
                    self.invalid.set("Password must contain at least one each of symbol, \ncapital letter, and number and must be between \n8-16 characters")
            else:
                if password=="":
                    self.invalid.set("Enter a password")
                elif password!=self.password2.get():
                    self.invalid.set("Passwords do not match")
        else:
            self.invalid.set("Invalid email")



        
class LoginPage(Page):
    def display(self):
        self.email = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.invalid=tkinter.StringVar()
        #Add styling
        ttk.Button(self.frame, text="< Back", command=lambda:self.goto(LoggedOutPage())).grid(column=0,row=0)
        ttk.Label(self.frame,text="Log in:").grid(column=1,row=0)
        ttk.Label(self.frame, text="Email:").grid(column=1,row=1)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=2,row=1,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=1,row=2)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=2,row=2,columnspan=2)
        ttk.Button(self.frame, text="Login",command=self.validate).grid(column=1,row=3)
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=4)
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
        self.CanvasWidth = 900
        self.CanvasHeight = 900

        self.displayMenu()
        tkinter.Canvas(self.frame,
                       width=self.CanvasWidth,
                       height=self.CanvasHeight,
                       background='white').grid(column=0,row=1,columnspan=5,rowspan=5)
    
    def displayMenu(self):
        menubar = tkinter.Menu(root,background="lightyellow")
        root['menu'] = menubar

        #"Class" dropdown menu
        menu_class = tkinter.Menu(menubar)
        menubar.add_cascade(menu=menu_class, label='Class')
        menu_class.add_command(label='Switch class', command="")
        menu_class.add_command(label="Save", command="")
        menu_class.add_command(label="Edit class",command="")

        #"Students" dropdown menu
        menu_students = tkinter.Menu(menubar)
        menubar.add_cascade(menu=menu_students, label="Students")
        menu_students.add_command(label='Edit students', command ="")

        #"Arrange" dropdown menu
        menu_arrange = tkinter.Menu(menubar)
        menubar.add_cascade(menu=menu_arrange, label="Arrange")
        
        #Tick box to choose to hide or show names of students
        hideNames=tkinter.StringVar()
        menubar.add_checkbutton(label="Hide names", variable=hideNames, onvalue=True, offvalue=False)

        #Tick box to choose to hide or show images of students
        hideImages=tkinter.StringVar()
        menubar.add_checkbutton(label="Hide images", variable=hideImages, onvalue=True, offvalue=False)

        




root = tkinter.Tk()
root.title( "Seating Planner" )
root.option_add('*tearOff', False)
LoggedOutPage().display()
root.mainloop()
connection.close()