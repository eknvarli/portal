from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDict

from .admin import AnnouncementAdmin, FinanceNotificationAdmin
from .forms import ServiceRequestForm
from .models import Announcement, BankInformation, CustomUser, Document, FinanceNotification, Project, ServiceRequest


class AnnouncementTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			username='musteri',
			password='guclu-sifre-123',
		)

	def test_announcement_requires_title_and_description(self):
		announcement = Announcement(created_by=self.user)

		with self.assertRaises(ValidationError):
			announcement.full_clean()

	def test_authenticated_user_sees_announcements_in_sidebar(self):
		Announcement.objects.create(
			title='Bakim Bildirimi',
			description='Cumartesi günü planlı bakım yapılacaktır.',
			created_by=self.user,
		)
		self.client.force_login(self.user)

		response = self.client.get(reverse('index'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'DUYURULAR')
		self.assertContains(response, 'Bakim Bildirimi')
		self.assertContains(response, self.user.username)

	def test_admin_sets_creator_on_first_save(self):
		admin_user = CustomUser.objects.create_superuser(
			username='admin',
			password='admin-12345',
			email='admin@example.com',
		)
		request = RequestFactory().post('/admin/core/announcement/add/')
		request.user = admin_user
		announcement = Announcement(
			title='Yeni Ozellik',
			description='Portal menusu guncellendi.',
		)

		AnnouncementAdmin(Announcement, AdminSite()).save_model(request, announcement, form=None, change=False)

		self.assertEqual(announcement.created_by, admin_user)


class AuthTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			username='giris-kullanici',
			password='guclu-sifre-123',
			customer_number='CST-1001',
		)

	def test_customer_can_login_only_with_customer_number(self):
		response = self.client.post(reverse('login'), data={'customer_number': 'CST-1001'})

		self.assertRedirects(response, reverse('index'))
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

	def test_unknown_customer_number_shows_error(self):
		response = self.client.post(reverse('login'), data={'customer_number': 'UNKNOWN'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'GECERSIZ_MUSTERI_NUMARASI')


class FinanceTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			username='finans-kullanici',
			password='guclu-sifre-123',
		)
		self.other_user = CustomUser.objects.create_user(
			username='diger-kullanici',
			password='guclu-sifre-123',
		)

	def test_automatic_notification_requires_schedule(self):
		notification = FinanceNotification(
			user=self.user,
			title='Mart Odeme',
			notification_type='payment',
			reason='Aylik hizmet bedeli',
			description='Mart donemi hizmet tahsilati.',
			amount='1500.00',
			due_date=timezone.now().date(),
			delivery_type='automatic',
		)

		with self.assertRaises(ValidationError):
			notification.full_clean()

	def test_finance_page_shows_only_users_notifications_and_bank_info(self):
		BankInformation.objects.create(iban_owner='Turkish Systems', iban='TR000000000000000000000001')
		FinanceNotification.objects.create(
			user=self.user,
			title='Nisan Finans Bildirimi',
			notification_type='finance',
			reason='Masraf bilgilendirmesi',
			description='Ek hizmet kapsamindaki masraf kalemleri.',
			amount='250.00',
			due_date=timezone.now().date(),
			delivery_type='manual',
			sent_at=timezone.now(),
		)
		FinanceNotification.objects.create(
			user=self.other_user,
			title='Gizli Bildirim',
			notification_type='payment',
			reason='Test',
			description='Bu bildirim diger kullaniciya ait.',
			amount='100.00',
			due_date=timezone.now().date(),
			delivery_type='manual',
			sent_at=timezone.now(),
		)

		self.client.force_login(self.user)
		response = self.client.get(reverse('finance_overview'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Turkish Systems')
		self.assertContains(response, 'TR000000000000000000000001')
		self.assertContains(response, 'Nisan Finans Bildirimi')
		self.assertNotContains(response, 'Gizli Bildirim')

	def test_due_automatic_notification_becomes_visible_on_finance_page(self):
		FinanceNotification.objects.create(
			user=self.user,
			title='Planli Odeme Hatirlatmasi',
			notification_type='payment',
			reason='Vadesi gelen odeme',
			description='Bu bildirim planli tarihte otomatik yayinlanmalidir.',
			amount='450.00',
			due_date=timezone.now().date(),
			delivery_type='automatic',
			scheduled_for=timezone.now() - timezone.timedelta(minutes=5),
		)
		self.client.force_login(self.user)

		response = self.client.get(reverse('finance_overview'))
		notification = FinanceNotification.objects.get(title='Planli Odeme Hatirlatmasi')

		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(notification.sent_at)
		self.assertContains(response, 'Planli Odeme Hatirlatmasi')

	def test_admin_sets_manual_notification_as_sent(self):
		admin_user = CustomUser.objects.create_superuser(
			username='finans-admin',
			password='admin-12345',
			email='finans-admin@example.com',
		)
		request = RequestFactory().post('/admin/core/financenotification/add/')
		request.user = admin_user
		notification = FinanceNotification(
			user=self.user,
			title='Elle Gonderilen Bildirim',
			notification_type='finance',
			reason='Manuel kayit',
			description='Admin panelinden olusturulan normal bildirim.',
			amount='300.00',
			due_date=timezone.now().date(),
			delivery_type='manual',
		)

		FinanceNotificationAdmin(FinanceNotification, AdminSite()).save_model(request, notification, form=None, change=False)

		self.assertEqual(notification.created_by, admin_user)
		self.assertIsNotNone(notification.sent_at)


class ServiceRequestTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			username='talep-kullanici',
			password='guclu-sifre-123',
		)

	def test_service_request_form_defaults_to_new_project_without_existing_project(self):
		form = ServiceRequestForm(user=self.user)

		self.assertEqual(form.fields['project_choice'].initial, 'new')

	def test_service_request_form_rejects_invalid_file_extensions(self):
		invalid_file = SimpleUploadedFile('notlar.pdf', b'fake-content', content_type='application/pdf')
		form = ServiceRequestForm(
			data={
				'project_choice': 'new',
				'title': 'Yeni Talep',
				'description': 'Aciklama',
				'budget': '1200.00',
				'urgency': 'medium',
			},
			files=MultiValueDict({'attachments': [invalid_file]}),
			user=self.user,
		)

		self.assertFalse(form.is_valid())
		self.assertIn('attachments', form.errors)

	def test_create_service_request_view_creates_new_project_and_request(self):
		self.client.force_login(self.user)
		image_file = SimpleUploadedFile('ekran.webp', b'fake-image-content', content_type='image/webp')

		response = self.client.post(
			reverse('create_service_request'),
			data={
				'project_choice': 'new',
				'title': 'Mobil Uygulama Talebi',
				'description': 'Yeni mobil uygulama icin teklif talebi.',
				'budget': '3500.00',
				'urgency': 'high',
				'attachments': [image_file],
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('index'))
		service_request = ServiceRequest.objects.get(title='Mobil Uygulama Talebi')
		self.assertEqual(service_request.requester, self.user)
		self.assertEqual(service_request.project.client, self.user)
		self.assertEqual(service_request.project.status, 'Talep Alindi')
		self.assertEqual(service_request.attachments.count(), 1)


class ProjectDashboardTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			username='proje-kullanici',
			password='guclu-sifre-123',
		)
		self.project_one = Project.objects.create(
			name='Portal Yenileme',
			client=self.user,
			client_label='Acme',
			summary='Kurumsal panel iyilestirme projesi.',
			technology_stack='Django, Alpine.js',
			status='In Progress',
			progress=45,
		)
		self.project_two = Project.objects.create(
			name='Mobil Uygulama',
			client=self.user,
			status='Planning',
			progress=10,
		)
		Document.objects.create(project=self.project_one, name='Teknik Dokuman', file='project_docs/test.pdf')

	def test_dashboard_allows_switching_between_projects(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('index'), {'project': self.project_one.id})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Portal Yenileme')
		self.assertContains(response, 'Acme')
		self.assertContains(response, 'Django, Alpine.js')

	def test_file_center_filters_documents_by_project(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('file_center'), {'project': self.project_one.id})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Teknik Dokuman')
