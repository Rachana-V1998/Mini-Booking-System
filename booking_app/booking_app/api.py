import frappe
import math
# create booking

@frappe.whitelist()   
def craete_booking(section_break_gk6z,phone,service_category,latitude,longitude):
    booking = frappe.get_doc
    ({
        "doctype" : "Service Booking"
        "Customer Name" : section_break_gk6z,
        " phone" : phone,
        "latitude" : latitude,
        "longitude" : longitude,
        "service_category" : service_category,
        "status" : "Pending"
    })
    booking.insert (ignore_permission = True)

    provider =get_provider(latitude, longitude)
    if provider:
       booking.assigned_provider = provider.name
       booking.status = "Assigned"
    distance = calculate_distance(latitude, longitude,provider.latitude, provider.longitude)    
    booking.distance=distance
    category=frappe.get_doc("Service Category", service_category)   
    booking.price = category.base_price * distance
    booking.save()
    frappe.db.commit()
    send_email(booking)
    return booking.name



# get providers by location
@frappe.whitelist()
def get_available_provide():
    return frappe.get_all("Service Provider",
        filter= {"is_available" : 1},
        fields=["name","Provider Name","rating","latitude","longitude"]
 )

# provider accepts
@frappe.whitelist()
def accept_booking(booking_id,provider):
    booking=frappe.get_doc("Service Booking",booking_id)
    booking.status="Accepted"
    booking.section_break_tmgl = provider
    booking.save()
    
    return "Booking Accepted"


# get booking details
@frappe.whitelist()
def booking_status(booking_id):
    booking = frappe.get_doc("Service Booking",booking_id)
    return{
        "status": booking.status,
        "provider" : booking.section_break_tmgl,
        "price" : booking.price
    }


# calculation
def calculate_distance(lat1,lon1,lat2,lon2):
    return((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5



# - Auto-assign provider based on distance & rating
def get_provider(lat,lon):
    providers = frappe.get_all("Service Provider",
            filter={"is_available":1},
            fields = ["name","latitude","longitude","rating"]
  )
    best = None
    best_score = 9999
    for p in providers:
        dist = calculate_distance(lat,lon,p.latitude,p.longitude)
        score = dist - (p.rating or 0)
        if score < best_score:
            best_score = score
            best = p
    return best    



# Notification
def send_email(booking):
    frappe.sendmail(
        recipients =[booking.email] if hasattr (booking,"email") 
        else[],
        subject = "booking created",
        message = f"your booking{booking.section_break_gk6z} is created"
    )


# Calculate price based on distance
category = frappe.get_doc( "Service Category", service_category)
price = category.base_price +(distance *10)
booking.price = price