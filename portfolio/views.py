# ============================================================
# views.py — Zenith Portfolio
# ============================================================

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import escape, strip_tags
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import datetime
import threading

from .models import Project, Service, Booking, FAQ, Appointment, Testimonial
from .forms import BookingForm, AppointmentForm
from .telegram import send_telegram_message
from .utils import render_to_pdf, get_pdf_bytes


# ============================================================
# ჰელფერ ფუნქციები
# ============================================================

def send_html_email(subject, template_name, context, recipient_list):
    """HTML ელ-ფოსტის გაგზავნა ფონურ რეჟიმში."""
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    def _send():
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@zenith.tech')
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
        except Exception as e:
            print(f"[Email Error] {e}")

    threading.Thread(target=_send).start()


def get_estimation_context(project_type, has_design):
    """DRY ფუნქცია — ფასების ლოგიკა ერთ ადგილზე."""
    if project_type == "web":
        service_name = _("Web Application / Portal")
        time = _("3-6 weeks")
        budget = "$1500 - $3500+"
        features = [_("Responsive Design"), _("CMS/Admin Panel"), _("SEO Optimization"), _("Security Checks")]
    elif project_type == "mobile":
        service_name = _("Mobile Application")
        time = _("6-10 weeks")
        budget = "$3000 - $6000+"
        features = [_("Native/Cross-Platform APIs"), _("Push Notifications"), _("App Store Deployment"), _("High Performance")]
    elif project_type == "crm":
        service_name = _("CRM / System Automation")
        time = _("8-14 weeks")
        budget = "$4000 - $10000+"
        features = [_("Custom Dashboards"), _("Third-party Integrations"), _("Data Analytics"), _("Role-based Access")]
    else:
        service_name = _("Custom Solution")
        time = _("To be assessed")
        budget = _("To be determined")
        features = [_("Discovery Phase needed"), _("Architecture Planning")]

    design_note = _("Includes UI/UX creation from scratch.") if has_design == "no" else _("We will use your existing design.")
    if has_design == "no":
        time = _("Additional 1-2 weeks for Design.") + " " + time
        budget = _("+ Design Cost") + " | " + budget

    return {
        "service_name": service_name,
        "time": time,
        "budget": budget,
        "features": features,
        "design_note": design_note,
    }


# ============================================================
# მთავარი Views
# ============================================================

def home(request):
    testimonials = Testimonial.objects.filter(is_active=True)
    return render(request, 'portfolio/home.html', {'testimonials': testimonials})


def services(request):
    services = Service.objects.all()
    return render(request, 'portfolio/services.html', {'services': services})


def projects(request):
    category = request.GET.get('category', '')
    all_projects = Project.objects.all()
    if category:
        all_projects = all_projects.filter(technologies__icontains=category)
    return render(request, 'portfolio/projects.html', {'projects': all_projects, 'active_cat': category})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'portfolio/project_detail.html', {'project': project})


def contact(request):
    services = Service.objects.all()
    faqs = FAQ.objects.all()
    return render(request, 'portfolio/contact.html', {'services': services, 'faqs': faqs})


# ============================================================
# ჯავშნები და Estimator
# ============================================================

def book_service(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('website_url'):  # Honeypot
                return HttpResponse("Spam detected.", status=400)

            booking = form.save()
            serv_title = booking.service.title if booking.service else str(_("General Consultation"))

            # Telegram
            tg_text = (
                f"🔔 <b>{_('New Message from Website')}!</b>\n\n"
                f"👤 <b>{_('Name')}:</b> {escape(booking.name)}\n"
                f"📧 <b>{_('Email')}:</b> {escape(booking.email)}\n"
                f"📱 <b>{_('Phone')}:</b> {escape(booking.phone)}\n"
                f"💼 <b>{_('Service')}:</b> {escape(serv_title)}\n\n"
                f"💬 <b>{_('Message')}:</b>\n<i>{escape(booking.message)}</i>"
            )
            send_telegram_message(tg_text)

            # Email
            send_html_email(
                subject="Zenith - We received your message",
                template_name="emails/booking_confirmation.html",
                context={"name": booking.name, "service": serv_title, "message": booking.message},
                recipient_list=[booking.email]
            )

            return HttpResponse(
                f'<div class="contact-success" style="padding:20px;border:1px solid #25d366;background:#e8f5e9;border-radius:8px;color:#2e7d32;">'
                f'<b>{_("Thank you!")}</b> {_("Your request was successfully sent. We will contact you soon.")}</div>'
            )
        return HttpResponse(f'<div style="color:red;padding:20px;">{form.errors.as_text()}</div>', status=400)
    return HttpResponse("Invalid request", status=400)


def get_available_slots(request):
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponse("")
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("")

    if selected_date < datetime.today().date():
        return HttpResponse(f'<p style="color:var(--text-secondary);">{_("Please select a future date.")}</p>')

    all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    booked = Appointment.objects.filter(
        date=selected_date, status__in=['PENDING', 'CONFIRMED']
    ).values_list('time_slot', flat=True)
    available = [s for s in all_slots if s not in booked]

    if not available:
        return HttpResponse(f'<p style="color:var(--text-secondary);">{_("No available slots on this day.")}</p>')

    html = '<div style="display:flex;gap:8px;flex-wrap:wrap;">'
    for slot in available:
        html += f'''
        <label style="cursor:pointer;display:inline-block;padding:8px 16px;border:1px solid var(--border-color);border-radius:8px;">
            <input type="radio" name="time_slot" value="{slot}" required style="display:none;">
            <span class="slot-text">{slot}</span>
        </label>'''
    html += '</div>'
    html += """<style>
        input[type="radio"]:checked + .slot-text { color: var(--accent-color); font-weight: 600; }
        label:has(input[type="radio"]:checked) { border-color: var(--accent-color); background: var(--bg-secondary); }
    </style>"""
    return HttpResponse(html)


def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('website_url'):  # Honeypot
                return HttpResponse("Spam detected.", status=400)

            date_obj = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']

            if Appointment.objects.filter(date=date_obj, time_slot=time_slot, status__in=['PENDING', 'CONFIRMED']).exists():
                return HttpResponse(
                    f'<div style="padding:20px;border:1px solid #ef4444;background:#fef2f2;border-radius:8px;color:#b91c1c;">'
                    f'{_("This slot is already booked.")}</div>'
                )

            try:
                appt = form.save()
            except IntegrityError:
                return HttpResponse(
                    f'<div style="padding:20px;border:1px solid #ef4444;background:#fef2f2;border-radius:8px;color:#b91c1c;">'
                    f'{_("This slot is already booked.")}</div>'
                )

            # Telegram
            tg_text = (
                f"📅 <b>{_('New Appointment Request')}!</b>\n\n"
                f"👤 <b>{_('Client')}:</b> {escape(appt.name)}\n"
                f"📧 <b>{_('Email')}:</b> {escape(appt.email)}\n"
                f"📱 <b>{_('Phone')}:</b> {escape(appt.phone)}\n"
                f"📆 <b>{_('Date')}:</b> {escape(str(appt.date))}\n"
                f"⏰ <b>{_('Time')}:</b> {escape(appt.time_slot)}\n\n"
                f"<b>{_('Confirm')}:</b>\n/accept_{appt.id} ან /reject_{appt.id}"
            )
            send_telegram_message(tg_text)

            # Email
            send_html_email(
                subject="Zenith - Meeting Request Confirmation",
                template_name="emails/appointment_confirmation.html",
                context={"name": appt.name, "date": str(appt.date), "time": appt.time_slot},
                recipient_list=[appt.email]
            )

            return HttpResponse(
                f'<div class="contact-success" style="padding:20px;border:1px solid #25d366;background:#e8f5e9;border-radius:8px;color:#2e7d32;">'
                f'<b>{_("Request received!")}</b> {_("We will contact you soon for confirmation.")}</div>'
            )
        return HttpResponse(f'<div style="color:red;padding:20px;">{form.errors.as_text()}</div>', status=400)
    return HttpResponse("Invalid request", status=400)


def estimate_service(request):
    if request.method == "POST":
        ctx = get_estimation_context(
            request.POST.get("project_type"),
            request.POST.get("has_design")
        )
        ctx["project_type_val"] = request.POST.get("project_type")
        ctx["has_design_val"] = request.POST.get("has_design")
        return render(request, 'portfolio/estimator_result.html', ctx)
    return HttpResponse("")


def action_pdf_quotation(request):
    if request.method == "POST":
        project_type = request.POST.get("project_type")
        has_design = request.POST.get("has_design")
        email = request.POST.get("email", "")
        action = request.POST.get("action")

        context = get_estimation_context(project_type, has_design)
        context["email"] = email
        context["date"] = timezone.now()

        if action == "download":
            pdf_response = render_to_pdf('emails/quotation_pdf.html', context)
            if pdf_response:
                filename = f"Zenith_Quotation_{timezone.now().strftime('%Y%m%d')}.pdf"
                pdf_response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return pdf_response
            return HttpResponse("Error generating PDF", status=500)

        elif action == "email":
            if not email:
                return HttpResponse('<div style="color:red;font-size:0.9rem;">Email is required</div>', status=400)

            pdf_bytes = get_pdf_bytes('emails/quotation_pdf.html', context)
            if pdf_bytes:
                def _send_pdf():
                    try:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@zenith.tech')
                        msg = EmailMultiAlternatives(
                            subject="Zenith - Your Official Quotation",
                            body="Hello,\n\nPlease find attached the official quotation from Zenith.\n\nBest regards,\nZenith Team",
                            from_email=from_email,
                            to=[email]
                        )
                        msg.attach("Zenith_Quotation.pdf", pdf_bytes, 'application/pdf')
                        msg.send(fail_silently=True)
                    except Exception as e:
                        print(f"[PDF Email Error] {e}")
                threading.Thread(target=_send_pdf).start()
                return HttpResponse(f'<div style="color:#00ff88;font-size:0.9rem;margin-top:10px;">✅ Quotation sent to {email}!</div>')
            return HttpResponse('<div style="color:red;font-size:0.9rem;">Error generating PDF</div>', status=500)

    return HttpResponse("Invalid request", status=400)
