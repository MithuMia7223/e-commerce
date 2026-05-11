from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class RefundPage:

    def __init__(self, app):
        self.app = app
        self.show_refunds()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_refunds(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Refunds & Returns", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )

        if self.app.user["role"] == "admin":
            ttk.Button(
                top, text="View All Refunds", command=self.show_all_refunds
            ).pack(side=RIGHT, padx=5)

        ttk.Button(top, text="Request Refund", command=self.show_request_refund).pack(
            side=RIGHT, padx=5
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for refunds
        columns = (
            "ID",
            "Order ID",
            "Product ID",
            "Quantity",
            "Status",
            "Amount",
            "Date",
        )
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

        ttk.Button(btn_frame, text="View Details", command=self.view_details).pack(
            side=LEFT, padx=5
        )

        if self.app.user["role"] == "admin":
            ttk.Button(btn_frame, text="Approve", command=self.approve_refund).pack(
                side=LEFT, padx=5
            )
            ttk.Button(btn_frame, text="Reject", command=self.reject_refund).pack(
                side=LEFT, padx=5
            )

        self.load_refunds()

    def load_refunds(self):
        if self.app.user["role"] == "admin":
            response = requests.get(
                f"{self.app.api_base}/refunds/admin/all", headers=self.headers()
            )
        else:
            response = requests.get(
                f"{self.app.api_base}/refunds/", headers=self.headers()
            )

        if response.status_code == 200:
            refunds = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for refund in refunds:
                self.tree.insert(
                    "",
                    END,
                    values=(
                        refund["id"],
                        refund["order_id"],
                        refund["product_id"],
                        refund["quantity"],
                        refund["status"],
                        f"${refund['refund_amount'] or 0:.2f}",
                        refund["created_at"][:10],
                    ),
                )

    def show_request_refund(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Request Refund", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_refunds).pack(side=RIGHT, padx=5)

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Load user orders
        ttk.Label(form, text="Order ID:").grid(row=0, column=0, sticky=W, pady=5)
        self.order_var = StringVar()
        self.order_combo = ttk.Combobox(
            form, textvariable=self.order_var, state="readonly"
        )
        self.order_combo.grid(row=0, column=1, pady=5)
        self.order_combo.bind("<<ComboboxSelected>>", self.load_order_products)

        ttk.Label(form, text="Product:").grid(row=1, column=0, sticky=W, pady=5)
        self.product_var = StringVar()
        self.product_combo = ttk.Combobox(
            form, textvariable=self.product_var, state="readonly"
        )
        self.product_combo.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Quantity:").grid(row=2, column=0, sticky=W, pady=5)
        self.quantity_entry = ttk.Entry(form, width=40)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Reason:").grid(row=3, column=0, sticky=W, pady=5)
        self.reason_text = Text(form, width=40, height=5)
        self.reason_text.grid(row=3, column=1, pady=5)

        ttk.Button(
            form, text="Submit Refund Request", command=self.submit_refund_request
        ).grid(row=4, column=1, pady=20)

        self.load_orders()

    def load_orders(self):
        response = requests.get(f"{self.app.api_base}/orders/", headers=self.headers())

        if response.status_code == 200:
            orders = response.json()
            order_list = [f"{o['id']} - {o['status']}" for o in orders]
            self.order_combo["values"] = order_list

            if order_list:
                self.order_combo.current(0)

    def load_order_products(self, event=None):
        selected_order = self.order_var.get()
        if not selected_order:
            return

        order_id = int(selected_order.split(" - ")[0])

        response = requests.get(
            f"{self.app.api_base}/orders/{order_id}", headers=self.headers()
        )

        if response.status_code == 200:
            order = response.json()
            product_list = [
                f"{item['product_id']} - Product {item['product_id']}"
                for item in order.get("items", [])
            ]
            self.product_combo["values"] = product_list

            if product_list:
                self.product_combo.current(0)

    def submit_refund_request(self):
        selected_order = self.order_var.get()
        selected_product = self.product_var.get()

        if not selected_order or not selected_product:
            messagebox.showerror("Error", "Please select order and product")
            return

        order_id = int(selected_order.split(" - ")[0])
        product_id = int(selected_product.split(" - ")[0])

        data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": int(self.quantity_entry.get()),
            "reason": self.reason_text.get("1.0", END).strip(),
        }

        response = requests.post(
            f"{self.app.api_base}/refunds/", json=data, headers=self.headers()
        )

        if response.status_code == 201:
            messagebox.showinfo("Success", "Refund request submitted successfully!")
            self.show_refunds()
        else:
            messagebox.showerror("Error", response.text)

    def show_all_refunds(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="All Refunds (Admin)", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_refunds).pack(side=RIGHT, padx=5)

        # Treeview for all refunds
        columns = (
            "ID",
            "User ID",
            "Order ID",
            "Product ID",
            "Quantity",
            "Status",
            "Amount",
            "Date",
        )
        self.admin_tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.admin_tree.heading(col, text=col)
            self.admin_tree.column(col, width=100)

        self.admin_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.app.main_frame)
        btn_frame.pack(fill=X, pady=5)

        ttk.Button(btn_frame, text="Approve", command=self.approve_refund).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Reject", command=self.reject_refund).pack(
            side=LEFT, padx=5
        )

        self.load_all_refunds()

    def load_all_refunds(self):
        response = requests.get(
            f"{self.app.api_base}/refunds/admin/all", headers=self.headers()
        )

        if response.status_code == 200:
            refunds = response.json()

            for row in self.admin_tree.get_children():
                self.admin_tree.delete(row)

            for refund in refunds:
                self.admin_tree.insert(
                    "",
                    END,
                    values=(
                        refund["id"],
                        refund["user_id"],
                        refund["order_id"],
                        refund["product_id"],
                        refund["quantity"],
                        refund["status"],
                        f"${refund['refund_amount'] or 0:.2f}",
                        refund["created_at"][:10],
                    ),
                )

    def get_selected_refund_id(self):
        tree = getattr(self, "admin_tree", self.tree)
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a refund")
            return None
        return tree.item(selected[0])["values"][0]

    def view_details(self):
        refund_id = self.get_selected_refund_id()
        if not refund_id:
            return

        response = requests.get(
            f"{self.app.api_base}/refunds/{refund_id}", headers=self.headers()
        )

        if response.status_code == 200:
            refund = response.json()

            details = f"""
Refund Details:
ID: {refund['id']}
Order ID: {refund['order_id']}
Product ID: {refund['product_id']}
Quantity: {refund['quantity']}
Status: {refund['status']}
Reason: {refund['reason']}
Refund Amount: ${refund['refund_amount'] or 0:.2f}
Created: {refund['created_at']}
Refund Date: {refund['refund_date'] or 'Not processed yet'}
            """

            messagebox.showinfo("Refund Details", details)
        else:
            messagebox.showerror("Error", response.text)

    def approve_refund(self):
        refund_id = self.get_selected_refund_id()
        if not refund_id:
            return

        # Ask for refund amount
        amount_window = Toplevel(self.app.root)
        amount_window.title("Refund Amount")
        amount_window.geometry("300x150")

        ttk.Label(amount_window, text="Enter Refund Amount:").pack(pady=10)
        amount_entry = ttk.Entry(amount_window)
        amount_entry.pack(pady=10)
        amount_entry.insert(0, "0.00")

        def process_approval():
            try:
                refund_amount = float(amount_entry.get())

                response = requests.put(
                    f"{self.app.api_base}/refunds/{refund_id}/status",
                    params={"status": "approved", "refund_amount": refund_amount},
                    headers=self.headers(),
                )

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Refund approved successfully!")
                    amount_window.destroy()
                    if self.app.user["role"] == "admin":
                        self.load_all_refunds()
                    else:
                        self.load_refunds()
                else:
                    messagebox.showerror("Error", response.text)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")

        ttk.Button(amount_window, text="Approve", command=process_approval).pack(
            pady=10
        )

    def reject_refund(self):
        refund_id = self.get_selected_refund_id()
        if not refund_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to reject this refund request?"
        ):
            response = requests.put(
                f"{self.app.api_base}/refunds/{refund_id}/status",
                params={"status": "rejected"},
                headers=self.headers(),
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Refund rejected successfully!")
                if self.app.user["role"] == "admin":
                    self.load_all_refunds()
                else:
                    self.load_refunds()
            else:
                messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
