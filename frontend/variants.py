from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class VariantPage:

    def __init__(self, app, product_id=None):
        self.app = app
        self.product_id = product_id
        self.show_variants()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_variants(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Product Variants", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )

        if self.app.user["role"] in ["vendor", "admin"]:
            ttk.Button(top, text="Add Variant", command=self.show_add_variant).pack(
                side=RIGHT, padx=5
            )

        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Product selection (if no product_id provided)
        if not self.product_id:
            product_frame = ttk.Frame(self.app.main_frame)
            product_frame.pack(fill=X, pady=5)

            ttk.Label(product_frame, text="Select Product:").pack(side=LEFT, padx=5)
            self.product_var = StringVar()
            self.product_combo = ttk.Combobox(
                product_frame, textvariable=self.product_var, state="readonly"
            )
            self.product_combo.pack(side=LEFT, padx=5)

            self.load_products()
            ttk.Button(
                product_frame, text="Load Variants", command=self.load_product_variants
            ).pack(side=LEFT, padx=5)

        # Treeview for variants
        columns = ("ID", "Name", "Value", "Price Adj", "Stock", "SKU")
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

        if self.app.user["role"] in ["vendor", "admin"]:
            ttk.Button(btn_frame, text="Edit", command=self.edit_variant).pack(
                side=LEFT, padx=5
            )
            ttk.Button(btn_frame, text="Delete", command=self.delete_variant).pack(
                side=LEFT, padx=5
            )

        if self.product_id:
            self.load_product_variants()

    def load_products(self):
        response = requests.get(
            f"{self.app.api_base}/products/", headers=self.headers()
        )

        if response.status_code == 200:
            products = response.json()
            product_list = [f"{p['id']} - {p['name']}" for p in products]
            self.product_combo["values"] = product_list

            if product_list:
                self.product_combo.current(0)

    def load_product_variants(self):
        product_id = self.product_id

        if not product_id:
            selected = self.product_var.get()
            if selected:
                product_id = int(selected.split(" - ")[0])

        if not product_id:
            return

        response = requests.get(
            f"{self.app.api_base}/variants/product/{product_id}", headers=self.headers()
        )

        if response.status_code == 200:
            variants = response.json()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for variant in variants:
                self.tree.insert(
                    "",
                    END,
                    values=(
                        variant["id"],
                        variant["name"],
                        variant["value"],
                        f"${variant['price_adjustment']:.2f}",
                        variant["stock"],
                        variant["sku"],
                    ),
                )

    def show_add_variant(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Add Product Variant", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_variants).pack(
            side=RIGHT, padx=5
        )

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Product selection
        ttk.Label(form, text="Product:").grid(row=0, column=0, sticky=W, pady=5)
        self.product_var = StringVar()
        self.product_combo = ttk.Combobox(
            form, textvariable=self.product_var, state="readonly"
        )
        self.product_combo.grid(row=0, column=1, pady=5)

        self.load_products()

        # Form fields
        ttk.Label(form, text="Variant Name:").grid(row=1, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(form, width=40)
        self.name_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Variant Value:").grid(row=2, column=0, sticky=W, pady=5)
        self.value_entry = ttk.Entry(form, width=40)
        self.value_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Price Adjustment:").grid(
            row=3, column=0, sticky=W, pady=5
        )
        self.price_adj_entry = ttk.Entry(form, width=40)
        self.price_adj_entry.insert(0, "0")
        self.price_adj_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Stock:").grid(row=4, column=0, sticky=W, pady=5)
        self.stock_entry = ttk.Entry(form, width=40)
        self.stock_entry.insert(0, "0")
        self.stock_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="SKU:").grid(row=5, column=0, sticky=W, pady=5)
        self.sku_entry = ttk.Entry(form, width=40)
        self.sku_entry.grid(row=5, column=1, pady=5)

        ttk.Button(form, text="Save Variant", command=self.save_variant).grid(
            row=6, column=1, pady=20
        )

    def save_variant(self):
        selected_product = self.product_var.get()
        if not selected_product:
            messagebox.showerror("Error", "Please select a product")
            return

        product_id = int(selected_product.split(" - ")[0])

        data = {
            "product_id": product_id,
            "name": self.name_entry.get(),
            "value": self.value_entry.get(),
            "price_adjustment": float(self.price_adj_entry.get()),
            "stock": int(self.stock_entry.get()),
            "sku": self.sku_entry.get(),
        }

        response = requests.post(
            f"{self.app.api_base}/variants/", json=data, headers=self.headers()
        )

        if response.status_code == 201:
            messagebox.showinfo("Success", "Product variant added successfully!")
            self.product_id = product_id
            self.show_variants()
        else:
            messagebox.showerror("Error", response.text)

    def get_selected_variant_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a variant")
            return None
        return self.tree.item(selected[0])["values"][0]

    def edit_variant(self):
        variant_id = self.get_selected_variant_id()
        if not variant_id:
            return

        # Get variant details and populate form for editing
        response = requests.get(
            f"{self.app.api_base}/variants/product/{self.product_id}",
            headers=self.headers(),
        )
        if response.status_code == 200:
            variants = response.json()
            variant = next((v for v in variants if v["id"] == variant_id), None)

            if variant:
                self.show_edit_form(variant)

    def show_edit_form(self, variant):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Edit Product Variant", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.show_variants).pack(
            side=RIGHT, padx=5
        )

        form = ttk.Frame(self.app.main_frame)
        form.pack(fill=BOTH, expand=True)

        # Form fields with existing data
        ttk.Label(form, text="Product ID:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Label(form, text=str(variant["product_id"])).grid(
            row=0, column=1, sticky=W, pady=5
        )

        ttk.Label(form, text="Variant Name:").grid(row=1, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(form, width=40)
        self.name_entry.insert(0, variant["name"])
        self.name_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Variant Value:").grid(row=2, column=0, sticky=W, pady=5)
        self.value_entry = ttk.Entry(form, width=40)
        self.value_entry.insert(0, variant["value"])
        self.value_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Price Adjustment:").grid(
            row=3, column=0, sticky=W, pady=5
        )
        self.price_adj_entry = ttk.Entry(form, width=40)
        self.price_adj_entry.insert(0, str(variant["price_adjustment"]))
        self.price_adj_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Stock:").grid(row=4, column=0, sticky=W, pady=5)
        self.stock_entry = ttk.Entry(form, width=40)
        self.stock_entry.insert(0, str(variant["stock"]))
        self.stock_entry.grid(row=4, column=1, pady=5)

        ttk.Label(form, text="SKU:").grid(row=5, column=0, sticky=W, pady=5)
        self.sku_entry = ttk.Entry(form, width=40)
        self.sku_entry.insert(0, variant["sku"])
        self.sku_entry.grid(row=5, column=1, pady=5)

        ttk.Button(
            form,
            text="Update Variant",
            command=lambda: self.update_variant(variant["id"]),
        ).grid(row=6, column=1, pady=20)

    def update_variant(self, variant_id):
        data = {
            "product_id": self.product_id,
            "name": self.name_entry.get(),
            "value": self.value_entry.get(),
            "price_adjustment": float(self.price_adj_entry.get()),
            "stock": int(self.stock_entry.get()),
            "sku": self.sku_entry.get(),
        }

        response = requests.put(
            f"{self.app.api_base}/variants/{variant_id}",
            json=data,
            headers=self.headers(),
        )

        if response.status_code == 200:
            messagebox.showinfo("Success", "Product variant updated successfully!")
            self.show_variants()
        else:
            messagebox.showerror("Error", response.text)

    def delete_variant(self):
        variant_id = self.get_selected_variant_id()
        if not variant_id:
            return

        if messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this variant?"
        ):
            response = requests.delete(
                f"{self.app.api_base}/variants/{variant_id}", headers=self.headers()
            )

            if response.status_code == 200:
                messagebox.showinfo("Success", "Product variant deleted successfully!")
                self.load_product_variants()
            else:
                messagebox.showerror("Error", response.text)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
