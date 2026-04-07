from django.urls import path
from .views import home, services, projects, contact, book_service, project_detail, estimate_service, get_available_slots, book_appointment, action_pdf_quotation

urlpatterns = [
    path('', home, name='home'),
    path('services/', services, name='services'),
    path('projects/', projects, name='projects'),
    path('projects/<slug:slug>/', project_detail, name='project_detail'),
    path('contact/', contact, name='contact'),
    path('book/', book_service, name='book_service'),
    path('estimate/', estimate_service, name='estimate_service'),
    path('api/slots/', get_available_slots, name='get_available_slots'),
    path('api/book-appointment/', book_appointment, name='book_appointment'),
    path('estimate/pdf/', action_pdf_quotation, name='action_pdf_quotation'),
]
