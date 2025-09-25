import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# -------------------- User & Group Classes --------------------
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Buyer:
    def __init__(self, user):
        self.user = user
        self.final_price = 0
        self.savings = 0

class GroupBuy:
    def __init__(self, product, price, discount, min_required, starter):
        self.product = product
        self.price = price
        self.discount = discount
        self.min_required = min_required
        self.buyers = [Buyer(starter)]
        self.active = True

    def add_buyer(self, user):
        self.buyers.append(Buyer(user))
        return len(self.buyers)

    def checkout(self):
        current = len(self.buyers)
        if current < self.min_required:
            self.active = False
            return False, f"❌ Group for {self.product} failed.\nOnly {current}/{self.min_required} joined."
        
        price_per_person = self.price * (1 - self.discount/100)
        savings = self.price - price_per_person
        total_revenue = price_per_person * current

        for b in self.buyers:
            b.final_price = price_per_person
            b.savings = savings

        self.active = False
        summary = f"🎉 Group Success!\n\nProduct: {self.product}\n"
        summary += f"Final Price/Person: RM {price_per_person:.2f}\n"
        summary += f"Savings/Person: RM {savings:.2f}\n"
        summary += f"Total Revenue: RM {total_revenue:.2f}\n\n"
        summary += "Buyers:\n"
        for b in self.buyers:
            summary += f" - {b.user.username} (Paid RM {b.final_price:.2f})\n"
        return True, summary

# -------------------- Global State --------------------
products = [
    {"name": "Xiaomi Earbuds", "price": 150, "discount": 30, "min_required": 3, "img": "earbuds.png"},
    {"name": "iPhone Case", "price": 20, "discount": 25, "min_required": 2, "img": "case.png"},
    {"name": "Smart Watch", "price": 200, "discount": 40, "min_required": 4, "img": "watch.png"}
]
groups = []
users = {}
current_user = None
seller_revenue = 0
product_status_labels = {}   # <--- track status labels for each product

# -------------------- Functions --------------------
def register_user():
    username = reg_username.get()
    password = reg_password.get()
    if username in users:
        messagebox.showerror("Error", "Username already exists.")
        return
    users[username] = User(username, password)
    messagebox.showinfo("Success", "Account created successfully!")

def login_user():
    global current_user
    username = login_username.get()
    password = login_password.get()
    if username not in users or users[username].password != password:
        messagebox.showerror("Error", "Invalid login.")
        return
    current_user = users[username]
    messagebox.showinfo("Welcome", f"Hello {current_user.username}, you are now logged in!")
    root.withdraw()      # hide login window
    open_catalog()       # open shopping catalog

def logout(catalog_window):
    global current_user
    current_user = None
    catalog_window.destroy()   # close catalog
    root.deiconify()           # show login window again

def update_status(product_name):
    frame = product_status_labels[product_name]
    for widget in frame.winfo_children():
        widget.destroy()

    active_groups = [gr for gr in groups if gr.active and gr.product == product_name]
    if not active_groups:
        tk.Label(frame, text="❌ No active group buy", fg="grey", bg="white",
                 font=("Arial", 9, "italic")).pack(anchor="w")
        return

    for gr in active_groups:
        info = f"👥 {gr.buyers[0].user.username}'s group ({len(gr.buyers)}/{gr.min_required})"
        tk.Label(frame, text=info, fg="green", bg="white").pack(anchor="w")

        def join_action(group=gr):
            # block if already in ANY group for this product
            if any(b.user.username == current_user.username for b in group.buyers):
                messagebox.showwarning("Already Joined", "You are already in this group.")
                return
            if any(b.user.username == current_user.username for g2 in groups if g2.active and g2.product == product_name for b in g2.buyers):
                messagebox.showwarning("Already Participating",
                                       f"You are already in another group for {product_name}.")
                return

            count = group.add_buyer(current_user)
            if count >= group.min_required:
                global seller_revenue
                success, msg = group.checkout()
                if success:
                    seller_revenue += group.price * (1 - group.discount/100) * count
                messagebox.showinfo("Checkout", msg)
                update_status(product_name)
            else:
                messagebox.showinfo("Joined",
                                    f"{current_user.username} joined {group.product}!\n👥 {count}/{group.min_required} now.")
                update_status(product_name)

        tk.Button(frame, text="Join This Group", bg="#FF5722", fg="white",
                  font=("Arial", 9, "bold"), command=join_action).pack(anchor="w", pady=2)

def start_group(product):
    if not current_user:
        messagebox.showwarning("Login Required", "Please login first.")
        return

    # Check if this user already in ANY active group for this product
    for g in groups:
        if g.active and g.product == product["name"]:
            if any(b.user.username == current_user.username for b in g.buyers):
                messagebox.showwarning("Already Participating",
                                       f"You are already in a group for {product['name']}.\nYou cannot start another one.")
                return

    g = GroupBuy(product["name"], product["price"], product["discount"],
                 product["min_required"], current_user)
    groups.append(g)
    messagebox.showinfo("Group Buy", f"✅ {current_user.username} started a Group Buy for {product['name']}!")
    update_status(product["name"])

def join_group():
    if not current_user:
        messagebox.showwarning("Login Required", "Please login first.")
        return

    active_groups = [g for g in groups if g.active]
    if not active_groups:
        messagebox.showwarning("No Groups", "No active group buys available.")
        return

    join_win = tk.Toplevel(root)
    join_win.title("Join Group Buy")
    join_win.configure(bg="white")

    for g in active_groups:
        frame = tk.Frame(join_win, bd=2, relief="ridge", padx=10, pady=10, bg="white")
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text=f"{g.product}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(frame, text=f"RM {g.price:.2f} (-{g.discount}%)", fg="red", font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(frame, text=f"👥 {len(g.buyers)}/{g.min_required} joined", bg="white").pack(anchor="w")

        def make_join(group=g):
            def join_action():
                if any(b.user.username == current_user.username for b in group.buyers):
                    messagebox.showwarning("Already Joined", "You have already joined this group.")
                    return
                count = group.add_buyer(current_user)
                if count >= group.min_required:
                    global seller_revenue
                    success, msg = group.checkout()
                    if success:
                        seller_revenue += group.price * (1 - group.discount/100) * count
                    messagebox.showinfo("Checkout", msg)
                    update_status(group.product)
                    join_win.destroy()
                else:
                    messagebox.showinfo("Joined", f"{current_user.username} joined {group.product}!\n👥 {count}/{group.min_required} now.")
                    update_status(group.product)
            return join_action

        tk.Button(frame, text="Join This Group", bg="#FF5722", fg="white", font=("Arial", 10, "bold"),
                  command=make_join()).pack(pady=5)

def view_revenue():
    messagebox.showinfo("Seller Revenue", f"📊 Total Revenue: RM {seller_revenue:.2f}")

def open_catalog():
    catalog = tk.Toplevel(root)
    catalog.title("Shopee Group Buy")
    catalog.geometry("950x950")
    catalog.configure(bg="white")

    # ---- Header row with title (left) and logout (right) ----
    header = tk.Frame(catalog, bg="white")
    header.pack(fill="x", pady=10)

    tk.Label(header, text="🛒 Shopee Mall - Group Buy Deals",
             font=("Arial", 16, "bold"), bg="white", fg="#FF5722").pack(side="left", padx=10)

    # 🚪 Logout button in top-right
    tk.Button(header, text="🚪 Logout", bg="black", fg="white",
              command=lambda: logout(catalog)).pack(side="right", padx=10)

    # ---- Product listing ----
    for p in products:
        frame = tk.Frame(catalog, bd=2, relief="groove", padx=10, pady=10, bg="white")
        frame.pack(padx=10, pady=5, fill="x")

        try:
            img = Image.open(p["img"])
            img = img.resize((80, 80))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=photo, bg="white")
            img_label.image = photo
            img_label.pack(side="left", padx=10)
        except:
            tk.Label(frame, text="[No Image]", width=12, height=6, bg="grey").pack(side="left", padx=10)

        info = tk.Frame(frame, bg="white")
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=p['name'], font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(info, text=f"RM {p['price']:.2f} (-{p['discount']}%)", fg="red",
                 font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(info, text=f"Min group size: {p['min_required']}", bg="white").pack(anchor="w")


        tk.Button(info, text="➕ Start Group Buy", bg="#FF5722", fg="white",
                  font=("Arial", 10, "bold"),
                  command=lambda prod=p: start_group(prod)).pack(anchor="e", pady=5)
        
                # status frame for active groups
        status_frame = tk.Frame(info, bg="white")
        status_frame.pack(anchor="w", pady=2, fill="x")
        product_status_labels[p['name']] = status_frame

        # ✅ show correct status (active groups or none)
        update_status(p['name'])


    # ---- Middle buttons ----
    tk.Button(catalog, text="👥 Join Existing Group Buys", width=40, bg="#FF5722", fg="white",
              command=join_group).pack(pady=10)
    tk.Button(catalog, text="📊 View Seller Revenue", width=40, bg="grey", fg="white",
              command=view_revenue).pack(pady=10)


# -------------------- Login Window --------------------
root = tk.Tk()
root.title("Shopee Login")
root.geometry("400x300")
root.configure(bg="white")

tk.Label(root, text="🔐 Login to Shopee", font=("Arial", 14, "bold"), bg="white", fg="#FF5722").pack(pady=10)

login_username = tk.Entry(root, width=30)
login_password = tk.Entry(root, width=30, show="*")
tk.Label(root, text="Username", bg="white").pack()
login_username.pack()
tk.Label(root, text="Password", bg="white").pack()
login_password.pack()

tk.Button(root, text="Login", bg="#FF5722", fg="white", command=login_user).pack(pady=5)

tk.Label(root, text="Or Register New Account", bg="white").pack(pady=5)

reg_username = tk.Entry(root, width=30)
reg_password = tk.Entry(root, width=30, show="*")
tk.Label(root, text="New Username", bg="white").pack()
reg_username.pack()
tk.Label(root, text="New Password", bg="white").pack()
reg_password.pack()

tk.Button(root, text="Register", bg="grey", fg="white", command=register_user).pack(pady=5)

root.mainloop()
