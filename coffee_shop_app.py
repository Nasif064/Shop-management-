import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Coffee Shop Management",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
# Custom CSS with coffee background image
# Custom CSS with clean coffee background only
st.markdown("""
<style>
    /* Pure coffee background without any overlays */
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1497935586351-b67a49e012bf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Make content areas completely transparent */
    .main .block-container,
    .metric-card,
    .menu-item,
    .stDataFrame {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Restore your original component styles */
    .main-header {
        background: linear-gradient(90deg, #8B4513 0%, #D2691E 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
    }
    
    .status-completed { background: #00C851; color: white; }
    .status-pending { background: #ffbb33; color: white; }
    .status-cancelled { background: #ff4444; color: white; }
</style>
""", unsafe_allow_html=True)

class MenuItem:
    def __init__(self, name: str, price: float, category: str, ingredients: List[str] = None):
        self.name = name
        self.price = price
        self.category = category
        self.ingredients = ingredients or []

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'ingredients': self.ingredients
        }

class InventoryItem:
    def __init__(self, name: str, quantity: int, unit: str, min_stock: int = 10):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.min_stock = min_stock

    def is_low_stock(self):
        return self.quantity <= self.min_stock

    def to_dict(self):
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'min_stock': self.min_stock,
            'status': 'Low Stock' if self.is_low_stock() else 'OK'
        }

class Order:
    def __init__(self, order_id: int, customer_name: str = "Walk-in"):
        self.order_id = order_id
        self.customer_name = customer_name
        self.items = []
        self.total = 0.0
        self.timestamp = datetime.now()
        self.status = "pending"

    def add_item(self, menu_item: MenuItem, quantity: int = 1):
        self.items.append({
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': quantity,
            'category': menu_item.category,
            'subtotal': menu_item.price * quantity
        })
        self.total += menu_item.price * quantity

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'items': len(self.items),
            'total': self.total,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M"),
            'status': self.status
        }

# Initialize session state
def init_session_state():
    if 'menu' not in st.session_state:
        st.session_state.menu = {}
        setup_default_menu()
    
    if 'inventory' not in st.session_state:
        st.session_state.inventory = {}
        setup_default_inventory()
    
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    
    if 'order_counter' not in st.session_state:
        st.session_state.order_counter = 1
    
    if 'daily_sales' not in st.session_state:
        st.session_state.daily_sales = 0.0
    
    if 'current_order' not in st.session_state:
        st.session_state.current_order = None

def setup_default_menu():
    """Setup default menu items"""
    default_items = [
        MenuItem("Espresso", 2.50, "Coffee", ["Coffee beans", "Water"]),
        MenuItem("Americano", 3.00, "Coffee", ["Coffee beans", "Water"]),
        MenuItem("Cappuccino", 4.00, "Coffee", ["Coffee beans", "Milk", "Water"]),
        MenuItem("Latte", 4.50, "Coffee", ["Coffee beans", "Milk", "Water"]),
        MenuItem("Mocha", 5.00, "Coffee", ["Coffee beans", "Milk", "Chocolate", "Water"]),
        MenuItem("Croissant", 3.50, "Pastry", ["Flour", "Butter"]),
        MenuItem("Muffin", 2.75, "Pastry", ["Flour", "Sugar", "Eggs"]),
        MenuItem("Green Tea", 2.00, "Tea", ["Tea leaves", "Water"]),
    ]
    
    for item in default_items:
        st.session_state.menu[item.name] = item

def setup_default_inventory():
    """Setup default inventory items"""
    default_inventory = [
        InventoryItem("Coffee beans", 100, "kg", 20),
        InventoryItem("Milk", 50, "liters", 10),
        InventoryItem("Water", 200, "liters", 50),
        InventoryItem("Sugar", 25, "kg", 5),
        InventoryItem("Chocolate", 15, "kg", 3),
        InventoryItem("Flour", 30, "kg", 5),
        InventoryItem("Butter", 10, "kg", 2),
        InventoryItem("Eggs", 100, "pieces", 20),
        InventoryItem("Tea leaves", 5, "kg", 1),
    ]
    
    for item in default_inventory:
        st.session_state.inventory[item.name] = item

def display_menu():
    """Display menu in Streamlit"""
    st.header("☕ Menu")
    
    # Group items by category
    categories = {}
    for item in st.session_state.menu.values():
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)
    
    for category, items in categories.items():
        st.subheader(f"{category}")
        
        # Create columns for better layout
        cols = st.columns(2)
        for idx, item in enumerate(items):
            with cols[idx % 2]:
                st.write(f"**{item.name}** - ${item.price:.2f}")
                if item.ingredients:
                    st.caption(f"Ingredients: {', '.join(item.ingredients)}")

def display_inventory():
    """Display inventory in Streamlit"""
    st.header("📦 Inventory Management")
    
    # Create inventory DataFrame
    inventory_data = []
    for item in st.session_state.inventory.values():
        inventory_data.append(item.to_dict())
    
    if inventory_data:
        df = pd.DataFrame(inventory_data)
        
        # Style the dataframe
        def color_status(val):
            color = 'red' if val == 'Low Stock' else 'green'
            return f'color: {color}'
        
        styled_df = df.style.applymap(color_status, subset=['status'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Show low stock alerts
        low_stock = [item for item in st.session_state.inventory.values() if item.is_low_stock()]
        if low_stock:
            st.error(f"⚠️ Low Stock Alert: {', '.join([item.name for item in low_stock])}")
    
    # Add inventory form
    st.subheader("Add/Update Inventory")
    with st.form("inventory_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            item_name = st.text_input("Item Name")
        with col2:
            quantity = st.number_input("Quantity", min_value=0, value=0)
        with col3:
            unit = st.text_input("Unit (kg, liters, pieces)")
        with col4:
            min_stock = st.number_input("Min Stock Level", min_value=1, value=10)
        
        if st.form_submit_button("Add/Update Item"):
            if item_name and quantity > 0 and unit:
                if item_name in st.session_state.inventory:
                    st.session_state.inventory[item_name].quantity += quantity
                    st.success(f"Updated {item_name}: {st.session_state.inventory[item_name].quantity} {unit}")
                else:
                    st.session_state.inventory[item_name] = InventoryItem(item_name, quantity, unit, min_stock)
                    st.success(f"Added {item_name} to inventory: {quantity} {unit}")
                st.rerun()

def create_order_page():
    """Create order page"""
    st.header("🛒 Create Order")
    
    # Customer info
    customer_name = st.text_input("Customer Name", value="Walk-in")
    
    # Create new order if none exists
    if st.session_state.current_order is None:
        if st.button("Start New Order"):
            st.session_state.current_order = Order(st.session_state.order_counter, customer_name)
            st.session_state.order_counter += 1
            st.success(f"Started Order #{st.session_state.current_order.order_id}")
            st.rerun()
    
    # Display current order
    if st.session_state.current_order is not None:
        order = st.session_state.current_order
        
        st.subheader(f"Order #{order.order_id} - {order.customer_name}")
        
        # Add items to order
        col1, col2 = st.columns([3, 1])
        with col1:
            item_names = list(st.session_state.menu.keys())
            selected_item = st.selectbox("Select Item", [""] + item_names)
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        
        if st.button("Add to Order") and selected_item:
            menu_item = st.session_state.menu[selected_item]
            
            # Check ingredient availability
            can_make = True
            for ingredient in menu_item.ingredients:
                if ingredient in st.session_state.inventory:
                    if st.session_state.inventory[ingredient].quantity < quantity:
                        st.error(f"Cannot make {selected_item}: Not enough {ingredient}")
                        can_make = False
                        break
            
            if can_make:
                order.add_item(menu_item, quantity)
                st.success(f"Added {quantity}x {selected_item} to order")
                st.rerun()
        
        # Display order items
        if order.items:
            st.subheader("Order Items")
            items_df = pd.DataFrame(order.items)
            st.dataframe(items_df, use_container_width=True)
            st.write(f"**Total: ${order.total:.2f}**")
            
            # Order actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Complete Order", type="primary"):
                    complete_order(order)
                    st.session_state.current_order = None
                    st.success("Order completed successfully!")
                    st.rerun()
            with col2:
                if st.button("Cancel Order"):
                    order.status = "cancelled"
                    st.session_state.orders.append(order)
                    st.session_state.current_order = None
                    st.warning("Order cancelled")
                    st.rerun()

def complete_order(order: Order):
    """Complete an order and update inventory"""
    # Deduct ingredients from inventory
    for item in order.items:
        menu_item = st.session_state.menu[item['name']]
        for ingredient in menu_item.ingredients:
            if ingredient in st.session_state.inventory:
                st.session_state.inventory[ingredient].quantity -= item['quantity']
    
    order.status = "completed"
    st.session_state.orders.append(order)
    st.session_state.daily_sales += order.total

def view_orders():
    """View orders page"""
    st.header("📋 Orders")
    
    if not st.session_state.orders:
        st.info("No orders yet")
        return
    
    # Filter options
    status_filter = st.selectbox("Filter by Status", ["All", "completed", "cancelled", "pending"])
    
    # Create orders DataFrame
    orders_data = []
    for order in st.session_state.orders:
        if status_filter == "All" or order.status == status_filter:
            orders_data.append(order.to_dict())
    
    if orders_data:
        df = pd.DataFrame(orders_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info(f"No {status_filter} orders found")

def add_menu_item_page():
    """Add menu item page with enhanced validation and feedback"""
    st.header("➕ Add Menu Item")
    
    with st.form("menu_form", clear_on_submit=True):  # Clear form after submission
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Item Name *", help="Required field")
            price = st.number_input("Price ($) *", min_value=0.0, value=0.0, step=0.25, help="Must be > $0")
        with col2:
            category = st.text_input("Category *", help="e.g., Coffee, Pastry, Tea")
            ingredients = st.text_area("Ingredients (one per line)", help="List each ingredient on a new line")
        
        submitted = st.form_submit_button("✅ Add Menu Item")
        
        if submitted:
            # Validate inputs
            if not name:
                st.error("❌ Item Name is required!")
                return
            if price <= 0:
                st.error("❌ Price must be greater than $0!")
                return
            if not category:
                st.error("❌ Category is required!")
                return
            
            # Process ingredients (split by newlines and remove empty entries)
            ingredient_list = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
            
            # Check if item already exists
            if name in st.session_state.menu:
                st.warning(f"⚠️ '{name}' already exists in the menu. Updating instead.")
            
            # Add/update the menu item
            st.session_state.menu[name] = MenuItem(name, price, category, ingredient_list)
            st.success(f"✅ **{name}** (${price:.2f}) added to **{category}** category!")
            
            # Debug: Show current menu (optional)
            st.write("### Current Menu Items:")
            st.json({k: v.to_dict() for k, v in st.session_state.menu.items()})
            
            # Rerun to reflect changes
            st.rerun()

def daily_report():
    """Display daily report"""
    st.header("📊 Daily Report")
    
    completed_orders = [o for o in st.session_state.orders if o.status == "completed"]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", len(completed_orders))
    with col2:
        st.metric("Total Sales", f"${st.session_state.daily_sales:.2f}")
    with col3:
        if completed_orders:
            avg_order = st.session_state.daily_sales / len(completed_orders)
            st.metric("Average Order", f"${avg_order:.2f}")
        else:
            st.metric("Average Order", "$0.00")
    
    # Popular items analysis
    if completed_orders:
        st.subheader("Popular Items")
        item_count = {}
        for order in completed_orders:
            for item in order.items:
                name = item['name']
                item_count[name] = item_count.get(name, 0) + item['quantity']
        
        if item_count:
            # Create DataFrame for popular items
            popular_df = pd.DataFrame(list(item_count.items()), columns=['Item', 'Quantity Sold'])
            popular_df = popular_df.sort_values('Quantity Sold', ascending=False)
            st.dataframe(popular_df, use_container_width=True)

def main():
    """Main Streamlit app"""
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("☕ Coffee Shop Manager")
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["Dashboard", "Menu", "Inventory", "Create Order", "View Orders", "Add Menu Item", "Daily Report"]
    )
    
    # Main content based on selected page
    if page == "Dashboard":
        st.title("☕ Coffee Shop Management System")
        st.write("Welcome to your coffee shop management dashboard!")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Menu Items", len(st.session_state.menu))
        with col2:
            st.metric("Inventory Items", len(st.session_state.inventory))
        with col3:
            st.metric("Today's Orders", len([o for o in st.session_state.orders if o.status == "completed"]))
        with col4:
            st.metric("Daily Sales", f"${st.session_state.daily_sales:.2f}")
        
        # Low stock alerts on dashboard
        low_stock = [item for item in st.session_state.inventory.values() if item.is_low_stock()]
        if low_stock:
            st.error(f"⚠️ Low Stock Alert: {', '.join([item.name for item in low_stock])}")
    
    elif page == "Menu":
        display_menu()
    
    elif page == "Inventory":
        display_inventory()
    
    elif page == "Create Order":
        create_order_page()
    
    elif page == "View Orders":
        view_orders()
    
    elif page == "Add Menu Item":
        add_menu_item_page()
    
    elif page == "Daily Report":
        daily_report()

if __name__ == "__main__":
    main()