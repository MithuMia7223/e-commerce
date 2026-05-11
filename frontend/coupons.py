from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class CouponPage:

    def __init__(self, app):
        self.app = app
        self.result_frame = None
        self.show_coupons()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_coupons(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Coupons & Discounts", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )

        if self.app.user["role"] == "admin":
            ttk.Button(top, text="Create Coupon", command=self.show_create_coupon).pack(
                side=RIGHT, padx=5
            )

        ttk.Button(top, text="Validate Coupon", command=self.show_validate_coupon).pack(
            side=RIGHT, padx=5
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for coupons
        columns = ("ID", "Code", "Type", "Value", "Min Amount", "Expires", "Status")
        self.tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.app.main_frame)
        btn_frame.pack(fill=X, pady=5)

        if self.app.user["role"] == "admin":
            ttk.Button(btn_frame, text="Edit", command=self.edit_coupon).pack(
                side=LEFT, padx=5
            )
            ttk.Button(btn_frame, text="Delete", command=self.delete_coupon).pack(
                side=LEFT, padx=5
            )

        self.load_coupons()

    def load_coupons(self):
        if self.app.user["role"] == "admin":
            response = requests.get(
                f"{self.app.api_base}/coupons/", headers=self.headers()
            )
        else:
            response = requests.get(
                f"{self.app.api_base}/coupons/active", headers=self.headers()
            )

        if response.status_code == 200:
            coupons = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for coupon in coupons:
                self.tree.insert(
                    "",
                    END,
                    values=(
                        coupon["id"],
                        coupon["code"],
                        coupon["discount_type"],
                        f"{coupon['discount_value']}{'%' if coupon['discount_type'] == 'percentage' else '$'}",
                        f"${coupon['minimum_amount']}",
                        coupon["expires_at"][:10],
                        "Active" if coupon["is_active"] else "Inactive",
                    ),
                )

    def show_create_coupon(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Create Coupon", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_coupons).pack(side=RIGHT, padx=5)

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Form fields
        ttk.Label(form, text="Coupon Code:").grid(row=0, column=0, sticky=W, pady=5)
        self.code_entry = ttk.Entry(form, width=40)
        self.code_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Discount Type:").grid(row=1, column=0, sticky=W, pady=5)
        self.discount_type_var = StringVar(value="percentage")
        ttk.Radiobutton(
            form, text="Percentage", variable=self.discount_type_var, value="percentage"
        ).grid(row=1, column=1, sticky=W)
        ttk.Radiobutton(
            form, text="Fixed Amount", variable=self.discount_type_var, value="fixed"
        ).grid(row=1, column=1, sticky=E)

        ttk.Label(form, text="Discount Value:").grid(row=2, column=0, sticky=W, pady=5)
        self.value_entry = ttk.Entry(form, width=40)
        self.value_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Minimum Amount:").grid(row=3, column=0, sticky=W, pady=5)
        self.min_amount_entry = ttk.Entry(form, width=40)
        self.min_amount_entry.insert(0, "0")
        self.min_amount_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Usage Limit:").grid(row=4, column=0, sticky=W, pady=5)
        self.usage_limit_entry = ttk.Entry(form, width=40)
        self.usage_limit_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="Expires At:").grid(row=5, column=0, sticky=W, pady=5)
        self.expires_entry = ttk.Entry(form, width=40)
        self.expires_entry.insert(0, "2024-12-31T23:59:59")
        self.expires_entry.grid(row=5, column=1, pady=5)

        ttk.Button(form, text="Create Coupon", command=self.create_coupon).grid(
            row=6, column=1, pady=20
        )

    def create_coupon(self):
        data = {
            "code": self.code_entry.get(),
            "discount_type": self.discount_type_var.get(),
            "discount_value": float(self.value_entry.get()),
            "minimum_amount": float(self.min_amount_entry.get()),
            "usage_limit": (
                int(self.usage_limit_entry.get())
                if self.usage_limit_entry.get()
                else None
            ),
            "expires_at": self.expires_entry.get(),
        }

        response = requests.post(
            f"{self.app.api_base}/coupons/", json=data, headers=self.headers()
        )

        if response.status_code == 201:
            messagebox.showinfo("Success", "Coupon created successfully!")
            self.show_coupons()
        else:
            messagebox.showerror("Error", response.text)

    def show_validate_coupon(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Validate Coupon", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_coupons).pack(side=RIGHT, padx=5)

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        ttk.Label(form, text="Coupon Code:").grid(row=0, column=0, sticky=W, pady=5)
        self.validate_code_entry = ttk.Entry(form, width=40)
        self.validate_code_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Cart Total:").grid(row=1, column=0, sticky=W, pady=5)
        self.cart_total_entry = ttk.Entry(form, width=40)
        self.cart_total_entry.insert(0, "0")
        self.cart_total_entry.grid(row=1, column=1, pady=5)

        ttk.Button(form, text="Validate Coupon", command=self.validate_coupon).grid(
            row=2, column=1, pady=20
        )

        # Result frame
        self.result_frame = ttk.LabelFrame(form, text="Validation Result")
        self.result_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky=EW)

    def validate_coupon(self):
        coupon_code = self.validate_code_entry.get()
        cart_total = float(self.cart_total_entry.get())

        response = requests.post(
            f"{self.app.api_base}/coupons/validate",
            params={"coupon_code": coupon_code, "cart_total": cart_total},
            headers=self.headers(),
        )

        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if response.status_code == 200:
            result = response.json()
            ttk.Label(
                self.result_frame,
                text="✅ Coupon Valid!",
                font=("Arial", 12, "bold"),
                foreground="green",
            ).pack()
            ttk.Label(
                self.result_frame,
                text=f"Discount Amount: ${result['discount_amount']:.2f}",
            ).pack()
            ttk.Label(
                self.result_frame, text=f"Final Total: ${result['final_total']:.2f}"
            ).pack()
        else:
            ttk.Label(
                self.result_frame,
                text="❌ Invalid Coupon",
                font=("Arial", 12, "bold"),
                foreground="red",
            ).pack()
            ttk.Label(self.result_frame, text=response.text).pack()

    def get_selected_coupon_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a coupon")
            return None
        return self.tree.item(selected[0])["values"][0]

    def edit_coupon(self):
        coupon_id = self.get_selected_coupon_id()
        if not coupon_id:
            return

        # Get coupon details and populate form for editing
        response = requests.get(f"{self.app.api_base}/coupons/", headers=self.headers())
        if response.status_code == 200:
            coupons = response.json()
            coupon = next((c for c in coupons if c["id"] == coupon_id), None)

            if coupon:
                self.show_edit_form(coupon)

    def show_edit_form(self, coupon):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Edit Coupon", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_coupons).pack(side=RIGHT, padx=5)

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Form fields with existing data
        ttk.Label(form, text="Coupon Code:").grid(row=0, column=0, sticky=W, pady=5)
        self.code_entry = ttk.Entry(form, width=40)
        self.code_entry.insert(0, coupon["code"])
        self.code_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Discount Type:").grid(row=1, column=0, sticky=W, pady=5)
        self.discount_type_var = StringVar(value=coupon["discount_type"])
        ttk.Radiobutton(
            form, text="Percentage", variable=self.discount_type_var, value="percentage"
        ).grid(row=1, column=1, sticky=W)
        ttk.Radiobutton(
            form, text="Fixed Amount", variable=self.discount_type_var, value="fixed"
        ).grid(row=1, column=1, sticky=E)

        ttk.Label(form, text="Discount Value:").grid(row=2, column=0, sticky=W, pady=5)
        self.value_entry = ttk.Entry(form, width=40)
        self.value_entry.insert(0, str(coupon["discount_value"]))
        self.value_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Minimum Amount:").grid(row=3, column=0, sticky=W, pady=5)
        self.min_amount_entry = ttk.Entry(form, width=40)
        self.min_amount_entry.insert(0, str(coupon["minimum_amount"]))
        self.min_amount_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Usage Limit:").grid(row=4, column=0, sticky=W, pady=5)
        self.usage_limit_entry = ttk.Entry(form, width=40)
        if coupon["usage_limit"]:
            self.usage_limit_entry.insert(0, str(coupon["usage_limit"]))
        self.usage_limit_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="Expires At:").grid(row=5, column=0, sticky=W, pady=5)
        self.expires_entry = ttk.Entry(form, width=40)
        self.expires_entry.insert(0, coupon["expires_at"])
        self.expires_entry.grid(row=5, column=1, pady=5)

        ttk.Button(
            form, text="Update Coupon", command=lambda: self.update_coupon(coupon["id"])
        ).grid(row=6, column=1, pady=20)

    def update_coupon(self, coupon_id):
        data = {
            "code": self.code_entry.get(),
            "discount_type": self.discount_type_var.get(),
            "discount_value": float(self.value_entry.get()),
            "minimum_amount": float(self.min_amount_entry.get()),
            "usage_limit": (
                int(self.usage_limit_entry.get())
                if self.usage_limit_entry.get()
                else None
            ),
            "expires_at": self.expires_entry.get(),
        }

        response = requests.put(
            f"{self.app.api_base}/coupons/{coupon_id}",
            json=data,
            headers=self.headers(),
        )

        if response.status_code == 200:
            messagebox.showinfo("Success", "Coupon updated successfully!")
            self.show_coupons()
        else:
            messagebox.showerror("Error", response.text)

    def delete_coupon(self):
        coupon_id = self.get_selected_coupon_id()
        if not coupon_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this coupon?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/coupons/{coupon_id}", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Coupon deleted successfully!")
                self.load_coupons()
            else:
                messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
