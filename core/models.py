from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    customer_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.customer_number})" if self.customer_number else self.username

class Project(models.Model):
    name = models.CharField(max_length=200)
    client_label = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    technology_stack = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default='Active')
    progress = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def display_client_label(self):
        return self.client_label or self.client.username

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='project_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Proposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    content = models.TextField()
    status = models.CharField(max_length=20, default='Pending') # Pending, Approved
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Proposal for {self.project.name}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.project.name} - {self.amount} - {self.status}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BankInformation(models.Model):
    iban_owner = models.CharField(max_length=200)
    iban = models.CharField(max_length=34)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Banka Bilgisi'
        verbose_name_plural = 'Banka Bilgileri'

    def __str__(self):
        return self.iban_owner


class FinanceNotification(models.Model):
    TYPE_CHOICES = [
        ('payment', 'Odeme'),
        ('finance', 'Finans'),
    ]
    DELIVERY_CHOICES = [
        ('manual', 'Normal'),
        ('automatic', 'Otomatik'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='finance_notifications')
    title = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='manual')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_finance_notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at', '-created_at']
        verbose_name = 'Finans Bildirimi'
        verbose_name_plural = 'Finans Bildirimleri'

    def clean(self):
        errors = {}

        if self.delivery_type == 'automatic' and not self.scheduled_for:
            errors['scheduled_for'] = 'Otomatik bildirimler icin gonderim tarihi zorunludur.'

        if self.delivery_type == 'manual' and self.scheduled_for:
            errors['scheduled_for'] = 'Normal bildirimlerde planli gonderim tarihi kullanilmaz.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.title} - {self.user.username}'


class ServiceRequest(models.Model):
    URGENCY_CHOICES = [
        ('question', 'Soru'),
        ('low', 'Dusuk'),
        ('medium', 'Orta'),
        ('high', 'Yuksek'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='service_requests')
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Talep'
        verbose_name_plural = 'Talepler'

    def __str__(self):
        return self.title


class ServiceRequestAttachment(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='service_request_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Talep Dosyasi'
        verbose_name_plural = 'Talep Dosyalari'

    def __str__(self):
        return self.file.name.rsplit('/', 1)[-1]
