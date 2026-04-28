import frappe
import math

@frappe.whitelist()
def create_booking(customer_name, phone, service_category, latitude, longitude):

    booking = frappe.get_doc({
        "doctype": "Service Booking",
        "customer_name": customer_name,
        "phone": phone,
        "latitude": latitude,
        "longitude": longitude,
        "service_category": service_category,
        "status": "Pending"
    })

    booking.insert(ignore_permissions=True)

    # Get provider
    provider = get_provider(latitude, longitude)

    if provider:
        booking.assigned_provider = provider.name
        booking.status = "Assigned"

        distance = calculate_distance(latitude, longitude, provider.latitude, provider.longitude)
        booking.distance = distance

        base_price = frappe.db.get_value("Service Category", service_category, "base_price") or 0
        booking.price = base_price + (distance * 10)

    booking.save()
    frappe.db.commit()

    send_email(booking)

    return booking.name


# Get available providers
@frappe.whitelist()
def get_available_provider():
    return frappe.get_all(
        "Service Provider",
        filters={"is_available": 1},
        fields=["name", "provider_name", "rating", "latitude", "longitude"]
    )


# Provider accepts booking
@frappe.whitelist()
def accept_booking(booking_id, provider):
    booking = frappe.get_doc("Service Booking", booking_id)
    booking.status = "Accepted"
    booking.assigned_provider = provider
    booking.save()

    return "Booking Accepted"


# Get booking status
@frappe.whitelist()
def booking_status(booking_id):
    booking = frappe.get_doc("Service Booking", booking_id)

    return {
        "status": booking.status,
        "provider": booking.assigned_provider,
        "price": booking.price
    }


# Distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5


# Auto assign provider
def get_provider(lat, lon):
    providers = frappe.get_all(
        "Service Provider",
        filters={"is_available": 1},
        fields=["name", "latitude", "longitude", "rating"]
    )

    best = None
    best_score = float("inf")

    for p in providers:
        dist = calculate_distance(lat, lon, p.latitude, p.longitude)
        score = dist - (p.rating or 0)

        if score < best_score:
            best_score = score
            best = p

    return best


# Email notification
def send_email(booking):
    if hasattr(booking, "email") and booking.email:
        frappe.sendmail(
            recipients=[booking.email],
            subject="Booking Created",
            message=f"Your booking {booking.name} has been created"
        )