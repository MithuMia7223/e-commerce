from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests

from cart import CartPage
from orders import OrdersPage
from wishlist import WishlistPage
from reviews import ReviewPage
from profile import ProfilePage
from vendor import VendorPage
from shipping import ShippingPage
from coupons import CouponPage
from variants import VariantPage
from refunds import RefundPage
from analytics import AnalyticsPage


class DashboardPage:

    def __init__(self, app):

        self.app = app

        self.show_dashboard()

    def clear(self):

        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):

        return {"Authorization": f"Bearer {self.app.token}"}

    def show_dashboard(self):

        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(
            top, text=f"Welcome {self.app.user['username']}", font=("Arial", 20, "bold")
        ).pack(side=LEFT, padx=10)

        # Row 1 navigation buttons
        nav1 = ttk.Frame(top)
        nav1.pack(side=RIGHT, padx=5)

        ttk.Button(nav1, text="Cart", command=self.show_cart).pack(side=RIGHT, padx=2)
        ttk.Button(nav1, text="Orders", command=self.show_orders).pack(
            side=RIGHT, padx=2
        )
        ttk.Button(nav1, text="Wishlist", command=self.show_wishlist).pack(
            side=RIGHT, padx=2
        )
        ttk.Button(nav1, text="Profile", command=self.show_profile).pack(
            side=RIGHT, padx=2
        )
        ttk.Button(nav1, text="Logout", command=self.logout).pack(side=RIGHT, padx=2)

        # Row 2 navigation buttons for new features
        nav2 = ttk.Frame(self.app.main_frame)
        nav2.pack(fill=X, pady=5)

        ttk.Button(nav2, text="Vendor", command=self.create_product).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav2, text="Shipping", command=self.show_shipping).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav2, text="Coupons", command=self.show_coupons).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav2, text="Variants", command=self.show_variants).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav2, text="Refunds", command=self.show_refunds).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav2, text="Analytics", command=self.show_analytics).pack(
            side=LEFT, padx=5
        )

        columns = ("ID", "Name", "Category", "Price", "Stock", "Status")

        self.tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=20
        )

        for col in columns:

            self.tree.heading(col, text=col)

        self.tree.pack(fill=BOTH, expand=True)

        # Search and filter frame
        search_frame = ttk.Frame(self.app.main_frame)
        search_frame.pack(fill=X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
        self.search_var = StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, padx=5)

        ttk.Button(search_frame, text="Search", command=self.search_products).pack(
            side=LEFT, padx=5
        )
        ttk.Button(search_frame, text="Filter", command=self.filter_products).pack(
            side=LEFT, padx=5
        )

        # Additional action buttons
        action_frame = ttk.Frame(self.app.main_frame)
        action_frame.pack(fill=X, pady=5)

        ttk.Button(action_frame, text="Sort by Price", command=self.sort_by_price).pack(
            side=LEFT, padx=5
        )
        ttk.Button(action_frame, text="Sort by Name", command=self.sort_by_name).pack(
            side=LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="View Details", command=self.view_product_details
        ).pack(side=LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", command=self.load_products).pack(
            side=RIGHT, padx=5
        )

        # Buttons frame
        btn = ttk.Frame(self.app.main_frame)
        btn.pack(fill=X)

        ttk.Button(btn, text="Select Product", command=self.select_product).pack(
            side=LEFT, padx=5
        )

        ttk.Button(btn, text="Load Product", command=self.load_product).pack(
            side=LEFT, padx=5
        )

        ttk.Button(btn, text="Add Cart", command=self.add_cart).pack(side=LEFT, padx=5)

        ttk.Button(btn, text="Like", command=self.like_product).pack(side=LEFT, padx=5)

        ttk.Button(btn, text="Review", command=self.review).pack(side=LEFT, padx=5)

        ttk.Button(btn, text="Wishlist", command=self.wishlist).pack(side=LEFT, padx=5)

        if self.app.user["role"] in ["vendor", "admin"]:

            ttk.Button(btn, text="Create Product", command=self.create_product).pack(
                side=RIGHT, padx=5
            )

        self.load_products()

    def load_products(self):

        response = requests.get(
            f"{self.app.api_base}/products/", headers=self.headers()
        )

        products = response.json()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in products:
            # Format price with currency and add stock status
            price = f"৳{p['price']:.2f}"
            stock_status = "In Stock" if p["stock"] > 0 else "Out of Stock"
            category = p.get("category", "General")

            self.tree.insert(
                "",
                END,
                values=(
                    p["id"],
                    p["name"],
                    category,
                    price,
                    f"{p['stock']} ({stock_status})",
                ),
            )

    def get_product(self):

        selected = self.tree.selection()

        if not selected:
            return None

        return self.tree.item(selected[0])["values"][0]

    def add_cart(self):

        pid = self.get_product()

        requests.post(
            f"{self.app.api_base}/cart/",
            json={"product_id": pid, "quantity": 1},
            headers=self.headers(),
        )

        messagebox.showinfo("Success", "Added To Cart")

    def like_product(self):

        pid = self.get_product()

        requests.post(f"{self.app.api_base}/likes/{pid}", headers=self.headers())

        messagebox.showinfo("Success", "Liked")

    def review(self):

        ReviewPage(self.app, self.get_product())

    def wishlist(self):

        WishlistPage(self.app, self.get_product())

    def show_cart(self):

        CartPage(self.app)

    def show_orders(self):

        OrdersPage(self.app)

    def show_wishlist(self):

        WishlistPage(self.app)

    def create_product(self):

        VendorPage(self.app)

    def show_profile(self):

        ProfilePage(self.app)

    def show_shipping(self):
        ShippingPage(self.app)

    def show_coupons(self):
        CouponPage(self.app)

    def show_variants(self):
        VariantPage(self.app)

    def show_refunds(self):
        RefundPage(self.app)

    def show_analytics(self):
        AnalyticsPage(self.app)

    def search_products(self):

        try:
            response = requests.get(
                f"{self.app.api_base}/products/search/{self.search_var.get()}",
                headers=self.headers(),
            )

            products = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for p in products:
                # Format price with currency and add stock status
                price = f"৳{p['price']:.2f}"
                stock_status = "In Stock" if p["stock"] > 0 else "Out of Stock"
                category = p.get("category", "General")

                self.tree.insert(
                    "",
                    END,
                    values=(
                        p["id"],
                        p["name"],
                        category,
                        price,
                        f"{p['stock']} ({stock_status})",
                    ),
                )

        except Exception as e:
            messagebox.showerror("Error", "অনুসন্ধ ব্যর্হ")

    def filter_products(self):

        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )
            if response.status_code == 200:
                products = response.json()

                # Filter in stock products first
                in_stock = [p for p in products if p.get("stock", 0) > 0]
                out_of_stock = [p for p in products if p.get("stock", 0) == 0]

                all_products = in_stock + out_of_stock

                for p in all_products:
                    price = f"৳{p['price']:.2f}"
                    stock_status = "স্টক আছে" if p["stock"] > 0 else "স্টক নেই"
                    category = p.get("category", "সাধারণিক")

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            p["id"],
                            p["name"],
                            category,
                            price,
                            f"{p['stock']} ({stock_status})",
                        ),
                    )
            else:
                messagebox.showerror("Error", "অনুসন্ধ ব্যর্হ")
        except Exception as e:
            messagebox.showerror("Error", f"অনুসন্ধ ব্যর্হ: {str(e)}")

    def sort_by_price(self):
        # Sort products by price (low to high)
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )
            if response.status_code == 200:
                products = response.json()
                # Sort by price
                sorted_products = sorted(products, key=lambda x: x.get("price", 0))

                for p in sorted_products:
                    price = f"৳{p['price']:.2f}"
                    stock_status = "স্টক আছে" if p["stock"] > 0 else "স্টক নেই"
                    category = p.get("category", "সাধারণিক")

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            p["id"],
                            p["name"],
                            category,
                            price,
                            f"{p['stock']} ({stock_status})",
                        ),
                    )
            else:
                messagebox.showerror("Error", "অনুসন্ধ ব্যর্হ")
        except Exception as e:
            messagebox.showerror("Error", f"অনুসন্ধ ব্যর্হ: {str(e)}")

    def sort_by_name(self):
        # Sort products by name (A to Z)
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )
            if response.status_code == 200:
                products = response.json()
                # Sort by name
                sorted_products = sorted(
                    products, key=lambda x: x.get("name", "").lower()
                )

                for p in sorted_products:
                    price = f"৳{p['price']:.2f}"
                    stock_status = "স্টক আছে" if p["stock"] > 0 else "স্টক নেই"
                    category = p.get("category", "সাধারণিক")

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            p["id"],
                            p["name"],
                            category,
                            price,
                            f"{p['stock']} ({stock_status})",
                        ),
                    )
            else:
                messagebox.showerror("Error", "অনুসন্ধ ব্যর্হ")
        except Exception as e:
            messagebox.showerror("Error", f"অনুসন্ধ ব্যর্হ: {str(e)}")

    def select_product(self):
        product_id = self.get_product()
        if not product_id:
            messagebox.showwarning("Warning", "Please select a product")
            return

        try:
            response = requests.get(
                f"{self.app.api_base}/products/{product_id}", headers=self.headers()
            )
            if response.status_code == 200:
                product = response.json()
                messagebox.showinfo(
                    "Product Selected", f"Selected: {product.get('name', 'N/A')}"
                )
            else:
                messagebox.showerror("Error", "Failed to load product")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product: {str(e)}")

    def load_product(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )
            if response.status_code == 200:
                products = response.json()
                if products:
                    product = products[0]  # Load first product
                    messagebox.showinfo(
                        "Product Loaded", f"Loaded: {product.get('name', 'N/A')}"
                    )
                else:
                    messagebox.showinfo("Info", "No products available")
            else:
                messagebox.showerror("Error", "Failed to load products")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def view_product_details(self):
        product_id = self.get_product()
        if not product_id:
            messagebox.showwarning("Warning", "Please select a product")
            return

        try:
            response = requests.get(
                f"{self.app.api_base}/products/{product_id}", headers=self.headers()
            )
            if response.status_code == 200:
                product = response.json()

                # Create details window
                details_window = Toplevel(self.app.main_frame)
                details_window.title(f"Product Details - {product_id}")
                details_window.geometry("700x600")

                # Product info
                info_frame = ttk.LabelFrame(details_window, text="Product Information")
                info_frame.pack(fill=X, padx=10, pady=10)

                ttk.Label(info_frame, text=f"ID: {product.get('id', 'N/A')}").pack(
                    anchor=W, pady=2
                )
                ttk.Label(info_frame, text=f"Name: {product.get('name', 'N/A')}").pack(
                    anchor=W, pady=2
                )
                ttk.Label(
                    info_frame,
                    text=f"Description: {product.get('description', 'N/A')[:100]}...",
                ).pack(anchor=W, pady=2)
                ttk.Label(
                    info_frame, text=f"Price: ৳{product.get('price', 0):.2f}"
                ).pack(anchor=W, pady=2)
                ttk.Label(info_frame, text=f"Stock: {product.get('stock', 0)}").pack(
                    anchor=W, pady=2
                )
                ttk.Label(
                    info_frame, text=f"Category: {product.get('category', 'N/A')}"
                ).pack(anchor=W, pady=2)

                # Order items
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

                ttk.Button(
                    details_window, text="Close", command=details_window.destroy
                ).pack(pady=10)
            else:
                messagebox.showerror("Error", "Failed to load product")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product: {str(e)}")

    def back_to_dashboard(self):

        from auth import AuthPage

        AuthPage(self.app)

    def logout(self):

        self.app.token = None
        self.app.user = None

        self.back_to_dashboard()
