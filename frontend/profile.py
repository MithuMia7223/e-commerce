from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class ProfilePage:

    def __init__(self, app):
        self.app = app
        self.show_profile()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_profile(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="User Profile", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Profile info frame
        info_frame = ttk.LabelFrame(self.app.main_frame, text="Basic Information")
        info_frame.pack(fill=X, padx=10, pady=10)

        # Profile image
        image_frame = ttk.Frame(info_frame)
        image_frame.pack(side=RIGHT, padx=10, pady=5)

        # Placeholder for profile image
        self.profile_image_label = ttk.Label(image_frame, text="👤", font=("Arial", 24))
        self.profile_image_label.pack()

        ttk.Label(
            info_frame,
            text=f"Name: {self.app.user.get('first_name', '')} {self.app.user.get('last_name', '')}",
        ).pack(anchor=W, pady=2)
        ttk.Label(info_frame, text=f"Email: {self.app.user.get('email', '')}").pack(
            anchor=W, pady=2
        )
        ttk.Label(info_frame, text=f"Role: {self.app.user.get('role', '')}").pack(
            anchor=W, pady=2
        )

        # Extended profile frame
        self.extended_frame = ttk.LabelFrame(
            self.app.main_frame, text="Extended Profile", padding=20
        )
        self.extended_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.app.main_frame)
        btn_frame.pack(fill=X, pady=10)

        ttk.Button(btn_frame, text="Edit Profile", command=self.show_edit_profile).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Refresh", command=self.show_profile).pack(
            side=LEFT, padx=5
        )

        self.load_extended_profile()

    def load_extended_profile(self):
        response = requests.get(f"{self.app.api_base}/profile/", headers=self.headers())

        if response.status_code == 200:
            profile = response.json()

            # Clear previous content
            for widget in self.extended_frame.winfo_children():
                widget.destroy()

            if profile:
                # Display profile information
                info_grid = ttk.Frame(self.extended_frame)
                info_grid.pack(fill=BOTH, expand=True)

                row = 0
                if profile.get("first_name"):
                    ttk.Label(
                        info_grid, text="First Name:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(info_grid, text=profile["first_name"]).grid(
                        row=row, column=1, sticky=W, pady=2, padx=5
                    )
                    row += 1

                if profile.get("last_name"):
                    ttk.Label(
                        info_grid, text="Last Name:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(info_grid, text=profile["last_name"]).grid(
                        row=row, column=1, sticky=W, pady=2, padx=5
                    )
                    row += 1

                if profile.get("phone"):
                    ttk.Label(
                        info_grid, text="Phone:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(info_grid, text=profile["phone"]).grid(
                        row=row, column=1, sticky=W, pady=2, padx=5
                    )
                    row += 1

                if profile.get("date_of_birth"):
                    ttk.Label(
                        info_grid, text="Date of Birth:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(info_grid, text=profile["date_of_birth"][:10]).grid(
                        row=row, column=1, sticky=W, pady=2, padx=5
                    )
                    row += 1

                if profile.get("gender"):
                    ttk.Label(
                        info_grid, text="Gender:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(info_grid, text=profile["gender"]).grid(
                        row=row, column=1, sticky=W, pady=2, padx=5
                    )
                    row += 1

                if profile.get("bio"):
                    ttk.Label(info_grid, text="Bio:", font=("Arial", 10, "bold")).grid(
                        row=row, column=0, sticky=W, pady=2, padx=5
                    )
                    bio_text = Text(info_grid, width=40, height=4, wrap=WORD)
                    bio_text.grid(row=row, column=1, sticky=W, pady=2, padx=5)
                    bio_text.insert("1.0", profile["bio"])
                    bio_text.config(state=DISABLED)
                    row += 1

                if profile.get("avatar_url"):
                    ttk.Label(
                        info_grid, text="Avatar URL:", font=("Arial", 10, "bold")
                    ).grid(row=row, column=0, sticky=W, pady=2, padx=5)
                    ttk.Label(
                        info_grid, text=profile["avatar_url"], wraplength=300
                    ).grid(row=row, column=1, sticky=W, pady=2, padx=5)
            else:
                ttk.Label(
                    self.extended_frame,
                    text="No extended profile information available. Click 'Edit Profile' to add details.",
                    font=("Arial", 10, "italic"),
                ).pack(pady=20)

    def show_edit_profile(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Edit Profile", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_profile).pack(side=RIGHT, padx=5)

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Load current profile data
        response = requests.get(f"{self.app.api_base}/profile/", headers=self.headers())
        current_profile = response.json() if response.status_code == 200 else {}

        # Form fields
        ttk.Label(form, text="First Name:").grid(row=0, column=0, sticky=W, pady=5)
        self.first_name_entry = ttk.Entry(form, width=40)
        self.first_name_entry.insert(0, current_profile.get("first_name", ""))
        self.first_name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Last Name:").grid(row=1, column=0, sticky=W, pady=5)
        self.last_name_entry = ttk.Entry(form, width=40)
        self.last_name_entry.insert(0, current_profile.get("last_name", ""))
        self.last_name_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Phone:").grid(row=2, column=0, sticky=W, pady=5)
        self.phone_entry = ttk.Entry(form, width=40)
        self.phone_entry.insert(0, current_profile.get("phone", ""))
        self.phone_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Avatar URL:").grid(row=3, column=0, sticky=W, pady=5)
        self.avatar_entry = ttk.Entry(form, width=40)
        self.avatar_entry.insert(0, current_profile.get("avatar_url", ""))
        self.avatar_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Date of Birth:").grid(row=4, column=0, sticky=W, pady=5)
        self.dob_entry = ttk.Entry(form, width=40)
        self.dob_entry.insert(
            0,
            (
                current_profile.get("date_of_birth", "")[:10]
                if current_profile.get("date_of_birth")
                else ""
            ),
        )
        self.dob_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="Gender:").grid(row=5, column=0, sticky=W, pady=5)
        self.gender_var = StringVar(value=current_profile.get("gender", ""))
        gender_combo = ttk.Combobox(
            form,
            textvariable=self.gender_var,
            values=["Male", "Female", "Other", "Prefer not to say"],
            width=37,
        )
        gender_combo.grid(row=5, column=1, pady=5)

        ttk.Label(form, text="Bio:").grid(row=6, column=0, sticky=W, pady=5)
        self.bio_text = Text(form, width=40, height=5, wrap=WORD)
        self.bio_text.grid(row=6, column=1, pady=5)
        if current_profile.get("bio"):
            self.bio_text.insert("1.0", current_profile["bio"])

        ttk.Button(form, text="Save Profile", command=self.save_profile).grid(
            row=7, column=1, pady=20
        )

    def save_profile(self):
        data = {
            "first_name": self.first_name_entry.get() or None,
            "last_name": self.last_name_entry.get() or None,
            "phone": self.phone_entry.get() or None,
            "avatar_url": self.avatar_entry.get() or None,
            "date_of_birth": self.dob_entry.get() or None,
            "gender": self.gender_var.get() or None,
            "bio": self.bio_text.get("1.0", END).strip() or None,
        }

        response = requests.post(
            f"{self.app.api_base}/profile/", json=data, headers=self.headers()
        )

        if response.status_code in [200, 201]:
            messagebox.showinfo("Success", "Profile updated successfully!")
            self.show_profile()
        else:
            messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
