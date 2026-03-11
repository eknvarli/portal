from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import Announcement, BankInformation, CustomUser, FinanceNotification, Project, Document, Comment, Proposal, Payment, ServiceRequest, ServiceRequestAttachment

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    readonly_fields = ('uploaded_at',)


class ProposalInline(admin.TabularInline):
    model = Proposal
    extra = 0
    readonly_fields = ('approved_at',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class ServiceRequestInline(admin.TabularInline):
    model = ServiceRequest
    extra = 0
    readonly_fields = ('requester', 'created_at')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('customer_number', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Bilgiler', {'fields': ('customer_number', 'phone')}),
    )
    list_display = ['username', 'customer_number', 'is_staff']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'progress', 'start_date', 'target_date', 'updated_at']
    list_filter = ['status']
    search_fields = ['name', 'client__username']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Proje Kimligi', {'fields': ('name', 'client', 'client_label', 'status', 'progress')}),
        ('Planlama', {'fields': ('summary', 'technology_stack', 'start_date', 'target_date')}),
        ('Zaman Bilgisi', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [DocumentInline, ProposalInline, PaymentInline, ServiceRequestInline]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'uploaded_at')
    list_filter = ('project',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'timestamp')

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'approved_at')
    list_filter = ('status',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_by', 'created_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BankInformation)
class BankInformationAdmin(admin.ModelAdmin):
    list_display = ('iban_owner', 'iban', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        if BankInformation.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(FinanceNotification)
class FinanceNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'delivery_type', 'amount', 'due_date', 'sent_at')
    list_filter = ('notification_type', 'delivery_type', 'due_date')
    search_fields = ('title', 'reason', 'description', 'user__username')
    readonly_fields = ('created_by', 'created_at', 'sent_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if obj.delivery_type == 'manual' and not obj.sent_at:
            obj.sent_at = timezone.now()
        super().save_model(request, obj, form, change)


class ServiceRequestAttachmentInline(admin.TabularInline):
    model = ServiceRequestAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'project', 'budget', 'urgency', 'created_at')
    list_filter = ('urgency', 'created_at')
    search_fields = ('title', 'description', 'requester__username', 'project__name')
    readonly_fields = ('requester', 'created_at')
    inlines = [ServiceRequestAttachmentInline]


@admin.register(ServiceRequestAttachment)
class ServiceRequestAttachmentAdmin(admin.ModelAdmin):
    list_display = ('service_request', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
