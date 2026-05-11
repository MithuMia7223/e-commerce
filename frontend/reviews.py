from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import requests


class ReviewPage:

    def __init__(self, app, product_id):
        self.app = app
        self.product_id = product_id
        self.review_text = None
        self.show_review_form()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_review_form(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(top, text="Write Review", font=("Arial", 20, "bold")).pack(
            side=LEFT, padx=10
        )
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Product info
        info_frame = ttk.Frame(self.app.main_frame)
        info_frame.pack(fill=X, pady=5)

        ttk.Label(
            info_frame, text=f"Product ID: {self.product_id}", font=("Arial", 12)
        ).pack(side=LEFT, padx=10)

        # Form frame
        form_frame = ttk.LabelFrame(self.app.main_frame, text="Review Details")
        form_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Rating
        ttk.Label(form_frame, text="Rating (1-5):").grid(
            row=0, column=0, sticky=W, pady=5
        )
        self.rating_var = IntVar(value=5)
        rating_frame = ttk.Frame(form_frame)
        rating_frame.grid(row=0, column=1, sticky=W, pady=5)

        # Review text
        ttk.Label(form_frame, text="Review Text:").grid(
            row=1, column=0, sticky=W, pady=5
        )
        self.review_text = ttk.Text(form_frame, width=40, height=4)
        self.review_text.grid(row=1, column=1, pady=5)

        for i in range(1, 6):
            ttk.Radiobutton(
                rating_frame, text=str(i), variable=self.rating_var, value=i
            ).pack(side=LEFT, padx=2)

        # Review details section
        ttk.Label(form_frame, text="Review Details:").grid(
            row=3, column=0, sticky=W, pady=5
        )
        review_details_frame = ttk.Frame(form_frame)
        review_details_frame.grid(row=3, column=1, pady=5)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=1, pady=20)

        ttk.Button(btn_frame, text="Submit Review", command=self.submit_review).pack(
            side=LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(
            side=LEFT, padx=5
        )

        # Comment state
        ttk.Label(form_frame, text="Comment Status:").grid(
            row=4, column=0, sticky=W, pady=5
        )
        self.comment_state_var = StringVar(value="enabled")
        comment_state_combo = ttk.Combobox(
            form_frame, textvariable=self.comment_state_var, state="readonly", width=15
        )
        comment_state_combo.grid(row=4, column=1, pady=5)
        comment_state_combo["values"] = ["enabled", "disabled"]

        ttk.Button(
            form_frame, text="Update Comment State", command=self.update_comment_state
        ).grid(row=5, column=1, pady=5)

    def submit_review(self):
        rating = self.rating_var.get()
        text = self.review_text.get("1.0", END).strip()
        comment = self.comment_text.get("1.0", END).strip()

        if not text:
            messagebox.showwarning("Warning", "Please enter review text")
            return

        try:
            response = requests.post(
                f"{self.app.api_base}/reviews/",
                json={
                    "product_id": self.product_id,
                    "rating": rating,
                    "text": text,
                    "comment": comment,
                },
                headers=self.headers(),
            )

            if response.status_code == 201:
                messagebox.showinfo("Success", "Review submitted successfully!")
                self.clear_form()
                # Invalidate token to refresh data
                self.app.token = None
                messagebox.showinfo("Info", "Please login again to see your review")
            else:
                messagebox.showerror("Error", response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit review: {str(e)}")

    def update_comment_state(self):
        current_state = self.comment_state_var.get()
        new_state = "disabled" if current_state == "enabled" else "enabled"
        self.comment_state_var.set(new_state)

        # Update review text widget state
        if new_state == "disabled":
            self.review_text.config(state="disabled")
            messagebox.showinfo("Info", "Comments disabled")
        else:
            self.review_text.config(state="normal")
            messagebox.showinfo("Info", "Comments enabled")

    def clear_form(self):
        self.rating_var.set(5)
        self.review_text.delete("1.0", END)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)


class ProductReviewsPage:

    def __init__(self, app, product_id):
        self.app = app
        self.product_id = product_id
        self.show_reviews()

    def clear(self):
        for widget in self.app.main_frame.winfo_children():
            widget.destroy()

    def headers(self):
        return {"Authorization": f"Bearer {self.app.token}"}

    def show_reviews(self):
        self.clear()

        top = ttk.Frame(self.app.main_frame)
        top.pack(fill=X, pady=10)

        ttk.Label(
            top,
            text=f"Product Reviews - #{self.product_id}",
            font=("Arial", 20, "bold"),
        ).pack(side=LEFT, padx=10)
        ttk.Button(top, text="Back", command=self.back_to_dashboard).pack(
            side=RIGHT, padx=5
        )

        # Review button
        review_btn_frame = ttk.Frame(self.app.main_frame)
        review_btn_frame.pack(fill=X, pady=5)

        ttk.Button(
            review_btn_frame, text="Write Review", command=self.write_review
        ).pack(side=LEFT, padx=10)

        # Treeview for reviews
        columns = ("ID", "User", "Rating", "Comment", "Date")
        self.tree = ttk.Treeview(
            self.app.main_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.load_reviews()

    def load_reviews(self):
        try:
            response = requests.get(
                f"{self.app.api_base}/reviews/product/{self.product_id}",
                headers=self.headers(),
            )

            if response.status_code == 200:
                reviews = response.json()

                for row in self.tree.get_children():
                    self.tree.delete(row)

                for review in reviews:
                    # Truncate long comments
                    comment = review.get("comment", "")
                    if len(comment) > 50:
                        comment = comment[:50] + "..."

                    self.tree.insert(
                        "",
                        END,
                        values=(
                            review.get("id", "N/A"),
                            f"User {review.get('user_id', 'N/A')}",
                            f"{'⭐' * review.get('rating', 0)}",
                            comment,
                            review.get("created_at", "N/A")[:10],
                        ),
                    )
            else:
                messagebox.showerror("Error", "Failed to load reviews")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reviews: {str(e)}")

    def write_review(self):
        ReviewPage(self.app, self.product_id)

    def back_to_dashboard(self):
        from dashboard import DashboardPage

        DashboardPage(self.app)
