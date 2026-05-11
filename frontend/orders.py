from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class OrdersPage:

    def __init__(self, app):
        self.app = app
        self.show_orders()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_orders(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="My Orders", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for orders
        columns = ("ID", "Status", "Payment Status", "Total Amount", "Created Date")
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

        ttk.Button(
            btn_frame, text="View Details", command=self.view_order_details
        ).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_orders).pack(
            side=LEFT, padx=5
        )

        self.load_orders()

    def load_orders(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/orders/", headers=self.headers()
            )

            if response.status_code == 200:
                orders = response.json()

                for row in self.tree.get_children():
                    self.tree.delete(row)

                for order in orders:
                    if not isinstance(order, dict):
                        continue

                    # Calculate total amount from order items
                    total_amount = 0
                    for item in order.get("items", []):
                        total_amount += item.get("price", 0) * item.get("quantity", 1)

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            order.get("id", "N/A"),
                            order.get("status", "N/A"),
                            order.get("payment_status", "N/A"),
                            f"${total_amount:.2f}",
                            order.get("created_at", "N/A")[:10],
                        ),
                    )
            else:
                messagebox.showerror("Error", "Failed to load orders")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def get_selected_order_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order")
            return None
        return self.tree.item(selected[0])["values"][0]

    def view_order_details(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        try:
            response = requests.get(
                f"{self.app.api_base}/orders/{order_id}", headers=self.headers()
            )

            if response.status_code == 200:
                order = response.json()

                # Create details window
                details_window = Toplevel(self.app.main_frame)
                details_window.title(f"অর্ডার বিব্য - {order_id}")
                details_window.geometry("700x600")

                # Order info
                info_frame = ttk.LabelFrame(details_window, text="অর্ডার তথ্যস")
                info_frame.pack(fill=X, padx=10, pady=10)

                ttk.Label(info_frame, text=f"অর্ডার ID: {order.get('id', 'N/A')}").pack(
                    anchor=W, pady=2
                )
                ttk.Label(
                    info_frame, text=f"অবস্থা: {order.get('status', 'N/A')}"
                ).pack(anchor=W, pady=2)
                ttk.Label(
                    info_frame, text=f"মোট মূল্য: ৳{order.get('total', 0):.2f}"
                ).pack(anchor=W, pady=2)
                ttk.Label(
                    info_frame, text=f"Date: {order.get('created_at', 'N/A')}"
                ).pack(anchor=W, pady=2)

                # Customer info
                customer_frame = ttk.LabelFrame(
                    details_window, text="Customer Information"
                )
                customer_frame.pack(fill=X, padx=10, pady=5)

                ttk.Label(
                    customer_frame, text=f"নাম: {order.get('customer_name', 'N/A')}"
                ).pack(anchor=W, pady=2)
                ttk.Label(
                    customer_frame, text=f"Email: {order.get('customer_email', 'N/A')}"
                ).pack(anchor=W, pady=2)
                ttk.Label(
                    customer_frame, text=f"Phone: {order.get('customer_phone', 'N/A')}"
                ).pack(anchor=W, pady=2)

                items_frame = ttk.LabelFrame(details_window, text="Order Items")
                items_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

                item_columns = ("Product", "Quantity", "Price")
                items_tree = ttk.Treeview(
                    items_frame, columns=item_columns, show="headings", height=8
                )

                for col in item_columns:
                    items_tree.heading(col, text=col)
                    items_tree.column(col, width=100)

                items_tree.pack(fill=BOTH, expand=True)

                total_amount = 0
                for item in order.get("items", []):
                    item_total = item.get("price", 0) * item.get("quantity", 1)
                    total_amount += item_total

                    items_tree.insert(
                        "",
                        END,
                        values=(
                            item.get("product_id", "N/A"),
                            f"Product {item.get('product_id', 'N/A')}",
                            item.get("quantity", 1),
                            f"${item.get('price', 0):.2f}",
                            f"${item_total:.2f}",
                        ),
                    )

                # Total label
                ttk.Label(
                    details_window,
                    text=f"Total Amount: ${total_amount:.2f}",
                    font=("Arial", 14, "bold"),
                ).pack(pady=10)

            else:
                messagebox.showerror("Error", "Failed to load order details")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order details: {str(e)}")

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
