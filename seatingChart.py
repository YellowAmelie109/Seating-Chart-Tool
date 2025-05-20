#Add seats
#Students pop-up
#POI
#Students
#Class list (switch+login)
#Press enter key on login/register

#Window needs to be resized when going to pages and text display(password invalid format text)
#Styling

import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
import bcrypt #Encrypt password
import re #Regex

#Constants

#Email validation
DOMAINS=("exe-coll.ac.uk","exetermathematicsschool.ac.uk")
#Regex for at least 1 letter, then any number of numbers, then one or no (+, least one alphanumeric character), then one @
#eg. EdHorncastle183+f8h_6f@
EMAILFORMAT="[A-z]+\d*(\+\w+)?@" 
#Database path
DATABASE = "seatingChartData.db"

#Classes

#Base class for all page classes to inherit from
class Page:
    def __init__(self,root):
        self.root=root
        self.frame = ttk.Frame(self.root)
        self.frame.grid()
    def goto(self, page):
        self.frame.destroy()
        page(self.root)


#Page that is visible on first load
class LoggedOutPage(Page):
    def __init__(self,root):
        super().__init__(root)

        ttk.Label(self.frame, text="Please register or log in to access your seating charts").grid(column=1,row=0)
        ttk.Button(self.frame, text="Register", command=lambda:self.goto(RegisterPage)).grid(column=1,row=1)
        ttk.Button(self.frame, text="Log in", command=lambda:self.goto(LoginPage)).grid(column=1,row=2)

#Page for registering new users, validating their inputs, and adding to database
class RegisterPage(Page):
    def __init__(self,root):
        super().__init__(root)

        self.firstName = tk.StringVar()
        self.lastName= tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.password2 = tk.StringVar()
        self.invalid = tk.StringVar()

        ttk.Button(self.frame, text="< Back", command=lambda:self.goto(LoggedOutPage)).grid(column=0,row=0)
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
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=8,columnspan=10)

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
                        with sql.connect(DATABASE) as conn:
                            cur = conn.cursor()
                            cur.execute(query,(self.firstName.get(),self.lastName.get(),self.email.get(),self.password))
                            conn.commit()
                        self.goto(ClassPage)
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

#Page for logging in existing users. Fetches password from database.    
class LoginPage(Page):
    def __init__(self,root):
        super().__init__(root)

        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.invalid=tk.StringVar()
        #Add styling
        ttk.Button(self.frame, text="< Back", command=lambda:self.goto(LoggedOutPage)).grid(column=0,row=0)
        ttk.Label(self.frame,text="Log in:").grid(column=1,row=0)
        ttk.Label(self.frame, text="Email:").grid(column=1,row=1)
        ttk.Entry(self.frame, textvariable=self.email).grid(column=2,row=1,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=1,row=2)
        ttk.Entry(self.frame, textvariable=self.password,show='*').grid(column=2,row=2,columnspan=2)
        ttk.Button(self.frame, text="Login",command=self.validate).grid(column=1,row=3)
        ttk.Label(self.frame, textvariable=self.invalid).grid(column=1,row=4)
    def validate(self):
        #Fetches encrypted correct password from databse
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT Password from Teachers WHERE Email = ?",(self.email.get(),))
            correctPass=cur.fetchone()
        #correctPass is NoneType when the email entered is not in the database
        try:
            correctPass=correctPass[0]
            #Checks that the password entered matches the encrypted correct password
            if bcrypt.checkpw(self.password.get().encode('utf-8'), correctPass):
                self.goto(ClassPage)
        #Error messages
            else:
                self.invalid.set("Password incorrect.")
        except:
            self.invalid.set("Email is not registered.")



#Page for displaying the seating chart and menu of tools.
class ClassPage(Page):
    def __init__(self,root):
        super().__init__(root)

        self.CANVASWIDTH = 900
        self.CANVASHEIGHT = 900

        self.displayMenu()
        canvas = tk.Canvas(self.frame,
                       width=self.CANVASWIDTH,
                       height=self.CANVASHEIGHT,
                       background='white')
        canvas.grid(column=0,row=1,columnspan=5,rowspan=5)
        Seat(canvas)
    
    def displayMenu(self):
        menubar = tk.Menu(self.root,background="lightyellow")
        self.root['menu'] = menubar

        #"Class" dropdown menu
        menu_class = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_class, label='Class')
        menu_class.add_command(label='Switch class', command="")
        menu_class.add_command(label="Save", command="")
        menu_class.add_command(label="Edit class",command="")

        #"Students" dropdown menu
        menu_students = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_students, label="Students")
        menu_students.add_command(label='Edit students', command ="")

        #"Arrange" dropdown menu
        menu_arrange = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_arrange, label="Arrange")
        
        #Tick box to choose to hide or show names of students
        hideNames=tk.StringVar()
        menubar.add_checkbutton(label="Hide names", variable=hideNames, onvalue=True, offvalue=False)

        #Tick box to choose to hide or show images of students
        hideImages=tk.StringVar()
        menubar.add_checkbutton(label="Hide images", variable=hideImages, onvalue=True, offvalue=False)

        
#Base class for all widgets to inherit from
class Widget:
    def __init__(self,canvas,x,y,rot):
        self.x=x
        self.y=y
        self.dir=rot
        self.canvas=canvas
    def move(self,event):
        if event.x<int(self.canvas["width"]) and event.y<int(self.canvas["height"]):
            self.canvas.move(self.id,event.x-self.x,event.y-self.y)
            self.x=event.x
            self.y=event.y
        
        
    def rotate(self):
        print("yup") #

class Seat(Widget):
    def __init__(self,canvas,x=0,y=0,rot='S'):
        super().__init__(canvas,x,y,rot)
        self.id=self.canvas.create_rectangle(self.x,self.y,self.x+100,self.y +100, fill='red', outline='blue',tags='seat')
        self.canvas.tag_bind(self.id,"<B1-Motion>", self.move)
        

class POI(Widget):
    def __init__(self):
        super.__init__()

class Student(Widget):
    def __init__(self):
        super.__init__()
    def getData(self,id):
        #<<<<-----------------------------------------------------------------
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT FirstName, LastName, PhotoPath FROM Students WHERE StudentID = ?",(id,))
            data=cur.fetchone()
        self.firstName=data[0]
        self.lastName=data[1]
        self.photoPath=data[2]
        #Tags

#Subroutines

def main():
    root = tk.Tk()
    root.title( "Seating Planner" )
    root.option_add('*tearOff', False)
    ClassPage(root)

    root.mainloop()

#================================================
main()