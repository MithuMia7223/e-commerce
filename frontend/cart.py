from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class CartPage:

    def __init__(self, app):
        self.app = app
        self.show_cart()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_cart(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Shopping Cart", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for cart items
        columns = ("ID", "Product ID", "Name", "Quantity", "Price", "Total")
        self.tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Summary frame
        self.summary_frame = ttk.Frame(self.app.main_frame)
        self.summary_frame.pack(fill=X, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.app.main_frame)
        btn_frame.pack(fill=X, pady=5)

        ttk.Button(
            btn_frame, text="Update Quantity", command=self.update_quantity
        ).pack(side=LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Remove from Cart", command=self.remove_from_cart
        ).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Cart", command=self.clear_cart).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Checkout", command=self.checkout).pack(
            side=RIGHT, padx=5
        )

        self.load_cart()

    def load_cart(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/cart/", headers=self.headers()
            )

            if response.status_code == 200:
                cart_items = response.json()

                for row in self.tree.get_children():
                    self.tree.delete(row)

                total_amount = 0

                for item in cart_items:
                    item_total = item.get("price", 0) * item.get("quantity", 1)
                    total_amount += item_total

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            item["id"],
                            item["product_id"],
                            f"Product {item['product_id']}",
                            item["quantity"],
                            f"${item.get('price', 0):.2f}",
                            f"${item_total:.2f}",
                        ),
                    )

                # Update summary
                for widget in self.summary_frame.winfo_children():
                    widget.destroy()

                ttk.Label(
                    self.summary_frame,
                    text=f"Total: ${total_amount:.2f}",
                    font=("Arial", 16, "bold"),
                ).pack(side=RIGHT, padx=10)

                ttk.Label(
                    self.summary_frame,
                    text=f"Items: {len(cart_items)}",
                    font=("Arial", 14),
                ).pack(side=RIGHT, padx=10)
            else:
                messagebox.showerror("Error", "Failed to load cart")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cart: {str(e)}")

    def get_selected_item_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return None
        return self.tree.item(selected[0])["values"][0]

    def update_quantity(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return

        # Create quantity update dialog
        dialog = Toplevel(self.app.main_frame)
        dialog.title("Update Quantity")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="New Quantity:").pack(pady=10)
        quantity_var = StringVar(value="1")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.pack(pady=10)

        def update():
            try:
                new_quantity = int(quantity_var.get())
                if new_quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return

                response = requests.put(
                    f"{self.app.api_base}/cart/{item_id}",
                    json={"quantity": new_quantity},
                    headers=self.headers(),
                )

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Quantity updated!")
                    dialog.destroy()
                    self.load_cart()
                else:
                    messagebox.showerror("Error", response.text)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")

        ttk.Button(dialog, text="Update", command=update).pack(pady=10)

    def remove_from_cart(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to remove this item from cart?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/cart/{item_id}", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Removed from cart!")
                self.load_cart()
            else:
                messagebox.showerror("Error", response.text)

    def clear_cart(self):
        if messagebox.askyesno(
            "Confirm", "Are you sure you want to clear your entire cart?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/cart/", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Cart cleared!")
                self.load_cart()
            else:
                messagebox.showerror("Error", response.text)

    def checkout(self):
        # Create checkout window
        checkout_window = Toplevel(self.app.main_frame)
        checkout_window.title("চেকআউট - Payment Processing")
        checkout_window.geometry("600x500")

        # Checkout form
        form_frame = ttk.LabelFrame(checkout_window, text="পেমেন্ট তথ্যস")
        form_frame.pack(fill=X, padx=20, pady=20)

        # Shipping address
        ttk.Label(form_frame, text="শিপিং ঠিকানা:").grid(
            row=0, column=0, sticky=W, pady=5
        )
        self.shipping_var = StringVar()
        shipping_combo = ttk.Combobox(
            form_frame, textvariable=self.shipping_var, width=30
        )
        shipping_combo["values"] = ["হোম ডেলিভারি", "অফিস", "অন্য ঠিকানা"]
        shipping_combo.grid(row=0, column=1, pady=5)

        # Payment method
        ttk.Label(form_frame, text="পেমেন্ট পদ্ধতি:").grid(
            row=1, column=0, sticky=W, pady=5
        )
        self.payment_var = StringVar()
        payment_combo = ttk.Combobox(
            form_frame, textvariable=self.payment_var, width=30
        )
        payment_combo["values"] = ["ক্যাশ কার্ড", "বিকাশ", "নগদ", "মোবাইল ব্যাংকিং"]
        payment_combo.grid(row=1, column=1, pady=5)

        # Coupon code
        ttk.Label(form_frame, text="কুপন কোড:").grid(row=2, column=0, sticky=W, pady=5)
        self.coupon_var = StringVar()
        coupon_entry = ttk.Entry(form_frame, textvariable=self.coupon_var, width=30)
        coupon_entry.grid(row=2, column=1, pady=5)

        # Order summary
        summary_frame = ttk.LabelFrame(checkout_window, text="অর্ডার সারাংশ")
        summary_frame.pack(fill=X, padx=20, pady=10)

        try:
            response = requests.get(
                f"{self.app.api_base}/cart/", headers=self.headers()
            )
            if response.status_code == 200:
                cart_items = response.json()
                total = sum(
                    item.get("price", 0) * item.get("quantity", 0)
                    for item in cart_items
                )

                ttk.Label(summary_frame, text=f"মোট পণ্য: {len(cart_items)} টি").pack(
                    anchor=W, pady=2
                )
                ttk.Label(summary_frame, text=f"মোট মূল্য: ৳{total:.2f}").pack(
                    anchor=W, pady=2
                )

                # Apply discount if coupon
                if self.coupon_var.get():
                    ttk.Label(summary_frame, text="কুপন প্রয় গত হয়েছে").pack(
                        anchor=W, pady=2
                    )
                    total *= 0.9  # 10% discount
                    ttk.Label(
                        summary_frame, text=f"ডিসকাউন্ট মূল্য: ৳{total:.2f}"
                    ).pack(anchor=W, pady=2)
        except:
            pass

        # Buttons
        btn_frame = ttk.Frame(checkout_window)
        btn_frame.pack(fill=X, padx=20, pady=20)

        ttk.Button(
            btn_frame,
            text="অর্ডার নিশ্চিত্ত করুন",
            command=lambda: self.process_checkout(checkout_window),
        ).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="বাতিল", command=checkout_window.destroy).pack(
            side=RIGHT, padx=5
        )

    def process_checkout(self, window):
        try:
            # Get cart items
            response = requests.get(
                f"{self.app.api_base}/cart/", headers=self.headers()
            )
            cart_items = response.json()

            # Create order
            order_data = {
                "shipping_address": self.shipping_var.get(),
                "payment_method": self.payment_var.get(),
                "coupon_code": self.coupon_var.get(),
                "items": cart_items,
            }

            response = requests.post(
                f"{self.app.api_base}/orders/", json=order_data, headers=self.headers()
            )

            if response.status_code == 201:
                messagebox.showinfo("সফল্য", "অর্ডার সফল্যভাবে হয়েছে!")
                window.destroy()
                self.show_cart()
            else:
                messagebox.showerror("অসফলত", response.text)
        except Exception as e:
            messagebox.showerror("অসফলত", f"চেকআউট ব্যর্হ: {str(e)}")

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
