import tkinter 
from tkinter import ttk

class Page:
    def __init__(self):
        self.frame = ttk.Frame(root)
        self.frame.grid()
        self.ok="ok"
    def goto(self, page):
        self.frame.destroy()
        page.frame = ttk.Frame(root)
        page.frame.grid()
        page.display(page)


class LoggedOutPage(Page):
    def display(self):
        ttk.Label(self.frame, text="Please register or log in to access your seating charts").grid(column=1,row=0,sticky=(tkinter.W,tkinter.E))
        ttk.Button(self.frame, text="Register", command=lambda:self.goto(RegisterPage)).grid(column=1,row=1)
        ttk.Button(self.frame, text="Log in", command=lambda:self.goto(LoginPage)).grid(column=1,row=2,sticky=tkinter.S)
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
        ttk.Entry(self.frame, textvariable=self.password).grid(column=1,row=3,columnspan=2)
        ttk.Label(self.frame, text="Confirm password:").grid(column=0,row=4)
        ttk.Entry(self.frame, textvariable=self.password2).grid(column=1,row=4,columnspan=2)
        ttk.Button(self.frame, text="Register",command="").grid(column=1,row=5)

class LoginPage:
    def display(self):
        email = tkinter.StringVar()
        password = tkinter.StringVar()
        #Add back button
        ttk.Label(self.frame, text="Email:").grid(column=0,row=0)
        ttk.Entry(self.frame, textvariable=email).grid(column=1,row=0,columnspan=2)
        ttk.Label(self.frame, text="Password:").grid(column=0,row=1)
        ttk.Entry(self.frame, textvariable=password).grid(column=1,row=1,columnspan=2)
        ttk.Button(self.frame, text="Login",command="").grid(column=1,row=2)


root = tkinter.Tk()
root.title( "Seating Planner" )
LoggedOutPage().display()
root.mainloop()
