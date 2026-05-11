from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class AnalyticsPage:

    def __init__(self, app):
        self.app = app
        self.show_analytics()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_analytics(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Analytics Dashboard", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )

        if self.app.user["role"] == "admin":
            ttk.Button(
                top, text="Admin Dashboard", command=self.show_admin_dashboard
            ).pack(side=RIGHT, padx=5)

        ttk.Button(top, text="Vendor Summary", command=self.show_vendor_summary).pack(
            side=RIGHT, padx=5
        )
        ttk.Button(
            top, text="Product Analytics", command=self.show_product_analytics
        ).pack(side=RIGHT, padx=5)
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Main content frame
        self.content_frame = ttk.Frame(self.app.main_frame)
        self.content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Show vendor summary by default
        self.show_vendor_summary()

    def show_vendor_business_analytics(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(
            top, text="Vendor Business Analytics", font=("Arial", 20, "bold")
        ).pack(side=LEFT, padx=10)
        ttk.Button(top, text="Back", command=self.show_analytics).pack(
            side=RIGHT, padx=5
        )

        # Date range frame
        days_frame = ttk.Frame(self.app.main_frame)
        days_frame.pack(fill=X, pady=10)

        ttk.Label(days_frame, text="Last").pack(side=LEFT, padx=5)
        self.days_var = StringVar(value="30")
        days_combo = ttk.Combobox(
            days_frame, textvariable=self.days_var, state="readonly", width=10
        )
        days_combo.pack(side=LEFT, padx=5)
        ttk.Button(
            days_frame, text="Refresh", command=self.load_vendor_business_analytics
        ).pack(side=LEFT, padx=5)

        # Business metrics frame
        metrics_frame = ttk.LabelFrame(self.app.main_frame, text="ব্যবসায় মেট্রিক্স")
        metrics_frame.pack(fill=BOTH, expand=True, pady=10)

        # Create metric display
        self.revenue_label = ttk.Label(
            metrics_frame, text="মোট আয়: ৳0.00", font=("Arial", 14, "bold")
        )
        self.revenue_label.pack(anchor=W, pady=5)

        self.orders_label = ttk.Label(
            metrics_frame, text="অর্ডার: 0", font=("Arial", 12)
        )
        self.orders_label.pack(anchor=W, pady=5)

        self.customers_label = ttk.Label(
            metrics_frame, text="গ্রাহক: 0", font=("Arial", 12)
        )
        self.customers_label.pack(anchor=W, pady=5)

        self.avg_order_label = ttk.Label(
            metrics_frame, text="গড় অর্ডার: ৳0.00", font=("Arial", 12)
        )
        self.avg_order_label.pack(anchor=W, pady=5)

        self.load_vendor_business_analytics()

    def load_vendor_business_analytics(self):
        days = int(self.days_var.get())

        response = requests.get(
            f"{self.app.api_base}/analytics/vendor/business",
            params={"days": days},
            headers=self.headers(),
        )

        if response.status_code == 200:
            analytics = response.json()

            self.revenue_label["text"] = f"মোট আয়: ৳{analytics['total_revenue']:.2f}"
            self.orders_label["text"] = f"অর্ডার: {analytics['total_orders']}"
            self.customers_label["text"] = f"গ্রাহক: {analytics['total_customers']}"
            self.avg_order_label["text"] = (
                f"গড় অর্ডার: ৳{analytics['avg_order_value']:.2f}"
            )
        else:
            messagebox.showerror("Error", response.text)

    def show_vendor_summary(self):
        self.clear_content_frame()

        # Days selection
        days_frame = ttk.Frame(self.content_frame)
        days_frame.pack(fill=X, pady=10)

        ttk.Label(days_frame, text="Days:").pack(side=LEFT, padx=5)
        self.days_var = StringVar(value="30")
        days_combo = ttk.Combobox(
            days_frame,
            textvariable=self.days_var,
            values=["7", "30", "90", "365"],
            state="readonly",
            width=10,
        )
        days_combo.pack(side=LEFT, padx=5)
        ttk.Button(days_frame, text="Refresh", command=self.load_vendor_summary).pack(
            side=LEFT, padx=5
        )

        # Summary frame
        self.summary_frame = ttk.LabelFrame(self.content_frame, text="Vendor Summary")
        self.summary_frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        self.load_vendor_summary()

    def load_vendor_summary(self):
        days = int(self.days_var.get())

        response = requests.get(
            f"{self.app.api_base}/analytics/vendor/summary",
            params={"days": days},
            headers=self.headers(),
        )

        if response.status_code == 200:
            summary = response.json()

            # Clear previous content
            for widget in self.summary_frame.winfo_children():
                widget.destroy()

            # Summary cards
            cards_frame = ttk.Frame(self.summary_frame)
            cards_frame.pack(fill=X, pady=10)

            # Total Views
            views_frame = ttk.Frame(cards_frame)
            views_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(views_frame, text="Total Views", font=("Arial", 14)).pack()
            ttk.Label(
                views_frame,
                text=str(summary["total_views"]),
                font=("Arial", 20, "bold"),
            ).pack()

            # Total Purchases
            purchases_frame = ttk.Frame(cards_frame)
            purchases_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(
                purchases_frame, text="Total Purchases", font=("Arial", 14)
            ).pack()
            ttk.Label(
                purchases_frame,
                text=str(summary["total_purchases"]),
                font=("Arial", 20, "bold"),
            ).pack()

            # Total Revenue
            revenue_frame = ttk.Frame(cards_frame)
            revenue_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(revenue_frame, text="Total Revenue", font=("Arial", 14)).pack()
            ttk.Label(
                revenue_frame,
                text=f"${summary['total_revenue']:.2f}",
                font=("Arial", 20, "bold"),
            ).pack()

            # Top Products
            if summary["top_products"]:
                top_frame = ttk.LabelFrame(
                    self.summary_frame, text="Top Products by Revenue"
                )
                top_frame.pack(fill=BOTH, expand=True, pady=10)

                columns = ("Product ID", "Revenue")
                top_tree = ttk.Treeview(
                    top_frame, columns=columns, show="headings", height=8
                )

                for col in columns:
                    top_tree.heading(col, text=col)
                    top_tree.column(col, width=150)

                top_tree.pack(fill=BOTH, expand=True)

                for product_id, revenue in summary["top_products"]:
                    top_tree.insert("", END, values=(product_id, f"${revenue:.2f}"))
        else:
            messagebox.showerror("Error", response.text)

    def show_product_analytics(self):
        self.clear_content_frame()

        # Product selection
        product_frame = ttk.Frame(self.content_frame)
        product_frame.pack(fill=X, pady=10)

        ttk.Label(product_frame, text="Product:").pack(side=LEFT, padx=5)
        self.product_var = StringVar()
        self.product_combo = ttk.Combobox(
            product_frame, textvariable=self.product_var, state="readonly"
        )
        self.product_combo.pack(side=LEFT, padx=5)
        self.product_combo.bind("<<ComboboxSelected>>", self.load_product_analytics)

        ttk.Label(product_frame, text="Days:").pack(side=LEFT, padx=5)
        self.product_days_var = StringVar(value="30")
        days_combo = ttk.Combobox(
            product_frame,
            textvariable=self.product_days_var,
            values=["7", "30", "90", "365"],
            state="readonly",
            width=10,
        )
        days_combo.pack(side=LEFT, padx=5)

        ttk.Button(
            product_frame, text="Load Analytics", command=self.load_product_analytics
        ).pack(side=LEFT, padx=5)

        # Analytics frame
        self.analytics_frame = ttk.LabelFrame(
            self.content_frame, text="Product Analytics"
        )
        self.analytics_frame.pack(fill=BOTH, expand=True, pady=10)

        self.load_products()

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

    def load_product_analytics(self, event=None):
        selected_product = self.product_var.get()
        if not selected_product:
            return

        product_id = int(selected_product.split(" - ")[0])
        days = int(self.product_days_var.get())

        response = requests.get(
            f"{self.app.api_base}/analytics/product/{product_id}",
            params={"days": days},
            headers=self.headers(),
        )

        if response.status_code == 200:
            analytics = response.json()

            # Clear previous content
            for widget in self.analytics_frame.winfo_children():
                widget.destroy()

            # Analytics table
            columns = ("Date", "Views", "Purchases", "Revenue")
            analytics_tree = ttk.Treeview(
                self.analytics_frame, columns=columns, show="headings", height=15
            )

            for col in columns:
                analytics_tree.heading(col, text=col)
                analytics_tree.column(col, width=120)

            analytics_tree.pack(fill=BOTH, expand=True)

            for data in analytics:
                analytics_tree.insert(
                    "",
                    END,
                    values=(
                        data["date"][:10],
                        data["views"],
                        data["purchases"],
                        f"${data['revenue']:.2f}",
                    ),
                )
        else:
            messagebox.showerror("Error", response.text)

    def show_admin_dashboard(self):
        self.clear_content_frame()

        # Days selection
        days_frame = ttk.Frame(self.content_frame)
        days_frame.pack(fill=X, pady=10)

        ttk.Label(days_frame, text="Days:").pack(side=LEFT, padx=5)
        self.admin_days_var = StringVar(value="30")
        days_combo = ttk.Combobox(
            days_frame,
            textvariable=self.admin_days_var,
            values=["7", "30", "90", "365"],
            state="readonly",
            width=10,
        )
        days_combo.pack(side=LEFT, padx=5)
        days = int(self.admin_days_var.get())

        response = requests.get(
            f"{self.app.api_base}/analytics/admin/dashboard",
            params={"days": days},
            headers=self.headers(),
        )

        if response.status_code == 200:
            dashboard = response.json()

            # Clear previous content
            for widget in self.admin_frame.winfo_children():
                widget.destroy()

            # Summary cards
            cards_frame = ttk.Frame(self.admin_frame)
            cards_frame.pack(fill=X, pady=10)

            # Total Views
            views_frame = ttk.Frame(cards_frame)
            views_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(views_frame, text="Total Views", font=("Arial", 14)).pack()
            ttk.Label(
                views_frame,
                text=str(dashboard["total_views"]),
                font=("Arial", 20, "bold"),
            ).pack()

            # Total Purchases
            purchases_frame = ttk.Frame(cards_frame)
            purchases_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(
                purchases_frame, text="Total Purchases", font=("Arial", 14)
            ).pack()
            ttk.Label(
                purchases_frame,
                text=str(dashboard["total_purchases"]),
                font=("Arial", 20, "bold"),
            ).pack()

            # Total Revenue
            revenue_frame = ttk.Frame(cards_frame)
            revenue_frame.pack(side=LEFT, padx=20, expand=True)
            ttk.Label(revenue_frame, text="Total Revenue", font=("Arial", 14)).pack()
            ttk.Label(
                revenue_frame,
                text=f"${dashboard['total_revenue']:.2f}",
                font=("Arial", 20, "bold"),
            ).pack()

            # Top Products by Views
            if dashboard["top_viewed_products"]:
                viewed_frame = ttk.LabelFrame(
                    self.admin_frame, text="Top Products by Views"
                )
                viewed_frame.pack(side=LEFT, fill=BOTH, expand=True, pady=10, padx=5)

                columns = ("Product ID", "Views")
                viewed_tree = ttk.Treeview(
                    viewed_frame, columns=columns, show="headings", height=8
                )

                for col in columns:
                    viewed_tree.heading(col, text=col)
                    viewed_tree.column(col, width=100)

                viewed_tree.pack(fill=BOTH, expand=True)

                for product_id, views in dashboard["top_viewed_products"]:
                    viewed_tree.insert("", END, values=(product_id, views))

            # Top Products by Revenue
            if dashboard["top_revenue_products"]:
                revenue_frame = ttk.LabelFrame(
                    self.admin_frame, text="Top Products by Revenue"
                )
                revenue_frame.pack(side=RIGHT, fill=BOTH, expand=True, pady=10, padx=5)

                columns = ("Product ID", "Revenue")
                revenue_tree = ttk.Treeview(
                    revenue_frame, columns=columns, show="headings", height=8
                )

                for col in columns:
                    revenue_tree.heading(col, text=col)
                    revenue_tree.column(col, width=100)

                revenue_tree.pack(fill=BOTH, expand=True)

                for product_id, revenue in dashboard["top_revenue_products"]:
                    revenue_tree.insert("", END, values=(product_id, f"${revenue:.2f}"))
        else:
            messagebox.showerror("Error", response.text)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
