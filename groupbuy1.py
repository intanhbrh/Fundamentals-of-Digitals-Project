import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime

# ==================== USER & GROUP CLASSES ====================
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.join_history = []
        self.created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

class Buyer:
    def __init__(self, user):
        self.user = user
        self.final_price = 0
        self.savings = 0
        self.join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

class GroupBuy:
    def __init__(self, product_name, original_price, discount_percent, min_required, starter_user):
        self.product = product_name
        self.price = original_price
        self.discount = discount_percent
        self.min_required = min_required
        self.buyers = [Buyer(starter_user)]
        self.active = True
        self.created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.completed_time = None

    def add_buyer(self, user):
        new_buyer = Buyer(user)
        self.buyers.append(new_buyer)
        user.join_history.append(f"Joined group for {self.product}")
        return len(self.buyers)

    def checkout(self):
        current_members = len(self.buyers)
        
        if current_members < self.min_required:
            self.active = False
            fail_message = f"❌ GROUP BUY FAILED ❌\n\n"
            fail_message += f"Product: {self.product}\n"
            fail_message += f"Only {current_members} out of {self.min_required} required members joined.\n\n"
            fail_message += "The group buy has been cancelled.\nBetter luck next time!"
            return False, fail_message
        
        # Calculate pricing
        discount_amount = self.price * (self.discount / 100)
        price_per_person = self.price - discount_amount
        total_revenue = price_per_person * current_members
        total_savings_group = discount_amount * current_members

        # Update all buyer information
        for buyer in self.buyers:
            buyer.final_price = price_per_person
            buyer.savings = discount_amount

        self.active = False
        self.completed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Create comprehensive success message
        success_message = f"🎉 GROUP BUY SUCCESS! 🎉\n\n"
        success_message += f"📱 Product: {self.product}\n"
        success_message += f"💰 Original Price: RM {self.price:.2f} per item\n"
        success_message += f"🎯 Discount Applied: {self.discount}%\n"
        success_message += f"💵 Final Price per Person: RM {price_per_person:.2f}\n"
        success_message += f"💸 Individual Savings: RM {discount_amount:.2f}\n"
        success_message += f"📊 Total Revenue for Seller: RM {total_revenue:.2f}\n"
        success_message += f"👥 Total Participants: {current_members}\n"
        success_message += f"🏆 Total Group Savings: RM {total_savings_group:.2f}\n\n"
        
        success_message += "🛒 Group Members:\n"
        for i, buyer in enumerate(self.buyers, 1):
            success_message += f"  {i}. {buyer.user.username} - Paid RM {buyer.final_price:.2f} (Saved RM {buyer.savings:.2f})\n"
        
        success_message += f"\nCompleted at: {self.completed_time}"
        
        return True, success_message

# ==================== GLOBAL APPLICATION STATE ====================
# Product catalog
products_catalog = [
    {
        "name": "Xiaomi Redmi Earbuds Pro", 
        "price": 159.90, 
        "discount": 30, 
        "min_required": 3, 
        "description": "Wireless Bluetooth earbuds with active noise cancellation and 28-hour battery life",
        "category": "Electronics"
    },
    {
        "name": "Premium iPhone 15 Case", 
        "price": 49.90, 
        "discount": 25, 
        "min_required": 2, 
        "description": "Military-grade drop protection with MagSafe compatibility and crystal clear design",
        "category": "Accessories"
    },
    {
        "name": "Smart Fitness Watch Pro", 
        "price": 299.90, 
        "discount": 40, 
        "min_required": 4, 
        "description": "Advanced health monitoring with GPS, heart rate sensor, and 7-day battery life",
        "category": "Wearables"
    },
    {
        "name": "Portable Power Bank 20000mAh", 
        "price": 89.90, 
        "discount": 20, 
        "min_required": 3, 
        "description": "Fast charging power bank with dual USB-C ports and digital display",
        "category": "Electronics"
    },
    {
        "name": "Wireless Gaming Mouse", 
        "price": 129.90, 
        "discount": 35, 
        "min_required": 5, 
        "description": "Professional gaming mouse with RGB lighting and 25000 DPI sensor",
        "category": "Gaming"
    },
    {
        "name": "Bluetooth Speaker Mini", 
        "price": 79.90, 
        "discount": 22, 
        "min_required": 2, 
        "description": "Portable waterproof speaker with 360-degree sound and 12-hour playtime",
        "category": "Audio"
    }
]

# Application state variables
active_groups = []
registered_users = {}
current_logged_user = None
total_seller_revenue = 0
product_status_widgets = {}

# For tracking application statistics
app_stats = {
    "total_groups_created": 0,
    "successful_groups": 0,
    "failed_groups": 0,
    "total_users_registered": 0,
    "total_items_sold": 0
}

# ==================== UTILITY FUNCTIONS ====================
def clear_entry_fields(*entry_widgets):
    """Clear multiple entry fields at once"""
    for entry in entry_widgets:
        if entry and hasattr(entry, 'delete'):
            entry.delete(0, tk.END)

def create_styled_button(parent, text, bg_color, fg_color="white", command=None, width=25, height=2):
    """Create a consistent styled button"""
    return tk.Button(
        parent, 
        text=text, 
        bg=bg_color, 
        fg=fg_color,
        font=("Arial", 11, "bold"), 
        width=width, 
        height=height,
        relief="raised",
        bd=2,
        command=command,
        cursor="hand2"
    )

def validate_user_input(username, password, is_registration=False):
    """Validate user input for login/registration"""
    if not username or not username.strip():
        return False, "Username cannot be empty!"
    
    if not password or not password.strip():
        return False, "Password cannot be empty!"
    
    if is_registration:
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long!"
        
        if len(password.strip()) < 4:
            return False, "Password must be at least 4 characters long!"
        
        if username.strip() in registered_users:
            return False, "Username already exists! Please choose a different one."
    
    return True, "Valid input"

def update_app_statistics():
    """Update global application statistics"""
    app_stats["total_groups_created"] = len(active_groups)
    app_stats["successful_groups"] = len([g for g in active_groups if not g.active and g.completed_time])
    app_stats["failed_groups"] = len([g for g in active_groups if not g.active and not g.completed_time])
    app_stats["total_users_registered"] = len(registered_users)
    app_stats["total_items_sold"] = sum(len(g.buyers) for g in active_groups if not g.active and g.completed_time)

# ==================== AUTHENTICATION FUNCTIONS ====================
def register_new_user():
    """Register a new user account"""
    print("🔧 REGISTER FUNCTION CALLED")
    
    username = username_reg_entry.get().strip()
    password = password_reg_entry.get().strip()
    
    print(f"📝 Registration attempt - Username: '{username}', Password length: {len(password)}")
    
    # Validate input
    is_valid, error_message = validate_user_input(username, password, is_registration=True)
    if not is_valid:
        messagebox.showerror("Registration Error", error_message)
        return
    
    # Create new user
    new_user = User(username, password)
    registered_users[username] = new_user
    app_stats["total_users_registered"] += 1
    
    success_message = f"✅ ACCOUNT CREATED SUCCESSFULLY! ✅\n\n"
    success_message += f"Welcome {username}!\n\n"
    success_message += f"Your account has been created successfully.\n"
    success_message += f"You can now login with your credentials to start group buying!\n\n"
    success_message += f"📊 You are user #{app_stats['total_users_registered']} to join Shopee Group Buy!"
    
    messagebox.showinfo("Registration Success", success_message)
    
    # Clear registration fields
    clear_entry_fields(username_reg_entry, password_reg_entry)
    
    print(f"✅ User '{username}' registered successfully. Total users: {len(registered_users)}")

def login_existing_user():
    """Login with existing user credentials"""
    print("🔧 LOGIN FUNCTION CALLED")
    
    global current_logged_user
    username = username_login_entry.get().strip()
    password = password_login_entry.get().strip()
    
    print(f"🔑 Login attempt - Username: '{username}'")
    print(f"👥 Available users: {list(registered_users.keys())}")
    
    # Validate input
    is_valid, error_message = validate_user_input(username, password, is_registration=False)
    if not is_valid:
        messagebox.showerror("Login Error", error_message)
        return
    
    # Check if user exists
    if username not in registered_users:
        messagebox.showerror("Login Error", 
                           f"Username '{username}' not found!\n\nPlease register first or check your spelling.")
        return
    
    # Check password
    if registered_users[username].password != password:
        messagebox.showerror("Login Error", 
                           "Incorrect password!\n\nPlease try again or reset your password.")
        return
    
    # Successful login
    current_logged_user = registered_users[username]
    
    welcome_message = f"🎉 WELCOME BACK! 🎉\n\n"
    welcome_message += f"Hello {current_logged_user.username}!\n\n"
    welcome_message += f"Login successful! Redirecting you to Shopee Group Buy Mall...\n\n"
    welcome_message += f"Start saving money by joining group buys!"
    
    messagebox.showinfo("Login Success", welcome_message)
    
    # Clear login fields and open main application
    clear_entry_fields(username_login_entry, password_login_entry)
    main_login_window.withdraw()
    open_main_shopping_catalog()
    
    print(f"✅ User '{username}' logged in successfully")

def logout_current_user(catalog_window):
    """Logout current user and return to login screen"""
    global current_logged_user
    
    if current_logged_user:
        logout_confirmation = messagebox.askyesno(
            "Logout Confirmation", 
            f"Are you sure you want to logout, {current_logged_user.username}?\n\n"
            f"You will be redirected back to the login screen."
        )
        
        if logout_confirmation:
            username = current_logged_user.username
            current_logged_user = None
            catalog_window.destroy()
            main_login_window.deiconify()
            print(f"👋 User '{username}' logged out successfully")

# ==================== GROUP BUY MANAGEMENT ====================
def start_new_group_buy(product_info):
    """Start a new group buy for a specific product"""
    if not current_logged_user:
        messagebox.showwarning("Authentication Required", "Please login first to start a group buy!")
        return

    print(f"🚀 Starting group buy for {product_info['name']}")
    
    # Check if user is already in a group for this product
    for existing_group in active_groups:
        if (existing_group.active and 
            existing_group.product == product_info["name"] and
            any(buyer.user.username == current_logged_user.username for buyer in existing_group.buyers)):
            
            messagebox.showwarning(
                "Already Participating", 
                f"You are already participating in a group buy for {product_info['name']}!\n\n"
                f"You cannot start another group for the same product.\n"
                f"Wait for your current group to complete or join a different product group."
            )
            return

    # Create new group buy
    new_group = GroupBuy(
        product_info["name"], 
        product_info["price"], 
        product_info["discount"],
        product_info["min_required"], 
        current_logged_user
    )
    
    active_groups.append(new_group)
    app_stats["total_groups_created"] += 1
    
    start_message = f"🚀 GROUP BUY STARTED! 🚀\n\n"
    start_message += f"📱 Product: {product_info['name']}\n"
    start_message += f"💰 Original Price: RM {product_info['price']:.2f}\n"
    start_message += f"🎯 Discount When Complete: {product_info['discount']}% OFF\n"
    start_message += f"💵 Final Price (if successful): RM {product_info['price'] * (1 - product_info['discount']/100):.2f}\n"
    start_message += f"👥 Minimum People Needed: {product_info['min_required']}\n"
    start_message += f"🟢 Current Members: 1 (You)\n\n"
    start_message += f"Share this group buy with {product_info['min_required'] - 1} more friends to activate the discount!\n\n"
    start_message += f"Group created at: {new_group.created_time}"
    
    messagebox.showinfo("Group Buy Started", start_message)
    
    # Update product status display
    update_product_status_display(product_info["name"])
    
    print(f"✅ Group buy created for {product_info['name']} by {current_logged_user.username}")

def join_existing_group_buy(target_group):
    """Join an existing group buy"""
    if not current_logged_user:
        messagebox.showwarning("Authentication Required", "Please login first to join a group!")
        return
    
    print(f"🤝 Attempting to join group for {target_group.product}")
    
    # Check if user is already in this specific group
    if any(buyer.user.username == current_logged_user.username for buyer in target_group.buyers):
        messagebox.showwarning("Already Joined", 
                             f"You are already a member of this group for {target_group.product}!")
        return
    
    # Check if user is in another group for the same product
    for other_group in active_groups:
        if (other_group.active and 
            other_group.product == target_group.product and 
            other_group != target_group and
            any(buyer.user.username == current_logged_user.username for buyer in other_group.buyers)):
            
            messagebox.showwarning(
                "Already Participating", 
                f"You are already in another group for {target_group.product}!\n\n"
                f"You can only join one group per product.\n"
                f"Complete your current group before joining another."
            )
            return
    
    # Add user to the group
    current_member_count = target_group.add_buyer(current_logged_user)
    
    # Check if group has reached minimum requirement
    if current_member_count >= target_group.min_required:
        # Group is complete - process checkout
        global total_seller_revenue
        success, checkout_message = target_group.checkout()
        
        if success:
            # Add to seller revenue
            revenue_from_group = target_group.price * (1 - target_group.discount/100) * current_member_count
            total_seller_revenue += revenue_from_group
            
            # Update statistics
            update_app_statistics()
            
            messagebox.showinfo("🎉 Group Buy Complete!", checkout_message)
        else:
            messagebox.showinfo("Group Buy Failed", checkout_message)
        
        # Update all product status displays
        for product in products_catalog:
            update_product_status_display(product["name"])
            
    else:
        # Group still needs more members
        join_success_message = f"✅ SUCCESSFULLY JOINED GROUP! ✅\n\n"
        join_success_message += f"📱 Product: {target_group.product}\n"
        join_success_message += f"👥 Group Progress: {current_member_count}/{target_group.min_required} members\n"
        join_success_message += f"🎯 Still Need: {target_group.min_required - current_member_count} more people\n"
        join_success_message += f"💰 Current Discount: {target_group.discount}% OFF\n"
        join_success_message += f"💵 Your Price (when complete): RM {target_group.price * (1 - target_group.discount/100):.2f}\n\n"
        join_success_message += f"Invite more friends to complete the group and unlock the discount!"
        
        messagebox.showinfo("Joined Group Successfully", join_success_message)
        
        # Update product status display
        update_product_status_display(target_group.product)
    
    print(f"✅ User {current_logged_user.username} joined group for {target_group.product}")

def update_product_status_display(product_name):
    """Update the status display for a specific product"""
    if product_name not in product_status_widgets:
        return
    
    status_frame = product_status_widgets[product_name]
    
    # Clear existing status widgets
    for widget in status_frame.winfo_children():
        widget.destroy()

    # Find active groups for this product
    product_active_groups = [group for group in active_groups 
                           if group.active and group.product == product_name]
    
    if not product_active_groups:
        # No active groups
        no_groups_label = tk.Label(
            status_frame, 
            text="💡 No active groups - Be the first to start one!", 
            fg="#999999", 
            bg="white",
            font=("Arial", 10, "italic")
        )
        no_groups_label.pack(anchor="w", pady=2)
        return

    # Display information for each active group
    for group in product_active_groups:
        current_members = len(group.buyers)
        
        # Group information display
        group_info_text = f"👥 {group.buyers[0].user.username}'s group: {current_members}/{group.min_required} members"
        
        # Color coding based on progress
        if current_members >= group.min_required:
            info_color = "#4CAF50"  # Green - ready
        elif current_members >= group.min_required * 0.7:
            info_color = "#FF9800"  # Orange - almost there
        else:
            info_color = "#2196F3"  # Blue - needs more people
        
        group_info_label = tk.Label(
            status_frame, 
            text=group_info_text, 
            fg=info_color, 
            bg="white", 
            font=("Arial", 10, "bold")
        )
        group_info_label.pack(anchor="w", pady=1)
        
        # Join button for this specific group
        def create_join_function(target_group):
            def join_this_specific_group():
                join_existing_group_buy(target_group)
            return join_this_specific_group
        
        join_group_button = tk.Button(
            status_frame, 
            text="🚀 Join This Group", 
            bg="#4CAF50", 
            fg="white",
            font=("Arial", 9, "bold"), 
            relief="raised",
            bd=1,
            cursor="hand2",
            command=create_join_function(group)
        )
        join_group_button.pack(anchor="w", pady=2, padx=10)

# ==================== INFORMATION AND STATISTICS ====================
def show_all_active_groups():
    """Display all active groups in a separate window"""
    if not current_logged_user:
        messagebox.showwarning("Authentication Required", "Please login first!")
        return

    currently_active_groups = [group for group in active_groups if group.active]
    
    if not currently_active_groups:
        messagebox.showinfo(
            "No Active Groups", 
            "There are no active group buys at the moment.\n\n"
            "Start a new group buy for any product to begin saving money together!"
        )
        return

    # Create new window for displaying all groups
    all_groups_window = tk.Toplevel()
    all_groups_window.title("👥 All Active Group Buys")

    all_groups_window.configure(bg="#f5f5f5")
    
    # Header
    header_frame = tk.Frame(all_groups_window, bg="#FF5722", height=60)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(
        header_frame, 
        text="👥 All Active Group Buys", 
        font=("Arial", 18, "bold"), 
        bg="#FF5722", 
        fg="white"
    ).pack(expand=True)
    
    # Main content with scrolling capability
    main_frame = tk.Frame(all_groups_window, bg="#f5f5f5")
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Create canvas and scrollbar for scrolling
    canvas = tk.Canvas(main_frame, bg="#f5f5f5")
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Display each active group
    for group in currently_active_groups:
        # Group card
        group_card = tk.Frame(scrollable_frame, bg="white", relief="raised", bd=2)
        group_card.pack(fill="x", pady=8, padx=5)
        
        group_content = tk.Frame(group_card, bg="white")
        group_content.pack(fill="x", padx=20, pady=15)
        
        # Product name
        tk.Label(
            group_content, 
            text=group.product, 
            font=("Arial", 14, "bold"), 
            bg="white", 
            fg="#333"
        ).pack(anchor="w")
        
        # Price information
        original_price = group.price
        discounted_price = group.price * (1 - group.discount/100)
        savings = original_price - discounted_price
        
        price_text = f"💰 RM {original_price:.2f} → RM {discounted_price:.2f} (Save RM {savings:.2f})"
        tk.Label(
            group_content, 
            text=price_text, 
            font=("Arial", 12, "bold"), 
            bg="white", 
            fg="#FF5722"
        ).pack(anchor="w", pady=2)
        
        # Discount badge
        discount_text = f"🎯 {group.discount}% OFF"
        tk.Label(
            group_content, 
            text=discount_text, 
            font=("Arial", 11, "bold"), 
            bg="#4CAF50", 
            fg="white",
            padx=8, 
            pady=2
        ).pack(anchor="w", pady=2)
        
        # Group status
        current_members = len(group.buyers)
        progress_text = f"👥 {current_members}/{group.min_required} people joined"
        progress_color = "#4CAF50" if current_members >= group.min_required else "#FF9800"
        
        tk.Label(
            group_content, 
            text=progress_text, 
            font=("Arial", 11), 
            bg="white", 
            fg=progress_color
        ).pack(anchor="w", pady=2)
        
        # Group starter info
        starter_text = f"Started by: {group.buyers[0].user.username} at {group.created_time}"
        tk.Label(
            group_content, 
            text=starter_text, 
            font=("Arial", 9), 
            bg="white", 
            fg="#666"
        ).pack(anchor="w", pady=2)
        
        # Join button
        def create_join_action_for_popup(target_group):
            def join_and_close():
                join_existing_group_buy(target_group)
                all_groups_window.destroy()
                # Refresh main catalog displays
                for product in products_catalog:
                    update_product_status_display(product["name"])
            return join_and_close
        
        join_button = create_styled_button(
            group_content, 
            "🚀 Join This Group", 
            "#FF5722", 
            command=create_join_action_for_popup(group),
            width=20,
            height=1
        )
        join_button.pack(pady=(10, 0))
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

def show_user_statistics():
    """Show current user's group buy statistics"""
    if not current_logged_user:
        messagebox.showwarning("Authentication Required", "Please login first!")
        return
    
    # Calculate user statistics
    user_active_groups = []
    user_completed_groups = []
    user_failed_groups = []
    total_user_savings = 0
    
    for group in active_groups:
        for buyer in group.buyers:
            if buyer.user.username == current_logged_user.username:
                if group.active:
                    user_active_groups.append(group)
                elif group.completed_time:  # Successfully completed
                    user_completed_groups.append(group)
                    total_user_savings += buyer.savings
                else:  # Failed group
                    user_failed_groups.append(group)
                break
    
    # Create statistics message
    stats_message = f"📊 YOUR GROUP BUY STATISTICS 📊\n\n"
    stats_message += f"👤 User: {current_logged_user.username}\n"
    stats_message += f"📅 Member Since: {current_logged_user.created_date}\n\n"
    
    stats_message += f"📈 ACTIVITY SUMMARY:\n"
    stats_message += f"🟡 Active Groups: {len(user_active_groups)}\n"
    stats_message += f"✅ Completed Groups: {len(user_completed_groups)}\n"
    stats_message += f"❌ Failed Groups: {len(user_failed_groups)}\n"
    stats_message += f"💰 Total Money Saved: RM {total_user_savings:.2f}\n\n"
    
    if user_active_groups:
        stats_message += f"🟡 YOUR ACTIVE GROUPS:\n"
        for group in user_active_groups:
            stats_message += f"  • {group.product} ({len(group.buyers)}/{group.min_required} members)\n"
        stats_message += "\n"
    
    if user_completed_groups:
        stats_message += f"✅ RECENT COMPLETED GROUPS:\n"
        for group in user_completed_groups[-5:]:  # Show last 5
            individual_savings = group.price - group.price * (1 - group.discount/100)
            stats_message += f"  • {group.product} - Saved RM {individual_savings:.2f}\n"
        stats_message += "\n"
    
    if len(current_logged_user.join_history) > 0:
        stats_message += f"📋 RECENT ACTIVITY:\n"
        for activity in current_logged_user.join_history[-5:]:
            stats_message += f"  • {activity}\n"
    
    messagebox.showinfo("Your Statistics", stats_message)

def show_seller_revenue_dashboard():
    """Display comprehensive seller revenue dashboard"""
    update_app_statistics()
    
    completed_groups = [g for g in active_groups if not g.active and g.completed_time]
    active_group_count = len([g for g in active_groups if g.active])
    
    revenue_message = f"💰 SELLER REVENUE DASHBOARD 💰\n\n"
    revenue_message += f"📊 FINANCIAL OVERVIEW:\n"
    revenue_message += f"💵 Total Revenue: RM {total_seller_revenue:.2f}\n"
    revenue_message += f"✅ Completed Groups: {app_stats['successful_groups']}\n"
    revenue_message += f"📦 Total Items Sold: {app_stats['total_items_sold']}\n"
    revenue_message += f"🟡 Currently Active Groups: {active_group_count}\n"
    revenue_message += f"❌ Failed Groups: {app_stats['failed_groups']}\n\n"
    
    if app_stats['successful_groups'] > 0:
        avg_revenue = total_seller_revenue / app_stats['successful_groups']
        revenue_message += f"📈 Average Revenue per Group: RM {avg_revenue:.2f}\n"
    
    revenue_message += f"👥 Total Registered Users: {app_stats['total_users_registered']}\n"
    revenue_message += f"🎯 Success Rate: {(app_stats['successful_groups']/(max(app_stats['total_groups_created'], 1)))*100:.1f}%\n\n"
    
    if completed_groups:
        revenue_message += f"🏆 TOP SELLING PRODUCTS:\n"
        product_sales = {}
        for group in completed_groups:
            if group.product in product_sales:
                product_sales[group.product] += len(group.buyers)
            else:
                product_sales[group.product] = len(group.buyers)
        
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
        for i, (product, sales) in enumerate(sorted_products[:5], 1):
            revenue_message += f"  {i}. {product}: {sales} units sold\n"
    
    messagebox.showinfo("Seller Revenue Dashboard", revenue_message)

def show_application_help():
    """Show help and instructions for using the application"""
    help_message = f"📱 SHOPEE GROUP BUY - USER GUIDE 📱\n\n"
    help_message += f"🎯 HOW GROUP BUYING WORKS:\n"
    help_message += f"1. Choose a product you want to buy\n"
    help_message += f"2. Start a group OR join an existing group\n"
    help_message += f"3. When enough people join, everyone gets the discount!\n"
    help_message += f"4. If not enough people join, the group buy fails\n\n"
    
    help_message += f"🚀 GETTING STARTED:\n"
    help_message += f"• Browse products in the main catalog\n"
    help_message += f"• Click 'Start Group Buy' to create a new group\n"
    help_message += f"• Click 'Join Group' to join existing groups\n"
    help_message += f"• Use 'All Groups' to see all active groups\n\n"
    
    help_message += f"💡 TIPS FOR SUCCESS:\n"
    help_message += f"• Share group buys with friends to complete them faster\n"
    help_message += f"• Join groups that are close to completion\n"
    help_message += f"• Check 'My Stats' to track your savings\n"
    help_message += f"• You can only join one group per product\n\n"
    
    help_message += f"📊 FEATURES:\n"
    help_message += f"• Real-time group progress tracking\n"
    help_message += f"• Personal statistics and savings history\n"
    help_message += f"• Seller revenue analytics\n"
    help_message += f"• Multiple product categories\n\n"
    
    help_message += f"❓ Need more help? Contact our support team!"
    
    messagebox.showinfo("User Guide", help_message)

# ==================== MAIN CATALOG WINDOW ====================
def open_main_shopping_catalog():
    """Open the main shopping catalog window"""
    catalog_window = tk.Toplevel(main_login_window)
    catalog_window.title("🛒 Shopee Group Buy Mall")
    
    catalog_window.configure(bg="#f8f9fa")
    catalog_window.resizable(True, True)
    
    # Prevent accidental window closing
    catalog_window.protocol("WM_DELETE_WINDOW", lambda: logout_current_user(catalog_window))
    
    # ===== HEADER SECTION =====
    header_frame = tk.Frame(catalog_window, bg="#FF5722", height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    header_content = tk.Frame(header_frame, bg="#FF5722")
    header_content.pack(expand=True, fill="both", padx=25, pady=15)
    
    # Logo and title
    title_label = tk.Label(
        header_content, 
        text="🛒 Shopee Group Buy Mall", 
        font=("Arial", 20, "bold"), 
        bg="#FF5722", 
        fg="white"
    )
    title_label.pack(side="left")
    
    # User controls section
    user_controls_frame = tk.Frame(header_content, bg="#FF5722")
    user_controls_frame.pack(side="right")
    
    # Welcome user label
    user_welcome_label = tk.Label(
        user_controls_frame, 
        text=f"👤 Welcome, {current_logged_user.username}!", 
        font=("Arial", 12, "bold"), 
        bg="#FF5722", 
        fg="white"
    )
    user_welcome_label.pack(side="left", padx=(0, 20))
    
    # Help button
    help_button = tk.Button(
        user_controls_frame, 
        text="❓ Help", 
        bg="#4CAF50", 
        fg="white",
        font=("Arial", 10, "bold"), 
        command=show_application_help,
        cursor="hand2"
    )
    help_button.pack(side="left", padx=(0, 10))
    
    # Logout button
    logout_button = tk.Button(
        user_controls_frame, 
        text="🚪 Logout", 
        bg="#d32f2f", 
        fg="white",
        font=("Arial", 10, "bold"), 
        command=lambda: logout_current_user(catalog_window),
        cursor="hand2"
    )
    logout_button.pack(side="right")
    
    # ===== MAIN CONTENT AREA =====
    main_content_frame = tk.Frame(catalog_window, bg="#f8f9fa")
    main_content_frame.pack(fill="both", expand=True, padx=25, pady=20)
    
    # ===== QUICK ACTION BUTTONS =====
    quick_actions_frame = tk.Frame(main_content_frame, bg="#f8f9fa")
    quick_actions_frame.pack(fill="x", pady=(0, 25))
    
    # Left side buttons
    left_actions = tk.Frame(quick_actions_frame, bg="#f8f9fa")
    left_actions.pack(side="left")
    
    all_groups_button = create_styled_button(
        left_actions, "👥 All Active Groups", "#4CAF50", 
        command=show_all_active_groups, width=20, height=1
    )
    all_groups_button.pack(side="left", padx=(0, 15))
    
    my_stats_button = create_styled_button(
        left_actions, "📊 My Statistics", "#2196F3", 
        command=show_user_statistics, width=20, height=1
    )
    my_stats_button.pack(side="left", padx=(0, 15))
    
    # Right side button
    right_actions = tk.Frame(quick_actions_frame, bg="#f8f9fa")
    right_actions.pack(side="right")
    
    revenue_button = create_styled_button(
        right_actions, "💰 Revenue Dashboard", "#9C27B0", 
        command=show_seller_revenue_dashboard, width=22, height=1
    )
    revenue_button.pack(side="right")
    
    # ===== PRODUCTS SECTION HEADER =====
    products_header_frame = tk.Frame(main_content_frame, bg="#f8f9fa")
    products_header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(
        products_header_frame, 
        text="🛍️ Available Products", 
        font=("Arial", 18, "bold"), 
        bg="#f8f9fa", 
        fg="#333"
    ).pack(side="left")
    
    # Product count
    tk.Label(
        products_header_frame, 
        text=f"({len(products_catalog)} items available)", 
        font=("Arial", 12), 
        bg="#f8f9fa", 
        fg="#666"
    ).pack(side="left", padx=(10, 0))
    
    # ===== PRODUCTS CATALOG =====
    # Create scrollable area for products
    products_canvas = tk.Canvas(main_content_frame, bg="#f8f9fa")
    products_scrollbar = ttk.Scrollbar(main_content_frame, orient="vertical", command=products_canvas.yview)
    products_scrollable_frame = tk.Frame(products_canvas, bg="#f8f9fa")
    
    products_scrollable_frame.bind(
        "<Configure>",
        lambda e: products_canvas.configure(scrollregion=products_canvas.bbox("all"))
    )
    
    products_canvas.create_window((0, 0), window=products_scrollable_frame, anchor="nw")
    products_canvas.configure(yscrollcommand=products_scrollbar.set)
    
    # Display each product
    for product in products_catalog:
        # Product card container
        product_card = tk.Frame(products_scrollable_frame, bg="white", relief="raised", bd=3)
        product_card.pack(fill="x", pady=12, padx=8)
        
        product_content = tk.Frame(product_card, bg="white")
        product_content.pack(fill="x", padx=25, pady=20)
        
        # ===== PRODUCT HEADER =====
        product_header = tk.Frame(product_content, bg="white")
        product_header.pack(fill="x", pady=(0, 8))
        
        # Product name
        product_name_label = tk.Label(
            product_header, 
            text=product["name"], 
            font=("Arial", 16, "bold"), 
            bg="white", 
            fg="#333"
        )
        product_name_label.pack(side="left")
        
        # Category badge
        category_badge = tk.Label(
            product_header, 
            text=f"📂 {product['category']}", 
            font=("Arial", 10, "bold"), 
            bg="#E3F2FD", 
            fg="#1976D2",
            padx=8, 
            pady=2
        )
        category_badge.pack(side="right")
        
        # ===== PRODUCT DESCRIPTION =====
        description_label = tk.Label(
            product_content, 
            text=product["description"], 
            font=("Arial", 11), 
            bg="white", 
            fg="#666",
            wraplength=700,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(0, 12))
        
        # ===== PRICING SECTION =====
        pricing_frame = tk.Frame(product_content, bg="white")
        pricing_frame.pack(fill="x", pady=(0, 12))
        
        # Original price
        original_price_label = tk.Label(
            pricing_frame, 
            text=f"RM {product['price']:.2f}", 
            font=("Arial", 18, "bold"), 
            bg="white", 
            fg="#FF5722"
        )
        original_price_label.pack(side="left")
        
        # Arrow
        arrow_label = tk.Label(
            pricing_frame, 
            text="→", 
            font=("Arial", 16, "bold"), 
            bg="white", 
            fg="#999"
        )
        arrow_label.pack(side="left", padx=(15, 15))
        
        # Discounted price
        discounted_price = product['price'] * (1 - product['discount']/100)
        discounted_price_label = tk.Label(
            pricing_frame, 
            text=f"RM {discounted_price:.2f}", 
            font=("Arial", 18, "bold"), 
            bg="white", 
            fg="#4CAF50"
        )
        discounted_price_label.pack(side="left")
        
        # Discount percentage badge
        discount_badge = tk.Label(
            pricing_frame, 
            text=f"-{product['discount']}% OFF", 
            font=("Arial", 12, "bold"), 
            bg="#4CAF50", 
            fg="white",
            padx=10, 
            pady=4
        )
        discount_badge.pack(side="left", padx=(15, 0))
        
        # Savings amount
        savings_amount = product['price'] - discounted_price
        savings_label = tk.Label(
            pricing_frame, 
            text=f"Save RM {savings_amount:.2f}!", 
            font=("Arial", 12, "bold"), 
            bg="white", 
            fg="#4CAF50"
        )
        savings_label.pack(side="right")
        
        # ===== GROUP REQUIREMENTS =====
        requirements_frame = tk.Frame(product_content, bg="white")
        requirements_frame.pack(fill="x", pady=(0, 15))
        
        requirements_label = tk.Label(
            requirements_frame, 
            text=f"👥 Minimum {product['min_required']} people needed to unlock discount", 
            font=("Arial", 12, "bold"), 
            bg="white", 
            fg="#666"
        )
        requirements_label.pack(side="left")
        
        # ===== ACTION SECTION =====
        action_section = tk.Frame(product_content, bg="white")
        action_section.pack(fill="x", pady=(10, 0))
        
        # Start group buy button
        start_group_button = create_styled_button(
            action_section, 
            "🚀 Start Group Buy", 
            "#FF5722", 
            command=lambda p=product: start_new_group_buy(p),
            width=20,
            height=1
        )
        start_group_button.pack(side="right")
        
        # ===== STATUS DISPLAY AREA =====
        status_display_frame = tk.Frame(product_content, bg="white")
        status_display_frame.pack(fill="x", pady=(15, 0))
        
        # Store reference for status updates
        product_status_widgets[product["name"]] = status_display_frame
        
        # Initialize status display
        update_product_status_display(product["name"])
        
        # Add separator line
        separator_line = tk.Frame(product_content, height=1, bg="#E0E0E0")
        separator_line.pack(fill="x", pady=(15, 0))
    
    # Pack canvas and scrollbar
    products_canvas.pack(side="left", fill="both", expand=True)
    products_scrollbar.pack(side="right", fill="y")
    
    # Mouse wheel scrolling for products
    def on_products_mousewheel(event):
        products_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    products_canvas.bind_all("<MouseWheel>", on_products_mousewheel)
    
    print(f"🏪 Catalog opened for user: {current_logged_user.username}")

# ==================== MAIN LOGIN WINDOW SETUP ====================
main_login_window = tk.Tk()
main_login_window.title("🛒 Shopee Group Buy - Login Portal")
main_login_window.configure(bg="white")
main_login_window.resizable(False, False)

# Center the window on screen
main_login_window.eval('tk::PlaceWindow . center')

# ===== HEADER SECTION =====
header_section = tk.Frame(main_login_window, bg="#FF5722", height=120)
header_section.pack(fill="x")
header_section.pack_propagate(False)

# Main title
main_title_label = tk.Label(
    header_section, 
    text="🛒 Shopee Group Buy", 
    font=("Arial", 24, "bold"), 
    bg="#FF5722", 
    fg="white"
)
main_title_label.pack(expand=True, pady=(30, 8))

# Subtitle
subtitle_label = tk.Label(
    header_section, 
    text="Save Money by Shopping Together!", 
    font=("Arial", 14), 
    bg="#FF5722", 
    fg="white"
)
subtitle_label.pack()

# ===== MAIN CONTENT AREA =====
main_content_area = tk.Frame(main_login_window, bg="white")
main_content_area.pack(fill="both", expand=True, padx=40, pady=35)

# ===== LOGIN SECTION =====
login_section = tk.LabelFrame(
    main_content_area, 
    text="🔐 Login to Your Account", 
    font=("Arial", 14, "bold"), 
    bg="white", 
    fg="#333",
    padx=30, 
    pady=25, 
    relief="raised", 
    bd=3
)
login_section.pack(fill="x", pady=(0, 30))

# Username field for login
tk.Label(login_section, text="Username:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
username_login_entry = tk.Entry(
    login_section, 
    width=35, 
    font=("Arial", 13), 
    relief="solid", 
    bd=2
)
username_login_entry.pack(pady=(8, 18), ipady=8)

# Password field for login
tk.Label(login_section, text="Password:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
password_login_entry = tk.Entry(
    login_section, 
    width=35, 
    show="*", 
    font=("Arial", 13), 
    relief="solid", 
    bd=2
)
password_login_entry.pack(pady=(8, 25), ipady=8)

# Login button
login_button = create_styled_button(
    login_section, 
    "🚀 LOGIN NOW", 
    "#FF5722", 
    command=login_existing_user,
    width=25,
    height=2
)
login_button.pack()

# ===== SEPARATOR =====
separator_frame = tk.Frame(main_content_area, height=3, bg="#E0E0E0")
separator_frame.pack(fill="x", pady=25)

# "OR" label
or_label = tk.Label(
    main_content_area, 
    text="OR", 
    font=("Arial", 12, "bold"), 
    bg="white", 
    fg="#999"
)
or_label.pack()

# ===== REGISTRATION SECTION =====
registration_section = tk.LabelFrame(
    main_content_area, 
    text="📝 Create New Account", 
    font=("Arial", 14, "bold"), 
    bg="white", 
    fg="#333",
    padx=30, 
    pady=25, 
    relief="raised", 
    bd=3
)
registration_section.pack(fill="x", pady=(20, 0))

# Username field for registration
tk.Label(registration_section, text="Choose Username:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
username_reg_entry = tk.Entry(
    registration_section, 
    width=35, 
    font=("Arial", 13), 
    relief="solid", 
    bd=2
)
username_reg_entry.pack(pady=(8, 18), ipady=8)

# Password field for registration
tk.Label(registration_section, text="Choose Password:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
password_reg_entry = tk.Entry(
    registration_section, 
    width=35, 
    show="*", 
    font=("Arial", 13), 
    relief="solid", 
    bd=2
)
password_reg_entry.pack(pady=(8, 25), ipady=8)

# Registration button
registration_button = create_styled_button(
    registration_section, 
    "✨ CREATE ACCOUNT", 
    "#4CAF50", 
    command=register_new_user,
    width=25,
    height=2
)
registration_button.pack()

# ===== KEYBOARD SHORTCUTS =====
def handle_keyboard_shortcuts(event):
    """Handle Enter key press for login/registration"""
    focused_widget = main_login_window.focus_get()
    
    if focused_widget in [username_login_entry, password_login_entry]:
        if username_login_entry.get().strip() and password_login_entry.get().strip():
            login_existing_user()
        else:
            messagebox.showwarning("Incomplete Input", "Please fill in both username and password for login!")
    
    elif focused_widget in [username_reg_entry, password_reg_entry]:
        if username_reg_entry.get().strip() and password_reg_entry.get().strip():
            register_new_user()
        else:
            messagebox.showwarning("Incomplete Input", "Please fill in both username and password for registration!")

main_login_window.bind('<Return>', handle_keyboard_shortcuts)

# ===== SET INITIAL FOCUS =====
username_login_entry.focus()

# ===== DEBUG INFORMATION =====
print("🚀 SHOPEE GROUP BUY APPLICATION STARTED")
print("=" * 50)
print("📋 Available Functions:")
print("  • register_new_user() - Register a new account")
print("  • login_existing_user() - Login with existing account")
print("  • start_new_group_buy(product) - Start a group buy")
print("  • join_existing_group_buy(group) - Join a group")
print("=" * 50)
print("🎯 TESTING:")
print("1. Create account with username/password (min 3/4 chars)")
print("2. Login with your credentials")
print("3. Start or join group buys!")
print("=" * 50)
print(f"📊 Initial Stats: {len(products_catalog)} products available")
print("✅ Application ready to use!")

# ===== START THE APPLICATION =====
if __name__ == "__main__":
    main_login_window.mainloop()
