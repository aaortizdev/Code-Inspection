"""Order processing logic."""
import database
import auth

TAX = 0.15
INVOICE_SEPARATOR = "==================================="

def calculate_coupon_discount(total, coupon, token):
    if coupon == "WELCOME10":
        return total * 0.9
    elif coupon == "BLACKFRIDAY":
        return total * 0.5
    elif coupon == "STAFF":
        return total * 0.7 
    return total

def calculate_shipping_cost(shipping):
    if shipping == "express":
        return 10
    elif shipping == "standard":
        return 3
    return 0

def process_order(token, items, coupon=None, shipping="standard", log=None):
    if log is None:
        log = []
        
    username = auth.sessions.get(token)
    if username is None:
        return None

    if not items:
        print("Empty order")
        return None

    total = 0
    for item in items:
        book = database.get_book(item["book_id"])
        if book and book[3] >= item["qty"]:
            total += book[2] * item["qty"]

    total = calculate_coupon_discount(total, coupon, token)
    total += calculate_shipping_cost(shipping)
    total += total * TAX

    order_id = len(log) + 1
    log.append({"order_id": order_id, "username": username, "total": total})
    return total

def _print_document_details(title, username, items):
    """Función auxiliar para reutilizar la lógica compartida entre facturas y cotizaciones."""
    print(INVOICE_SEPARATOR)
    print(title)
    print("Customer: " + username)
    print(INVOICE_SEPARATOR)
    
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal += line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
        
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    return subtotal

def print_invoice(username, items):
    _print_document_details("BOOKSTORE INVOICE", username, items)
    print(INVOICE_SEPARATOR)

def print_quote(username, items):
    _print_document_details("BOOKSTORE QUOTE", username, items)
    print("This quote is valid for 7 days.")
    print(INVOICE_SEPARATOR)

def cancel_order(order_id):
    try:
        conn = database.get_connection()
        conn.execute("UPDATE orders SET status = 'CANCELLED' WHERE id = ?", (order_id,))
        conn.commit()
    except Exception:
        pass