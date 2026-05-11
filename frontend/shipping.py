from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class ShippingPage:

    def __init__(self, app):
        self.app = app
        self.show_shipping_addresses()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_shipping_addresses(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Shipping Addresses", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Add Address", command=self.show_add_address).pack(
            side=RIGHT, padx=5
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for addresses
        columns = ("ID", "Name", "Address", "City", "Phone", "Default")
        self.tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.app.main_frame)
        btn_frame.pack(fill=X, pady=5)

        ttk.Button(btn_frame, text="Edit", command=self.edit_address).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_address).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Set Default", command=self.set_default).pack(
            side=LEFT, padx=5
        )

        self.load_addresses()

    def load_addresses(self):
        response = requests.get(
            f"{self.app.api_base}/shipping/", headers=self.headers()
        )

        if response.status_code == 200:
            addresses = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for addr in addresses:
                self.tree.insert(
                    "",
                    END,
                    values=(
                        addr["id"],
                        addr["name"],
                        f"{addr['address']}, {addr['city']}, {addr['postal_code']}",
                        addr["city"],
                        addr["phone"],
                        "Yes" if addr["is_default"] else "No",
                    ),
                )

    def show_add_address(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Add Shipping Address", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_shipping_addresses).pack(
            side=RIGHT, padx=5
        )

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Form fields
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Address:").grid(row=1, column=0, sticky=W, pady=5)
        self.address_entry = ttk.Entry(form, width=40)
        self.address_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="City:").grid(row=2, column=0, sticky=W, pady=5)
        self.city_entry = ttk.Entry(form, width=40)
        self.city_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Postal Code:").grid(row=3, column=0, sticky=W, pady=5)
        self.postal_entry = ttk.Entry(form, width=40)
        self.postal_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Country:").grid(row=4, column=0, sticky=W, pady=5)
        self.country_entry = ttk.Entry(form, width=40)
        self.country_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="Phone:").grid(row=5, column=0, sticky=W, pady=5)
        self.phone_entry = ttk.Entry(form, width=40)
        self.phone_entry.grid(row=5, column=1, pady=5)

        self.default_var = BooleanVar()
        ttk.Checkbutton(
            form, text="Set as Default Address", variable=self.default_var
        ).grid(row=6, column=1, sticky=W, pady=10)

        ttk.Button(form, text="Save Address", command=self.save_address).grid(
            row=7, column=1, pady=20
        )

    def save_address(self):
        data = {
            "name": self.name_entry.get(),
            "address": self.address_entry.get(),
            "city": self.city_entry.get(),
            "postal_code": self.postal_entry.get(),
            "country": self.country_entry.get(),
            "phone": self.phone_entry.get(),
            "is_default": self.default_var.get(),
        }

        response = requests.post(
            f"{self.app.api_base}/shipping/", json=data, headers=self.headers()
        )

        if response.status_code == 201:
            messagebox.showinfo("Success", "Shipping address added successfully!")
            self.show_shipping_addresses()
        else:
            messagebox.showerror("Error", response.text)

    def get_selected_address_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an address")
            return None
        return self.tree.item(selected[0])["values"][0]

    def edit_address(self):
        addr_id = self.get_selected_address_id()
        if not addr_id:
            return

        # Get address details and populate form for editing
        response = requests.get(
            f"{self.app.api_base}/shipping/", headers=self.headers()
        )
        if response.status_code == 200:
            addresses = response.json()
            addr = next((a for a in addresses if a["id"] == addr_id), None)

            if addr:
                self.show_edit_form(addr)

    def show_edit_form(self, addr):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Edit Shipping Address", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_shipping_addresses).pack(
            side=RIGHT, padx=5
        )

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Form fields with existing data
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(form, width=40)
        self.name_entry.insert(0, addr["name"])
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Address:").grid(row=1, column=0, sticky=W, pady=5)
        self.address_entry = ttk.Entry(form, width=40)
        self.address_entry.insert(0, addr["address"])
        self.address_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="City:").grid(row=2, column=0, sticky=W, pady=5)
        self.city_entry = ttk.Entry(form, width=40)
        self.city_entry.insert(0, addr["city"])
        self.city_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Postal Code:").grid(row=3, column=0, sticky=W, pady=5)
        self.postal_entry = ttk.Entry(form, width=40)
        self.postal_entry.insert(0, addr["postal_code"])
        self.postal_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Country:").grid(row=4, column=0, sticky=W, pady=5)
        self.country_entry = ttk.Entry(form, width=40)
        self.country_entry.insert(0, addr["country"])
        self.country_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="Phone:").grid(row=5, column=0, sticky=W, pady=5)
        self.phone_entry = ttk.Entry(form, width=40)
        self.phone_entry.insert(0, addr["phone"])
        self.phone_entry.grid(row=5, column=1, pady=5)

        self.default_var = BooleanVar(value=addr["is_default"])
        ttk.Checkbutton(
            form, text="Set as Default Address", variable=self.default_var
        ).grid(row=6, column=1, sticky=W, pady=10)

        ttk.Button(
            form, text="Update Address", command=lambda: self.update_address(addr["id"])
        ).grid(row=7, column=1, pady=20)

    def update_address(self, addr_id):
        data = {
            "name": self.name_entry.get(),
            "address": self.address_entry.get(),
            "city": self.city_entry.get(),
            "postal_code": self.postal_entry.get(),
            "country": self.country_entry.get(),
            "phone": self.phone_entry.get(),
            "is_default": self.default_var.get(),
        }

        response = requests.put(
            f"{self.app.api_base}/shipping/{addr_id}", json=data, headers=self.headers()
        )

        if response.status_code == 200:
            messagebox.showinfo("Success", "Shipping address updated successfully!")
            self.show_shipping_addresses()
        else:
            messagebox.showerror("Error", response.text)

    def delete_address(self):
        addr_id = self.get_selected_address_id()
        if not addr_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this address?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/shipping/{addr_id}", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Shipping address deleted successfully!")
                self.load_addresses()
            else:
                messagebox.showerror("Error", response.text)

    def set_default(self):
        addr_id = self.get_selected_address_id()
        if not addr_id:
            return

        response = requests.get(
            f"{self.app.api_base}/shipping/", headers=self.headers()
        )
        if response.status_code == 200:
            addresses = response.json()
            addr = next((a for a in addresses if a["id"] == addr_id), None)

            if addr:
                addr["is_default"] = True
                response = requests.put(
                    f"{self.app.api_base}/shipping/{addr_id}",
                    json=addr,
                    headers=self.headers(),
                )

                if response.status_code == 200:
                    messagebox.showinfo(
                        "Success", "Default address updated successfully!"
                    )
                    self.load_addresses()
                else:
                    messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
