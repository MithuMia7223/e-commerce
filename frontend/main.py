import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from ttkbootstrap import Style


class ECommerceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Commerce App")
        self.root.geometry("800x600")

        # Apply ttkbootstrap theme
        self.style = Style(theme="cosmo")

        # API base URL
        self.api_base = "http://localhost:8002"

        # User session
        self.token = None
        self.user = None

        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize frames
        self.login_frame = None
        self.signup_frame = None
        self.products_frame = None
        self.cart_frame = None
        self.profile_frame = None

        # Show login screen initially
        self.show_login()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(pady=50)

        ttk.Label(self.login_frame, text="Login", font=("Arial", 24)).pack(pady=20)

        # Username
        ttk.Label(self.login_frame, text="Username:").pack()
        self.login_username = ttk.Entry(self.login_frame, width=30)
        self.login_username.pack(pady=5)

        # Password
        ttk.Label(self.login_frame, text="Password:").pack()
        self.login_password = ttk.Entry(self.login_frame, show="*", width=30)
        self.login_password.pack(pady=5)

        # Buttons
        ttk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)
        ttk.Button(
            self.login_frame, text="Go to Signup", command=self.show_signup
        ).pack()

    def show_signup(self):
        self.clear_frame()
        self.signup_frame = ttk.Frame(self.main_frame)
        self.signup_frame.pack(pady=50)

        ttk.Label(self.signup_frame, text="Sign Up", font=("Arial", 24)).pack(pady=20)

        # Username
        ttk.Label(self.signup_frame, text="Username:").pack()
        self.signup_username = ttk.Entry(self.signup_frame, width=30)
        self.signup_username.pack(pady=5)

        # Email
        ttk.Label(self.signup_frame, text="Email:").pack()
        self.signup_email = ttk.Entry(self.signup_frame, width=30)
        self.signup_email.pack(pady=5)

        # Password
        ttk.Label(self.signup_frame, text="Password:").pack()
        self.signup_password = ttk.Entry(self.signup_frame, show="*", width=30)
        self.signup_password.pack(pady=5)

        # Buttons
        ttk.Button(self.signup_frame, text="Sign Up", command=self.signup).pack(pady=10)
        ttk.Button(
            self.signup_frame, text="Go to Login", command=self.show_login
        ).pack()

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            response = requests.post(
                f"{self.api_base}/users/login",
                json={"username_or_email": username, "password": password},
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user = data["user"]
                messagebox.showinfo("Success", "Login successful!")
                self.show_products()
            else:
                messagebox.showerror("Error", "Login failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def signup(self):
        username = self.signup_username.get()
        password = self.signup_password.get()
        email = self.signup_email.get()

        if not username or not password or not email:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            response = requests.post(
                f"{self.api_base}/users/register",
                json={"username": username, "email": email, "password": password},
            )
            if response.status_code == 201:
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.show_login()
            elif response.status_code == 400:
                messagebox.showerror(
                    "Error", response.json().get("detail", "Registration failed")
                )
            else:
                messagebox.showerror("Error", "Registration failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def show_products(self):
        self.clear_frame()
        self.products_frame = ttk.Frame(self.main_frame)
        self.products_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = ttk.Frame(self.products_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            header_frame, text=f"Welcome, {self.user['username']}!", font=("Arial", 16)
        ).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Cart", command=self.show_cart).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(header_frame, text="Profile", command=self.show_profile).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT)

        # Search Bar
        search_frame = ttk.Frame(self.products_frame)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(search_frame, text="Search", command=self.load_products).pack(
            side=tk.RIGHT
        )

        # Products list
        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=("Name", "Price", "Stock", "Category"),
            show="headings",
        )
        self.products_tree.heading("Name", text="Name")
        self.products_tree.heading("Price", text="Price")
        self.products_tree.heading("Stock", text="Stock")
        self.products_tree.heading("Category", text="Category")

        scrollbar = ttk.Scrollbar(
            self.products_frame, orient=tk.VERTICAL, command=self.products_tree.yview
        )
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        btn_frame = ttk.Frame(self.products_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Add to Cart", command=self.add_to_cart).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Like", command=self.like_product).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Comment", command=self.comment_product).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Refresh", command=self.load_products).pack(
            side=tk.RIGHT
        )

        self.load_products()

    def load_products(self):
        search_term = self.search_entry.get() if hasattr(self, "search_entry") else ""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_base}/products/?search={search_term}", headers=headers
            )
            if response.status_code == 200:
                products = response.json()["products"]
                self.products_tree.delete(*self.products_tree.get_children())
                for product in products:
                    self.products_tree.insert(
                        "",
                        tk.END,
                        iid=str(product["id"]),
                        values=(
                            product["name"],
                            f"${product['price']}",
                            product["stock"],
                            product.get("category", ""),
                        ),
                    )
            else:
                messagebox.showerror("Error", "Failed to load products")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def add_to_cart(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return

        item = self.products_tree.item(selected[0])
        product_name = item["values"][0]

        product_id = int(selected[0])

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base}/cart/",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )
            if response.status_code in (200, 201):
                messagebox.showinfo("Success", f"{product_name} added to cart!")
            elif response.status_code == 400:
                messagebox.showerror(
                    "Error", response.json().get("detail", "Failed to add to cart")
                )
            else:
                messagebox.showerror("Error", "Failed to add to cart")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def like_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return

        product_id = int(selected[0])

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_base}/likes/{product_id}", headers=headers
            )
            if response.status_code == 200:
                messagebox.showinfo("Success", "Product liked!")
            else:
                messagebox.showerror("Error", "Failed to like product")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def comment_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return

        product_id = int(selected[0])

        comment = simpledialog.askstring("Comment", "Enter your comment:")
        if comment:
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.post(
                    f"{self.api_base}/comments/",
                    json={"product_id": product_id, "comment": comment},
                    headers=headers,
                )
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Comment added!")
                else:
                    messagebox.showerror("Error", "Failed to add comment")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")

    def show_cart(self):
        self.clear_frame()
        self.cart_frame = ttk.Frame(self.main_frame)
        self.cart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self.cart_frame, text="Shopping Cart", font=("Arial", 20)).pack(
            pady=20
        )

        # Cart items display
        self.cart_text = tk.Text(self.cart_frame, height=15, width=80)
        self.cart_text.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.cart_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Checkout", command=self.checkout).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Back to Products", command=self.show_products).pack(
            side=tk.RIGHT
        )

        self.load_cart()

    def load_cart(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.api_base}/cart/", headers=headers)
            if response.status_code == 200:
                cart_data = response.json()
                self.cart_text.delete(1.0, tk.END)
                self.cart_text.insert(tk.END, "Your Cart:\n\n")
                for item in cart_data["cart_items"]:
                    self.cart_text.insert(
                        tk.END,
                        f"{item['product_name']} - Qty: {item['quantity']} - ${item['subtotal']}\n",
                    )
                self.cart_text.insert(tk.END, f"\nTotal: ${cart_data['total_price']}")
            else:
                self.cart_text.delete(1.0, tk.END)
                self.cart_text.insert(tk.END, "Your cart is empty or failed to load.")
        except Exception as e:
            self.cart_text.delete(1.0, tk.END)
            self.cart_text.insert(tk.END, f"Connection error: {str(e)}")

    def checkout(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{self.api_base}/cart/checkout", headers=headers)
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo(
                    "Success", f"Checkout successful! Order ID: {data['order_id']}"
                )
                self.show_products()
            else:
                messagebox.showerror("Error", "Checkout failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def show_profile(self):
        self.clear_frame()
        self.profile_frame = ttk.Frame(self.main_frame)
        self.profile_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self.profile_frame, text="User Profile", font=("Arial", 20)).pack(
            pady=20
        )

        # Profile info
        profile_text = f"Username: {self.user['username']}\nEmail: {self.user['email']}\nRole: {self.user['role']}"
        ttk.Label(self.profile_frame, text=profile_text, justify=tk.LEFT).pack(pady=10)

        # Buttons
        ttk.Button(
            self.profile_frame, text="Back to Products", command=self.show_products
        ).pack(pady=20)

    def logout(self):
        self.token = None
        self.user = None
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = ECommerceApp(root)
    root.mainloop()
