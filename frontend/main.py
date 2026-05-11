import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style

from auth import AuthPage


class ECommerceApp:

    def __init__(self, root):

        self.root = root
        self.root.title("E-Commerce App")
        self.root.geometry("1200x800")

        self.style = Style(theme="cosmo")

        self.api_base = "http://127.0.0.1:8000"

        self.token = None
        self.user = None
        self.current_role = None
        self.current_role = ["admin", "vendor", "buyer"]
        self.permissions = {
            "admin": {
                "description": "Platform owner",
                "features": ["add_vendor", "remove_vendor"],
            },
            "vendor": {
                "description": "Product seller",
                "features": ["add_product", "remove_product", "update_product_details"],
            },
            "buyer": {
                "description": "Customer",
                "features": ["browse_products", "add_cart", "checkout", "track_order"],
            },
        }

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        AuthPage(self)

    def set_user(self, user_data):
        self.user = user_data
        self.current_role = user_data.get("role", "buyer")

        print("Logged in as:", self.current_role)
        print("Allowed features:", self.permissions[self.current_role]["features"])

        self.load_dashboard()

    # ---------------- DASHBOARD ----------------
    def load_dashboard(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        role = self.current_role

        tk.Label(
            self.main_frame,
            text=f"{role.upper()} DASHBOARD",
            font=("Arial", 20, "bold"),
        ).pack(pady=20)

        features = self.permissions.get(role, {}).get("features", [])

        for feature in features:
            tk.Label(self.main_frame, text=f"• {feature}", font=("Arial", 14)).pack(
                anchor="w", padx=40
            )


if __name__ == "__main__":

    root = tk.Tk()

    app = ECommerceApp(root)

    root.mainloop()
"""
roles:
    - admin
    - vendor
    - buyer

admin:
    - add/remove vendors

vendor:
    - add/remove products
    - set product details

buyer:
    - browse products
    - add/remove products to cart
    - make purchase
"""
