from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class VendorPage:

    def __init__(self, app):
        self.app = app
        self.current_product_id = None
        self.show_vendor_dashboard()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_vendor_dashboard(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Vendor Dashboard", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Navigation buttons
        nav_frame = ttk.Frame(self.app.main_frame)
        nav_frame.pack(fill=X, pady=5)

        ttk.Button(
            nav_frame, text="Create Product", command=self.show_create_form
        ).pack(side=LEFT, padx=5)
        ttk.Button(nav_frame, text="My Products", command=self.show_my_products).pack(
            side=LEFT, padx=5
        )
        ttk.Button(nav_frame, text="Product Variants", command=self.show_variants).pack(
            side=LEFT, padx=5
        )

        # Welcome message
        welcome_frame = ttk.Frame(self.app.main_frame)
        welcome_frame.pack(fill=BOTH, expand=True, pady=20)

        ttk.Label(
            welcome_frame, text="Welcome to Vendor Dashboard", font=("Arial", 16)
        ).pack(pady=10)
        ttk.Label(
            welcome_frame,
            text="Manage your products and track sales",
            font=("Arial", 12),
        ).pack(pady=5)

    def show_create_form(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Create Product", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_vendor_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Form frame
        form_frame = ttk.LabelFrame(self.app.main_frame, text="Product Details")
        form_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Name
        ttk.Label(form_frame, text="Product Name:").grid(
            row=0, column=0, sticky=W, pady=5
        )
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)

        # Description
        ttk.Label(form_frame, text="Description:").grid(
            row=1, column=0, sticky=W, pady=5
        )
        self.desc_text = Text(form_frame, width=40, height=5, wrap=WORD)
        self.desc_text.grid(row=1, column=1, pady=5)

        # Price
        ttk.Label(form_frame, text="Price:").grid(row=2, column=0, sticky=W, pady=5)
        self.price_entry = ttk.Entry(form_frame, width=40)
        self.price_entry.grid(row=2, column=1, pady=5)

        # Stock
        ttk.Label(form_frame, text="Stock:").grid(row=3, column=0, sticky=W, pady=5)
        self.stock_entry = ttk.Entry(form_frame, width=40)
        self.stock_entry.insert(0, "0")
        self.stock_entry.grid(row=3, column=1, pady=5)

        # Category
        ttk.Label(form_frame, text="Category ID:").grid(
            row=4, column=0, sticky=W, pady=5
        )
        self.category_entry = ttk.Entry(form_frame, width=40)
        self.category_entry.grid(row=4, column=1, pady=5)

        # Category selection
        ttk.Label(form_frame, text="Select Category:").grid(
            row=5, column=0, sticky=W, pady=5
        )
        self.category_var = StringVar()
        category_combo = ttk.Combobox(
            form_frame, textvariable=self.category_var, state="readonly", width=30
        )
        category_combo.grid(row=5, column=1, pady=5)

        # Load categories
        ttk.Button(
            form_frame, text="Load Categories", command=self.load_categories
        ).grid(row=6, column=1, pady=5)

        # Product image
        ttk.Label(form_frame, text="Product Image:").grid(
            row=5, column=0, sticky=W, pady=5
        )
        self.image_path_var = StringVar()
        self.image_label = ttk.Label(form_frame, text="No image selected")
        self.image_label.grid(row=5, column=1, sticky=W, pady=5)

        # Product price
        ttk.Label(form_frame, text="Product Price (৳):").grid(
            row=6, column=0, sticky=W, pady=5
        )
        self.price_var = StringVar()
        self.price_entry = ttk.Entry(form_frame, textvariable=self.price_var, width=40)
        self.price_entry.grid(row=6, column=1, pady=5)

        image_btn_frame = ttk.Frame(form_frame)
        image_btn_frame.grid(row=7, column=1, pady=5)

        ttk.Button(
            image_btn_frame, text="Choose Image", command=self.choose_image
        ).pack(side=LEFT, padx=5)
        ttk.Button(
            image_btn_frame, text="Upload Image", command=self.upload_image
        ).pack(side=LEFT, padx=5)

        # Buttons frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=1, pady=20)

        ttk.Button(btn_frame, text="Create Product", command=self.create_product).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(
            side=LEFT, padx=5
        )

    def load_categories(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/categories/", headers=self.headers()
            )
            if response.status_code == 200:
                categories = response.json()
                self.category_combo["values"] = [
                    f"ID: {cat['id']} - {cat['name']}" for cat in categories
                ]
            else:
                messagebox.showerror("Error", "Failed to load categories")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")

    def create_product(self):
        name = self.name_entry.get().strip()
        description = self.desc_text.get("1.0", END).strip()
        price = self.price_entry.get().strip()
        stock = self.stock_entry.get().strip()
        category_id = self.category_entry.get().strip()
        image_path = self.image_path_var.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter product name")
            return

        if not price:
            messagebox.showwarning("Warning", "Please enter product price")
            return

        try:
            # Create product data
            product_data = {
                "name": name,
                "description": description,
                "price": float(price),
                "stock": int(stock),
                "category_id": int(category_id) if category_id else None,
                "image_path": image_path if image_path else None,
            }

            response = requests.post(
                f"{self.app.api_base}/products/",
                json=product_data,
                headers=self.headers(),
            )

            if response.status_code == 201:
                messagebox.showinfo("Success", "Product created successfully!")
                self.clear_form()
            else:
                messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create product: {str(e)}")

        if not description:
            messagebox.showwarning("Warning", "Please enter product description")
            return

        if not price:
            messagebox.showwarning("Warning", "Please enter product price")
            return

        try:
            price = float(price)
            stock = int(stock) if stock else 0
            category_id = int(category_id) if category_id else None
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock value")
            return

        try:
            response = requests.post(
                f"{self.app.api_base}/products/",
                json={
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category_id": category_id,
                },
                headers=self.headers(),
            )

            if response.status_code == 201:
                messagebox.showinfo("Success", "Product created successfully!")
                self.show_vendor_dashboard()
            else:
                messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create product: {str(e)}")

    def choose_image(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Choose Product Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")],
        )
        if file_path:
            self.image_path_var.set(file_path)
            self.image_label.config(text=f"Selected: {file_path.split('/')[-1]}")

    def upload_image(self):
        image_path = self.image_path_var.get()
        if not image_path:
            messagebox.showwarning("Warning", "Please choose an image first")
            return

        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.split("/")[-1], f, "image/jpeg")}
                response = requests.post(
                    f"{self.app.api_base}/products/upload-image/{self.current_product_id}",
                    files=files,
                    headers=self.headers(),
                )

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Image uploaded successfully!")
                else:
                    messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload image: {str(e)}")

    def clear_form(self):
        self.name_entry.delete(0, END)
        self.desc_text.delete("1.0", END)
        self.price_entry.delete(0, END)
        self.stock_entry.delete(0, END)
        self.stock_entry.insert(0, "0")
        self.category_entry.delete(0, END)
        self.image_path_var.set("")
        self.image_label.config(text="No image selected")

    def show_my_products(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="My Products", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_vendor_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Add upload button
        upload_frame = ttk.Frame(self.app.main_frame)
        upload_frame.pack(fill=X, pady=5)

        ttk.Button(
            upload_frame, text="Upload Image", command=self.upload_image_page
        ).pack(side=LEFT, padx=5)

        # Treeview for products
        columns = ("ID", "Name", "Price", "Stock", "Status")
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

        ttk.Button(btn_frame, text="Edit Product", command=self.edit_product).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Refresh", command=self.load_my_products).pack(
            side=LEFT, padx=5
        )

        self.load_my_products()

    def load_my_products(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )

            if response.status_code == 200:
                products = response.json()

                # Filter products by current vendor
                my_products = [
                    p for p in products if p.get("vendor_id") == self.app.user.get("id")
                ]

                for row in self.tree.get_children():
                    self.tree.delete(row)

                for product in my_products:
                    self.tree.insert(
                        "",
                        END,
                        values=(
                            product.get("id", "N/A"),
                            product.get("name", "N/A"),
                            f"${product.get('price', 0):.2f}",
                            product.get("stock", 0),
                            (
                                "In Stock"
                                if product.get("stock", 0) > 0
                                else "Out of Stock"
                            ),
                        ),
                    )
            else:
                messagebox.showerror("Error", "Failed to load products")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def get_selected_product_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return None
        return self.tree.item(selected[0])["values"][0]

    def edit_product(self):
        product_id = self.get_selected_product_id()
        if not product_id:
            return

        messagebox.showinfo(
            "Info", f"Edit functionality for product {product_id} coming soon!"
        )

    def delete_product(self):
        product_id = self.get_selected_product_id()
        if not product_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this product?"
        ):
            try:
                response = requests.delete(
                    f"{self.app.api_base}/products/{product_id}", headers=self.headers()
                )

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Product deleted successfully!")
                    self.load_my_products()
                else:
                    messagebox.showerror("Error", response.text)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")

    def show_variants(self):
        from variants import VariantPage

        VariantPage(self.app)

    def upload_image_page(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Upload Product Image", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_my_products).pack(
            side=RIGHT, padx=5
        )

        # Product selection
        select_frame = ttk.Frame(self.app.main_frame)
        select_frame.pack(fill=X, pady=10)

        ttk.Label(select_frame, text="Select Product:").pack(side=LEFT, padx=5)

        self.product_combo = ttk.Combobox(select_frame, width=20)
        self.product_combo.pack(side=LEFT, padx=5)

        ttk.Button(
            select_frame, text="Load Products", command=self.load_products_for_upload
        ).pack(side=LEFT, padx=5)

        # Image upload
        upload_frame = ttk.Frame(self.app.main_frame)
        upload_frame.pack(fill=X, pady=10)

        ttk.Label(upload_frame, text="Choose Image:").pack(side=LEFT, padx=5)

        self.upload_image_path_var = StringVar()
        self.upload_image_label = ttk.Label(upload_frame, text="No image selected")
        self.upload_image_label.pack(side=LEFT, padx=5)

        ttk.Button(
            upload_frame, text="Choose Image", command=self.choose_upload_image
        ).pack(side=LEFT, padx=5)
        ttk.Button(
            upload_frame, text="Upload Image", command=self.upload_product_image
        ).pack(side=LEFT, padx=5)

        self.load_products_for_upload()

    def load_products_for_upload(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/products/", headers=self.headers()
            )
            if response.status_code == 200:
                products = response.json()
                vendor_products = [
                    p for p in products if p.get("vendor_id") == self.app.user.get("id")
                ]
                self.product_combo["values"] = [
                    f"ID: {p['id']} - {p['name']}" for p in vendor_products
                ]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def choose_upload_image(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Choose Product Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")],
        )
        if file_path:
            self.upload_image_path_var.set(file_path)
            self.upload_image_label.config(text=f"Selected: {file_path.split('/')[-1]}")

    def upload_product_image(self):
        selected_product = self.product_combo.get()
        if not selected_product:
            messagebox.showwarning("Warning", "Please select a product first")
            return

        product_id = int(selected_product.split(" - ")[0].split(": ")[1])
        image_path = self.upload_image_path_var.get()

        if not image_path:
            messagebox.showwarning("Warning", "Please choose an image first")
            return

        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.split("/")[-1], f, "image/jpeg")}
                response = requests.post(
                    f"{self.app.api_base}/products/upload-image/{product_id}",
                    files=files,
                    headers=self.headers(),
                )

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Image uploaded successfully!")
                    self.upload_image_path_var.set("")
                    self.upload_image_label.config(text="No image selected")
                else:
                    messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload image: {str(e)}")

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
