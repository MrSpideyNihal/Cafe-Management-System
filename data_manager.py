import os
import json
import time
from datetime import datetime, date
import pandas as pd

class DataManager:
    def __init__(self):
        self.menu_file = "data/menu.txt"
        self.sales_file = "data/sales.txt"
        self.inventory_file = "data/inventory.txt"
        
        # Ensure data files exist
        self._ensure_file_exists(self.menu_file)
        self._ensure_file_exists(self.sales_file)
        self._ensure_file_exists(self.inventory_file)
    
    def _ensure_file_exists(self, filepath):
        """Create file if it doesn't exist"""
        if not os.path.exists(filepath):
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(filepath, 'w') as f:
                if filepath == self.menu_file or filepath == self.inventory_file:
                    f.write('[]')  # Empty JSON array
                else:
                    f.write('[]')  # Empty JSON array for sales
    
    # Menu Management Functions
    def get_menu_items(self):
        """Retrieve all menu items"""
        try:
            with open(self.menu_file, 'r') as f:
                content = f.read()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, FileNotFoundError):
            # In case of corruption or missing file, create a new one
            self._ensure_file_exists(self.menu_file)
            return []
    
    def add_menu_item(self, item):
        """Add a new menu item"""
        all_items = self.get_menu_items()
        
        # Check if item with this name already exists
        for existing_item in all_items:
            if existing_item.get('name') == item.get('name'):
                return False, "An item with this name already exists."
        
        # Add the new item with timestamp
        item['id'] = int(time.time() * 1000)  # Generate unique ID based on timestamp
        item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        all_items.append(item)
        
        with open(self.menu_file, 'w') as f:
            f.write(json.dumps(all_items, indent=2))
        
        # Update inventory if needed
        self._update_inventory_for_new_item(item)
        
        return True, "Item added successfully."
    
    def update_menu_item(self, item_id, updated_data):
        """Update an existing menu item"""
        all_items = self.get_menu_items()
        
        for i, item in enumerate(all_items):
            if item.get('id') == item_id:
                # Update the item
                all_items[i].update(updated_data)
                all_items[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(self.menu_file, 'w') as f:
                    f.write(json.dumps(all_items, indent=2))
                return True, "Item updated successfully."
        
        return False, "Item not found."
    
    def delete_menu_item(self, item_id):
        """Delete a menu item"""
        all_items = self.get_menu_items()
        
        for i, item in enumerate(all_items):
            if item.get('id') == item_id:
                # Remove the item
                deleted_item = all_items.pop(i)
                
                with open(self.menu_file, 'w') as f:
                    f.write(json.dumps(all_items, indent=2))
                return True, "Item deleted successfully."
        
        return False, "Item not found."
    
    # Sales Tracking Functions
    def get_sales(self, date_filter=None):
        """Retrieve sales data with optional date filtering"""
        try:
            with open(self.sales_file, 'r') as f:
                content = f.read()
                all_sales = json.loads(content) if content else []
                
                if date_filter:
                    # Filter sales by date
                    filtered_sales = [
                        sale for sale in all_sales 
                        if sale.get('date') == date_filter
                    ]
                    return filtered_sales
                
                return all_sales
        except (json.JSONDecodeError, FileNotFoundError):
            self._ensure_file_exists(self.sales_file)
            return []
    
    def add_sale(self, sale_data):
        """Add a new sale record"""
        all_sales = self.get_sales()
        
        # Add timestamp and sale ID
        sale_data['id'] = int(time.time() * 1000)
        sale_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'date' not in sale_data:
            sale_data['date'] = date.today().strftime('%Y-%m-%d')
        
        all_sales.append(sale_data)
        
        with open(self.sales_file, 'w') as f:
            f.write(json.dumps(all_sales, indent=2))
        
        # Update inventory based on the sale
        self._update_inventory_from_sale(sale_data)
        
        return True, "Sale recorded successfully."
    
    def get_daily_sales_summary(self, target_date=None):
        """Get a summary of sales for a specific date"""
        if not target_date:
            target_date = date.today().strftime('%Y-%m-%d')
        
        sales = self.get_sales(target_date)
        
        # Calculate summary
        total_revenue = sum(sale.get('total_amount', 0) for sale in sales)
        items_sold = {}
        
        for sale in sales:
            for item in sale.get('items', []):
                item_name = item.get('name')
                item_quantity = item.get('quantity', 1)
                
                if item_name in items_sold:
                    items_sold[item_name] += item_quantity
                else:
                    items_sold[item_name] = item_quantity
        
        return {
            'date': target_date,
            'total_revenue': total_revenue,
            'items_sold': items_sold,
            'total_transactions': len(sales)
        }
    
    # Inventory Management Functions
    def get_inventory(self):
        """Retrieve inventory data"""
        try:
            with open(self.inventory_file, 'r') as f:
                content = f.read()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, FileNotFoundError):
            self._ensure_file_exists(self.inventory_file)
            return []
    
    def update_inventory(self, item_name, quantity_change, is_addition=True):
        """Update inventory quantity for an item"""
        inventory = self.get_inventory()
        
        # Find the item in inventory
        item_found = False
        for item in inventory:
            if item.get('name') == item_name:
                current_quantity = item.get('quantity', 0)
                
                if is_addition:
                    item['quantity'] = current_quantity + quantity_change
                else:
                    new_quantity = current_quantity - quantity_change
                    item['quantity'] = max(0, new_quantity)  # Prevent negative inventory
                
                item['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                item_found = True
                break
        
        # If item not found, add it to inventory
        if not item_found and is_addition:
            inventory.append({
                'name': item_name,
                'quantity': quantity_change,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        with open(self.inventory_file, 'w') as f:
            f.write(json.dumps(inventory, indent=2))
        
        return True, "Inventory updated successfully."
    
    def _update_inventory_for_new_item(self, item):
        """Initialize inventory for a new menu item"""
        if 'initial_stock' in item:
            self.update_inventory(item['name'], item['initial_stock'], True)
    
    def _update_inventory_from_sale(self, sale_data):
        """Update inventory based on a sale"""
        for item in sale_data.get('items', []):
            item_name = item.get('name')
            quantity = item.get('quantity', 1)
            
            # Decrease inventory
            self.update_inventory(item_name, quantity, False)
    
    # Export functions
    def export_menu_to_excel(self, filepath):
        """Export menu data to Excel"""
        menu_items = self.get_menu_items()
        if not menu_items:
            return False, "No menu items to export"
        
        df = pd.DataFrame(menu_items)
        df.to_excel(filepath, index=False)
        return True, f"Menu exported to {filepath}"
    
    def export_sales_to_excel(self, filepath, date_filter=None):
        """Export sales data to Excel"""
        sales = self.get_sales(date_filter)
        if not sales:
            return False, "No sales data to export"
        
        df = pd.DataFrame(sales)
        df.to_excel(filepath, index=False)
        return True, f"Sales exported to {filepath}"
    
    def export_inventory_to_excel(self, filepath):
        """Export inventory data to Excel"""
        inventory = self.get_inventory()
        if not inventory:
            return False, "No inventory data to export"
        
        df = pd.DataFrame(inventory)
        df.to_excel(filepath, index=False)
        return True, f"Inventory exported to {filepath}"
