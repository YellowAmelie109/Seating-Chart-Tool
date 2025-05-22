#Add the ability to add seats
#Students pop-up
#POI
#Students
#Class list (switch+login)
#Press enter key on login/register
#Sepearate register validation into different methods and move constants
#Make password regex format a constant

#Window needs to be resized when going to pages and text display(password invalid format text)
#Styling

import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
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
    def __init__(self,root:tk.Tk):
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

    def validate(self):
        ''''''


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

        self.CANVASWIDTH =  900
        self.CANVASHEIGHT =  900

        self.displayMenu()
        self.canvas = tk.Canvas(self.frame,
                       width=self.CANVASWIDTH,
                       height=self.CANVASHEIGHT,
                       background='white')
        self.canvas.grid(column=0,row=1,columnspan=5,rowspan=5)
        maxSeats=10
        for i in range(maxSeats):
            Seat(self.canvas,x=i*(self.CANVASWIDTH/maxSeats))
        Student(self.canvas,y=100)
    
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
        menubar.add_checkbutton(label="Hide names", variable=hideNames, onvalue=True, offvalue=False,command="")

        #Tick box to choose to hide or show images of students
        hideImages=tk.StringVar()
        menubar.add_checkbutton(label="Hide images", variable=hideImages, onvalue=True, offvalue=False,command="")

        #menubar.add_command(label="Add seat")

        
#Base class for all widgets to inherit from
class Widget:
    def __init__(self,canvas:tk.Canvas,x,y,rot,width,height):
        self.x=x
        self.y=y
        self.dir=rot
        self.canvas=canvas
        self.width=width
        self.height=height
    def move(self,event:tk.Event):
        #Prevents widget being moved outside of canvas
        if event.x<int(self.canvas["width"]) and event.y<int(self.canvas["height"]) and event.x>0 and event.y>0:
            #Moves so that the mouse is the center
            self.canvas.move(self.tag,event.x-self.x-self.width/2,event.y-self.y-self.width/2) 
            self.x=self.canvas.coords(self.id)[0]
            self.y=self.canvas.coords(self.id)[1]
        
        
    def rotate(self,event):
        match self.dir:
            case 'W':
                self.dir='N'
            case 'N':
                self.dir='E'
            case 'S':
                self.dir='W'
            case 'E':
                self.dir='S'
        self.displayDirection()

class Seat(Widget):
    #Keeping track of total seats in the class to prevent more seats than maxSeats in database from being created
    seats=0
    def __init__(self,canvas,x=0,y=0,rot='S',width=100):
        super().__init__(canvas,x,y,rot,width,width)
        Seat.seats+=1

        self.id=self.canvas.create_rectangle(self.x,self.y,self.x+self.width,self.y +self.width, fill='red', outline='blue',tags='seat')
        #Rectangles and arrows have the same tag so they move together when dragged
        self.tag="seat"+str(self.id)
        self.canvas.addtag_withtag(self.tag,self.id)

        self.textid=self.canvas.create_text(self.x,self.y,tags=('seat',self.tag),font=("Arial", 20))
        self.displayDirection()

        self.canvas.tag_bind(self.tag,"<B1-Motion>", self.move) #Hold left click and drag to move widget
        self.canvas.tag_bind(self.tag,"<ButtonPress-3>",self.rotate) #Press right click to rotate arrow

    def displayDirection(self):
        match self.dir:
            case 'N':
                self.canvas.itemconfigure(self.textid,text='↑')
                self.canvas.coords(self.textid, self.x+self.width/2, self.y)
            case 'E':
                self.canvas.itemconfigure(self.textid,text='→')
                self.canvas.coords(self.textid, self.x+self.width, self.y+self.width/2)
            case 'W':
                self.canvas.itemconfigure(self.textid,text='←')
                self.canvas.coords(self.textid, self.x, self.y+self.width/2)
            case 'S':
                self.canvas.itemconfigure(self.textid,text='↓')
                self.canvas.coords(self.textid, self.x+self.width/2, self.y+self.width)
            case _:
                self.canvas.itemconfigure(self.textid,text='↓')
                self.canvas.coords(self.textid, self.x+self.width/2, self.y+self.width)
                self.dir='S'

        

class POI(Widget):
    def __init__(self):
        super().__init__()

class Student(Widget):
    def __init__(self,canvas,x=0,y=0,rot='S',width=75):
        super().__init__(canvas,x,y,rot,width,width)

        self.id=self.canvas.create_rectangle(self.x,self.y,self.x+self.width,self.y +self.width, fill='#ffdb32', outline='black',tags='student')
        self.tag="student"+str(self.id)
        self.canvas.addtag_withtag(self.tag,self.id)

        #self.image=ImageTk.PhotoImage(Image.open("DatabaseAnalysis.png"))
        #self.canvas.create_image(self.x,self.y,image=self.image,anchor=tk.NW)

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