
from decimal import Decimal

from .models import Item


def check_stock(name):
    """Look up how many units of an item are in stock."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    return {
        "name": item.name,
        "quantity": item.quantity,
    }


def list_items():
    """Return every item in the inventory."""
    items = Item.objects.all()

    return {
        "items": [
            {
                "name": item.name,
                "quantity": item.quantity,
                "price": str(item.price),
            }
            for item in items
        ]
    }


def add_item(name, quantity):
    """Create an item or add stock to an existing item."""
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0."}

    item = Item.objects.filter(name__iexact=name).first()

    if item is not None:
        item.quantity += quantity
        item.save()

        return {
            "name": item.name,
            "quantity": item.quantity,
            "created": False,
        }

    item = Item.objects.create(name=name, quantity=quantity)

    return {
        "name": item.name,
        "quantity": item.quantity,
        "created": True,
    }


def remove_stock(name, quantity):
    """Remove a quantity from an existing item."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0."}

    if quantity > item.quantity:
        return {
            "error": f"Cannot remove {quantity} units. Only {item.quantity} are in stock.",
            "name": item.name,
            "quantity": item.quantity,
        }

    item.quantity -= quantity
    item.save()

    return {
        "name": item.name,
        "quantity": item.quantity,
    }


def delete_item(name):
    """Permanently delete an item from the inventory."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    deleted_name = item.name
    item.delete()

    return {"deleted": deleted_name}


def calculate_cost(name, quantity, vat_percent=10):
    """Calculate the total cost of an item, including VAT."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0."}

    if vat_percent < 0:
        return {"error": "VAT percentage cannot be negative."}

    unit_price = item.price
    subtotal = unit_price * Decimal(quantity)
    vat_rate = Decimal(str(vat_percent)) / Decimal("100")
    vat = subtotal * vat_rate
    total = subtotal + vat

    return {
        "name": item.name,
        "quantity": quantity,
        "unit_price": str(unit_price),
        "subtotal": str(subtotal),
        "vat_percent": vat_percent,
        "vat": str(vat),
        "total": str(total),
    }


def increase_price(name, percentage=50):
    """Increase an item's stored price by a specified percentage."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {
            "error": f"No item named '{name}' exists in the inventory."
        }

    if percentage <= 0:
        return {
            "error": "The percentage must be greater than 0."
        }

    old_price = item.price
    increase = old_price * Decimal(str(percentage)) / Decimal("100")
    new_price = old_price + increase

    item.price = new_price
    item.save()

    return {
        "name": item.name,
        "old_price": str(old_price),
        "increase_percent": percentage,
        "increase_amount": str(increase),
        "new_price": str(new_price),
    }


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "check_stock",
        "description": (
            "Look up the current quantity of an inventory item. "
            "Use this when the user asks how many units are in stock."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the inventory item.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "list_items",
        "description": (
            "List all inventory items, including their quantities and prices. "
            "Use this when the user asks what items are in the inventory."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "type": "function",
        "name": "add_item",
        "description": (
            "Add stock to an inventory item. If the item does not exist, "
            "create it. New items have a default unit price of zero until set."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "The positive number of units to add.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "remove_stock",
        "description": (
            "Remove a quantity from an existing inventory item without "
            "deleting the item itself."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "The positive number of units to remove.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "delete_item",
        "description": (
            "Permanently delete an inventory item and its record. "
            "Use only when the user clearly requests deletion."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item to delete.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "calculate_cost",
        "description": (
            "Calculate the cost of a specified quantity of an inventory item, "
            "including VAT. Always use this tool for inventory cost or price "
            "questions. Use the stored unit price; never invent a price."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the inventory item.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "The number of units to calculate the cost for.",
                },
                "vat_percent": {
                    "type": "number",
                    "description": "The VAT percentage, such as 10 for 10% VAT.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    
    {
        "type": "function",
        "name": "increase_price",
        "description": (
            "Increase the stored price of an existing inventory item by a "
            "specified percentage. Use this whenever the user asks to raise "
            "or increase an item's price. Report the old and new prices."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the inventory item.",
                },
                "percentage": {
                    "type": "number",
                    "description": "The percentage increase, such as 50 for 50%.",
                },
            },
            "required": ["name", "percentage"],
        },
    },

]


TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "list_items": list_items,
    "add_item": add_item,
    "remove_stock": remove_stock,
    "delete_item": delete_item,
    "calculate_cost": calculate_cost,
    "increase_price": increase_price,
}
