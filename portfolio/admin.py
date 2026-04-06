from django.contrib import admin
from .models import Project, Service, Booking, FAQ, Appointment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "technologies", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description", "technologies")

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)
    search_fields = ("title", "description")

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at")
    list_filter = ("service", "created_at")
    search_fields = ("name", "email", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date", "time_slot", "status")
    list_filter = ("status", "date")
    search_fields = ("name", "email", "date")
    date_hierarchy = "date"
    list_editable = ("status",)
