from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Project, Service, Booking, FAQ, Appointment, Testimonial

# ======================================================
# Admin Panel კონფიგურაცია — Zenith Portfolio
# ======================================================

admin.site.site_header = "Zenith ადმინ პანელი"
admin.site.site_title = "Zenith"
admin.site.index_title = "მართვის პანელი"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "technologies_preview", "has_image", "order", "live_link")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description", "technologies")
    list_per_page = 15
    fieldsets = (
        (_("ძირითადი ინფო"), {
            "fields": ("title", "slug", "technologies", "image", "link", "order")
        }),
        (_("კეის სტადი"), {
            "fields": ("description", "problem", "solution", "result"),
            "classes": ("collapse",),
        }),
    )

    def technologies_preview(self, obj):
        techs = obj.technologies.split()[:3]
        badges = " ".join(
            f'<span style="background:#222;color:#0f0;padding:2px 6px;border-radius:4px;font-size:11px;">{t}</span>'
            for t in techs
        )
        return format_html(badges)
    technologies_preview.short_description = _("ტექნოლოგიები")
    technologies_preview.allow_tags = True

    def has_image(self, obj):
        return format_html('<span style="color:green;">✔</span>') if obj.image else format_html('<span style="color:red;">✘</span>')
    has_image.short_description = _("სურათი")

    def live_link(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">🔗 გახსენი</a>', obj.link)
        return "—"
    live_link.short_description = _("ლინკი")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)
    search_fields = ("title", "description")
    list_per_page = 20


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)
    search_fields = ("question", "answer")
    list_per_page = 20


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "service", "created_at")
    list_filter = ("service", "created_at")
    search_fields = ("name", "email", "message", "phone")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    list_per_page = 20
    ordering = ("-created_at",)
    fieldsets = (
        (_("კლიენტის ინფო"), {
            "fields": ("name", "email", "phone", "service")
        }),
        (_("შეტყობინება"), {
            "fields": ("message",)
        }),
        (_("სისტემური"), {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "date", "time_slot", "status", "status_badge", "created_at")
    list_filter = ("status", "date")
    search_fields = ("name", "email", "phone")
    date_hierarchy = "date"
    list_editable = ("status",)
    ordering = ("date", "time_slot")
    readonly_fields = ("created_at",)
    list_per_page = 20
    actions = ["mark_confirmed", "mark_rejected"]

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'CONFIRMED': '#22c55e',
            'REJECTED': '#ef4444',
        }
        labels = {
            'PENDING': '⏳ Pending',
            'CONFIRMED': '✅ Confirmed',
            'REJECTED': '❌ Rejected',
        }
        color = colors.get(obj.status, '#888')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            color, label
        )
    status_badge.short_description = _("სტატუსი")

    @admin.action(description=_("დადასტურება — Confirmed"))
    def mark_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, _("შერჩეული ჯავშნები დადასტურებულია."))

    @admin.action(description=_("უარყოფა — Rejected"))
    def mark_rejected(self, request, queryset):
        queryset.update(status='REJECTED')
        self.message_user(request, _("შერჩეული ჯავშნები უარყოფილია."))


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "position", "company", "is_active", "order")
    list_editable = ("is_active", "order")
    search_fields = ("client_name", "company", "text")
    list_per_page = 20
    fieldsets = (
        (_("კლიენტი"), {
            "fields": ("client_name", "position", "company", "avatar")
        }),
        (_("გამოხმაურება"), {
            "fields": ("text",)
        }),
        (_("პარამეტრები"), {
            "fields": ("is_active", "order")
        }),
    )
