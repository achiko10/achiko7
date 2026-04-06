from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Project, Service, Booking, FAQ, Appointment
from django.utils.translation import gettext as _
from .telegram import send_telegram_message
from django.utils.html import escape
from datetime import datetime, timedelta

def home(request):
    return render(request, 'portfolio/home.html')

def services(request):
    services = Service.objects.all()
    return render(request, 'portfolio/services.html', {'services': services})

def projects(request):
    projects = Project.objects.all()
    return render(request, 'portfolio/projects.html', {'projects': projects})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'portfolio/project_detail.html', {'project': project})

def contact(request):
    services = Service.objects.all()
    faqs = FAQ.objects.all()
    return render(request, 'portfolio/contact.html', {'services': services, 'faqs': faqs})

def book_service(request):
    if request.method == "POST":
        honeypot = request.POST.get('website_url')
        if honeypot:
            return HttpResponse("Mmm, feels like spam...", status=400)
            
        name = request.POST.get('name')

        email = request.POST.get('email')
        service_id = request.POST.get('service')
        message = request.POST.get('message')
        
        service = Service.objects.get(id=service_id) if service_id else None
        
        booking = Booking.objects.create(
            name=name,
            email=email,
            service=service,
            message=message
        )
        
        # Send Telegram Notification
        safename = escape(name)
        safeemail = escape(email)
        safemsg = escape(message)
        safeserv = escape(service.title if service else _("General Consultation"))
        
        tg_text = (
            f"🔔 <b>{_('New Message from Website')}!</b>\n\n"
            f"👤 <b>{_('Name')}:</b> {safename}\n"
            f"📧 <b>{_('Email')}:</b> {safeemail}\n"
            f"💼 <b>{_('Service')}:</b> {safeserv}\n\n"
            f"💬 <b>{_('Message')}:</b>\n<i>{safemsg}</i>"
        )
        send_telegram_message(tg_text)
        
        return HttpResponse(f'<div class="contact-success" style="padding: 20px; border: 1px solid #25d366; background: #e8f5e9; border-radius: 8px; color: #2e7d32;"><b>{_("Thank you!")}</b> {_("Your request was successfully sent. We will contact you soon.")}</div>')
    
    return HttpResponse("Invalid request", status=400)

def get_available_slots(request):
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponse("")
        
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("")
        
    # Ignore past dates
    if selected_date < datetime.today().date():
        return HttpResponse(f'<p style="color:var(--text-secondary);">{_("Please select a future date.")}</p>')

    all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    booked = Appointment.objects.filter(
        date=selected_date, 
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('time_slot', flat=True)
    
    available = [s for s in all_slots if s not in booked]
    
    if not available:
        return HttpResponse(f'<p style="color:var(--text-secondary);">{_("No available slots on this day.")}</p>')
        
    html = '<div style="display: flex; gap: 8px; flex-wrap: wrap;">'
    for slot in available:
        html += f"""
        <label style="cursor:pointer; display:inline-block; padding:8px 16px; border:1px solid var(--border-color); border-radius:8px;">
            <input type="radio" name="time_slot" value="{slot}" required style="display:none;">
            <span class="slot-text">{slot}</span>
        </label>
        """
    html += '</div>'
    
    # CSS to highlight selected
    html += """
    <style>
        input[type="radio"]:checked + .slot-text { color: var(--accent-color); font-weight: 600; }
        label:has(input[type="radio"]:checked) { border-color: var(--accent-color); background: var(--bg-secondary); }
    </style>
    """
    return HttpResponse(html)

def book_appointment(request):
    if request.method == "POST":
        honeypot = request.POST.get('website_url')
        if honeypot:
            return HttpResponse("Mmm, feels like spam...", status=400)
            
        name = request.POST.get("name")
        email = request.POST.get("email")
        date_str = request.POST.get("date")
        time_slot = request.POST.get("time_slot")
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse("Invalid Date", status=400)
            
        # Check if already booked
        exists = Appointment.objects.filter(date=date_obj, time_slot=time_slot, status__in=['PENDING', 'CONFIRMED']).exists()
        if exists:
            return HttpResponse(f'<div class="contact-success" style="padding: 20px; border: 1px solid #ef4444; background: #fef2f2; border-radius: 8px; color: #b91c1c;">{_("This slot is already booked.")}</div>')
        
        appt = Appointment.objects.create(name=name, email=email, date=date_obj, time_slot=time_slot)
        
        # Send Telegram Msg
        safename = escape(name)
        safeemail = escape(email)
        safedate = escape(str(date_obj))
        safetime = escape(time_slot)
        
        tg_text = (
            f"📅 <b>{_('New Appointment Request')}!</b>\n\n"
            f"👤 <b>{_('Client')}:</b> {safename}\n"
            f"📧 <b>{_('Email')}:</b> {safeemail}\n"
            f"📆 <b>{_('Date')}:</b> {safedate}\n"
            f"⏰ <b>{_('Time')}:</b> {safetime}\n\n"
            f"<b>{_('Confirm')}:</b>\n/accept_{appt.id} ან /reject_{appt.id}"
        )
        send_telegram_message(tg_text)
        
        return HttpResponse(f'<div class="contact-success" style="padding: 20px; border: 1px solid #25d366; background: #e8f5e9; border-radius: 8px; color: #2e7d32;"><b>{_("Request received!")}</b> {_("We will contact you soon for confirmation.")}</div>')
        
    return HttpResponse("Invalid request", status=400)

def estimate_service(request):
    if request.method == "POST":
        project_type = request.POST.get("project_type")
        has_design = request.POST.get("has_design")
        
        # Simple logic for estimation
        if project_type == "web":
            service_name = _("Web Application / Website")
            time = "3-6 " + _("weeks")
            budget = "High-end"
        elif project_type == "mobile":
            service_name = _("Mobile Application")
            time = "4-8 " + _("weeks")
            budget = "Premium"
        elif project_type == "crm":
            service_name = _("CRM / Business Automation")
            time = "6-12 " + _("weeks")
            budget = "Enterprise"
        else:
            service_name = _("Custom Solution")
            time = _("After assessment")
            budget = _("Depends on requirements")
            
        context = {
            "service_name": service_name,
            "time": time,
            "budget": budget,
            "design_note": _("I will work on the design from scratch.") if has_design == "no" else ""
        }
        return render(request, 'portfolio/estimator_result.html', context)
    return HttpResponse("")
