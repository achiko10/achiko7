from django.test import TestCase, Client
from django.urls import reverse
from .models import Project, Service, Booking, Appointment, FAQ
from unittest.mock import patch
from datetime import date

class PortfolioModelTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(title="Web Dev", description="Dev", icon="layers")
        self.project = Project.objects.create(title="Project 1", slug="project-1", technologies="Django")

    def test_service_creation(self):
        self.assertEqual(str(self.service), "Web Dev")

    def test_project_creation(self):
        self.assertEqual(str(self.project), "Project 1")

    def test_appointment_uniqueness(self):
        # Testing unique_together for date and time_slot
        Appointment.objects.create(name="A", email="a@a.com", date=date(2026,1,1), time_slot="10:00")
        with self.assertRaises(Exception):
            Appointment.objects.create(name="B", email="b@b.com", date=date(2026,1,1), time_slot="10:00")

class PortfolioViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(title="Web Dev", description="Dev", icon="layers")

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_services_view(self):
        response = self.client.get(reverse('services'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    @patch('portfolio.telegram.requests.post')
    def test_book_service_submission(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.client.post(reverse('book_service'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'service': self.service.id,
            'message': 'Hello Test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(name='Test User').exists())
        self.assertTrue(mock_post.called)

    def test_honeypot_blocking(self):
        response = self.client.post(reverse('book_service'), {
            'name': 'Spam Bot',
            'website_url': 'http://spam.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Booking.objects.filter(name='Spam Bot').exists())

    def test_estimate_project_logic(self):
        response = self.client.post(reverse('estimate_service'), {
            'project_type': 'web',
            'has_design': 'no'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Web Application")
