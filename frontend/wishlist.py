from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class WishlistPage:

    def __init__(self, app, product_id=None):
        self.app = app

        if product_id:
            self.add(product_id)
        else:
            self.show_wishlist()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_wishlist(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="My Wishlist", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Treeview for wishlist items
        columns = ("ID", "Product ID", "Name", "Price", "Added Date")
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
            btn_frame, text="Remove from Wishlist", command=self.remove_from_wishlist
        ).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_wishlist).pack(
            side=LEFT, padx=5
        )

        self.load_wishlist()

    def load_wishlist(self):
        response = requests.get(
            f"{self.app.api_base}/wishlist/", headers=self.headers()
        )

        if response.status_code == 200:
            wishlist_items = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for item in wishlist_items:
                self.tree.insert(
                    "",
                    END,
                    values=(
                        item["id"],
                        item["product_id"],
                        f"Product {item['product_id']}",
                        f"${item.get('price', 0):.2f}",
                        item.get("created_at", "N/A")[:10],
                    ),
                )

    def add(self, product_id):
        try:
            response = requests.post(
                f"{self.app.api_base}/wishlist/{product_id}",
                headers=self.headers(),
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Added to Wishlist!")
            else:
                messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to wishlist: {str(e)}")

    def get_selected_item_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return None
        return self.tree.item(selected[0])["values"][0]

    def remove_from_wishlist(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to remove this item from wishlist?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/wishlist/{item_id}", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Removed from wishlist!")
                self.load_wishlist()
            else:
                messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
