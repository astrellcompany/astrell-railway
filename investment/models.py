


from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from django.template.loader import render_to_string
from django.conf import settings
from utils.email_utils import send_resend_email  # <-- Resend API


class InvestmentPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField()
    minimum_investment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    maximum_investment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    required_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.name} - {self.interest_rate}% ROI for {self.duration_days} days"

    class Meta:
        verbose_name = "Investment Plan"
        verbose_name_plural = "Investment Plans"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('roi', 'Return on Investment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} by {self.user.username}"

    # ---------------------------
    # USER EMAIL
    # ---------------------------
    def send_user_email(self, subject, template_name, extra_context=None):
        context = {
            "username": self.user.username,
            "amount": self.amount,
            "transaction_id": self.id,
            "transaction_type": self.get_transaction_type_display(),  # FIXED
            "transaction_date": self.created_at.strftime("%Y-%m-%d %H:%M"),  # FIXED
            "status": self.status,
            "dashboard_url": "https://astrellcapitalinvest.com/userprofile/dashboard/",
        }

        if extra_context:
            context.update(extra_context)

        html_content = render_to_string(template_name, context)

        send_resend_email(
            to=self.user.email,
            subject=subject,
            html=html_content
        )

    # ---------------------------
    # ADMIN EMAIL
    # ---------------------------
    def send_admin_email(self, subject, template_name):
        context = {
            "transaction": self,
            "username": self.user.username,
            "amount": self.amount,
            "transaction_id": self.id,
            "transaction_type": self.get_transaction_type_display(),  # ADDED
            "transaction_date": self.created_at.strftime("%Y-%m-%d %H:%M"),  # ADDED
            "status": self.status,
        }

        html_content = render_to_string(template_name, context)

        send_resend_email(
            to=settings.ADMIN_EMAIL,
            subject=subject,
            html=html_content
        )

    # ---------------------------
    # SAVE + EMAIL TRIGGERS
    # ---------------------------
    def save(self, *args, **kwargs):
        send_notification = False
        old_status = None

        if self.pk:
            old = Transaction.objects.get(pk=self.pk)
            old_status = old.status
            if old_status != self.status:
                send_notification = True

        super().save(*args, **kwargs)

        if send_notification:
            if self.status == "approved":
                self.send_user_email(
                    "Transaction Approved",
                    "investment/new_transaction_alert.html"
                )
                self.send_admin_email(
                    "Transaction Approved (Admin Notification)",
                    "investment/transaction_admin_notification.html"
                )

            elif self.status == "rejected":
                self.send_user_email(
                    "Transaction Rejected",
                    "investment/transaction_rejected.html"
                )
                self.send_admin_email(
                    "Transaction Rejected (Admin Notification)",
                    "investment/transaction_admin_notification.html"
                )

    # ---------------------------
    # ACTIONS
    # ---------------------------
    def approve(self):
        if self.status == 'pending':
            self.status = 'approved'
            self.save()

    def reject(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()



class Investment(models.Model):
    user_profile = models.ForeignKey('userprofile.UserProfile', on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    roi_accumulated = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deposit_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(null=True, blank=True)
    required_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Investment of ${self.deposit_amount} by {self.user_profile.user.username}"

    def save(self, *args, **kwargs):
        if self.plan.maximum_investment and self.deposit_amount > self.plan.maximum_investment:
            raise ValueError(f"Deposit amount exceeds the maximum allowed for this plan: {self.plan.maximum_investment}")

        if not self.end_date:
            self.end_date = self.deposit_time + timedelta(days=self.plan.duration_days)
            if isinstance(self.end_date, datetime):
                self.end_date = timezone.make_aware(self.end_date, timezone.get_current_timezone())
            else:
                self.end_date = timezone.make_aware(datetime.combine(self.end_date, datetime.min.time()), timezone.get_current_timezone())

        if self.required_deposit is None:
            self.required_deposit = self.plan.required_deposit or Decimal('0.00')

        super().save(*args, **kwargs)
        self.user_profile.update_balance(self.deposit_amount, 'deposit')
        self.user_profile.calculate_return_of_investment(self.deposit_amount)

    def calculate_roi(self):
        if self.end_date and timezone.now() >= self.end_date:
            self.is_active = False
            self.save()
            return self.roi_accumulated

        time_elapsed = timezone.now() - self.deposit_time
        days_elapsed = time_elapsed.days
        roi_per_day = self.deposit_amount * (self.plan.interest_rate / Decimal('100')) / Decimal('365')
        return roi_per_day * days_elapsed

    def update_roi(self):
        new_roi = self.calculate_roi()
        self.roi_accumulated = new_roi
        self.save()

    def is_expired(self):
        return self.end_date and timezone.now() >= self.end_date


class WithdrawalRequest(models.Model):
    user_profile = models.ForeignKey('userprofile.UserProfile', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def approve(self):
        if self.user_profile.balance >= self.amount:
            self.user_profile.balance -= self.amount
            self.user_profile.withdrawable_amount -= self.amount
            self.user_profile.save()

            Transaction.objects.create(
                user=self.user_profile.user,
                amount=self.amount,
                transaction_type='withdrawal',
                status='approved',
                description="Approved withdrawal"
            )

            user_html = render_to_string("investment/withdrawal_user_approved.html", {
                "username": self.user_profile.user.username,
                "amount": self.amount,
            })

            send_resend_email(
                to=self.user_profile.user.email,
                subject="Withdrawal Approved",
                html=user_html
            )

            admin_html = render_to_string("investment/withdrawal_admin_approved.html", {
                "username": self.user_profile.user.username,
                "amount": self.amount,
                "email": self.user_profile.user.email,
            })

            send_resend_email(
                to=settings.ADMIN_EMAIL,
                subject="Withdrawal Approved (Admin Notification)",
                html=admin_html
            )

            self.approved = True
            self.save()
        else:
            raise ValueError("Insufficient balance to approve this withdrawal")

    def __str__(self):
        return f"Withdrawal request by {self.user_profile.user.username} for ${self.amount}"


class Wallet(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='wallet_icons/', blank=True, null=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Manage Wallets"
