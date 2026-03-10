from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, Document, Comment, Proposal, Payment

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
    list_display = ['name', 'client', 'status', 'progress', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'client__username']

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
