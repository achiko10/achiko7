from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

class Project(models.Model):
    title = models.CharField(_("სათაური"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, null=True, blank=True)
    description = RichTextField(_("Description"))
    problem = RichTextField(_("Problem"), blank=True, null=True)
    solution = RichTextField(_("Solution"), blank=True, null=True)
    result = RichTextField(_("Result"), blank=True, null=True)
    technologies = models.CharField(_("Technologies"), max_length=300)
    link = models.URLField(_("Link"), blank=True, null=True)
    image = models.ImageField(_("Image"), upload_to="projects/", blank=True, null=True)
    order = models.IntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["order"]

    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(_("სათაური"), max_length=200)
    description = RichTextField(_("აღწერა"))
    icon = models.CharField(_("Icon"), max_length=100, help_text="Lucide icon name or SVG path")
    order = models.IntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["order"]

    def __str__(self):
        return self.title

class Booking(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, verbose_name=_("Service"))
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __str__(self):
        return f"{self.name} - {self.service.title if self.service else 'General'}"

class FAQ(models.Model):
    question = models.CharField(_("კითხვა"), max_length=255)
    question_en = models.CharField(_("Question (EN)"), max_length=255, blank=True, null=True)
    answer = RichTextField(_("პასუხი"))
    answer_en = RichTextField(_("Answer (EN)"), blank=True, null=True)
    order = models.IntegerField(_("რიგითობა"), default=0)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ["order"]

    def __str__(self):
        return self.question

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    ]
    
    name = models.CharField(_("Client Name"), max_length=100)
    email = models.EmailField(_("ელ-ფოსტა"))
    phone = models.CharField(_("Phone"), max_length=20, default="")
    date = models.DateField(_("Date"))
    time_slot = models.CharField(_("Time"), max_length=20) # e.g. "10:00", "11:00"
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'time_slot')
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f"{self.name} - {self.date} @ {self.time_slot} ({self.status})"


class Testimonial(models.Model):
    """კლიენტების შეფასებები (Social Proof სექციისთვის)"""
    client_name = models.CharField(_("კლიენტის სახელი"), max_length=100)
    position = models.CharField(_("პოზიცია / თანამდებობა"), max_length=100, blank=True)
    company = models.CharField(_("კომპანია"), max_length=100, blank=True)
    text = models.TextField(_("გამოხმაურება"))
    avatar = models.ImageField(_("ფოტო"), upload_to="testimonials/", blank=True, null=True)
    is_active = models.BooleanField(_("გამოჩნდეს საიტზე"), default=True)
    order = models.IntegerField(_("რიგითობა"), default=0)

    class Meta:
        verbose_name = _("შეფასება")
        verbose_name_plural = _("შეფასებები (Testimonials)")
        ordering = ["order"]

    def __str__(self):
        return f"{self.client_name} — {self.company}"
