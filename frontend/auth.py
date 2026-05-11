import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests
from dashboard import DashboardPage


class AuthPage:

    def __init__(self, app):

        self.app = app

        self.show_login()

    def clear(self):

        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def show_login(self):

        self.clear()

        frame = ttk.Frame(self.app.main_frame, padding=30)
        frame.pack(expand=True)

        ttk.Label(frame, text="Login", font=("Arial", 20, "bold")).pack(pady=10)

        ttk.Label(frame, text="Username:").pack(pady=5)
        self.username = ttk.Entry(frame, width=30)
        self.username.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(pady=5)
        self.password = ttk.Entry(frame, width=30, show="*")
        self.password.pack(pady=5)

        ttk.Button(frame, text="Login", command=self.login).pack(pady=20)
        ttk.Button(
            frame, text="Don't have an account? Sign Up", command=self.show_signup
        ).pack(pady=5)

    def show_signup(self):

        self.clear()

        frame = ttk.Frame(self.app.main_frame, padding=30)
        frame.pack(expand=True)

        ttk.Label(frame, text="Create Account", font=("Arial", 28, "bold")).pack(
            pady=20
        )

        ttk.Label(frame, text="Username").pack()

        self.s_username = ttk.Entry(frame, width=40)
        self.s_username.pack()

        ttk.Label(frame, text="Email").pack()

        self.s_email = ttk.Entry(frame, width=40)
        self.s_email.pack()

        ttk.Label(frame, text="Password").pack()

        self.s_password = ttk.Entry(frame, show="*", width=40)
        self.s_password.pack()

        ttk.Button(frame, text="Register", command=self.signup).pack(pady=10)

        ttk.Button(frame, text="Back Login", command=self.show_login).pack()

    def login(self):

        response = requests.post(
            f"{self.app.api_base}/users/login",
            json={
                "username_or_email": self.username.get(),
                "password": self.password.get(),
            },
        )

        if response.status_code == 200:

            data = response.json()

            self.app.token = data["access_token"]
            self.app.user = data["user"]

            DashboardPage(self.app)

        else:
            messagebox.showerror("Error", response.text)

    def signup(self):

        response = requests.post(
            f"{self.app.api_base}/users/register",
            json={
                "username": self.s_username.get(),
                "email": self.s_email.get(),
                "password": self.s_password.get(),
            },
        )

        if response.status_code == 201:

            messagebox.showinfo("Success", "Registration Success")

            self.show_login()

        else:
            messagebox.showerror("Error", response.text)
