from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import Profile  # ใช้ Profile.Role สำหรับ role TRAINER


def certificate_upload_path(instance, filename):
    return f'trainer_certs/app_{instance.application.id}/{filename}'


#  Trainer Application : ส่งคำขอเป็นผู้ฝึก
class TrainerApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "รอดำเนินการ"
        APPROVED = "approved", "อนุมัติ"
        REJECTED = "rejected", "ปฏิเสธ"

    GENDER_CHOICES = [
        ("male", "ชาย"),
        ("female", "หญิง"),
        ("other", "อื่น ๆ"),
        ("prefer_not", "ไม่ระบุ"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_apps"
    )
    full_name = models.CharField(max_length=120, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email_snapshot = models.EmailField(blank=True, help_text="อีเมล ณ เวลายื่นคำร้อง")
    intro = models.TextField(blank=True, null=True, help_text="แนะนำตัว/ประสบการณ์/เพิ่มเติมที่อยากเขียน")
    portfolio_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="trainer_apps_reviewed"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TrainerApplication({self.user.username}, {self.status})"


class TrainerCertificate(models.Model):
    application = models.ForeignKey(
        TrainerApplication,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    file = models.FileField(upload_to=certificate_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate(app={self.application.id})"


@receiver(post_save, sender=TrainerApplication)
def promote_user_on_approval(sender, instance: TrainerApplication, **kwargs):
    """อนุมัติคำร้อง -> อัพเดท role เป็น TRAINER อัตโนมัติ"""
    if instance.status == TrainerApplication.Status.APPROVED:
        profile = getattr(instance.user, "profile", None)
        if profile and profile.role != Profile.Role.TRAINER:
            profile.role = Profile.Role.TRAINER
            profile.save(update_fields=["role"])



# ===== ระบบจองคอร์ส =====
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "รอดำเนินการ"
        APPROVED = "approved", "อนุมัติ"
        REJECTED = "rejected", "ปฏิเสธ"
        CANCELED = "canceled", "ยกเลิกโดยผู้ใช้"

    class DogGender(models.TextChoices):
        MALE = "male", "ผู้"
        FEMALE = "female", "เมีย"
        # OTHER = "other", "อื่น ๆ"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    # อ้างอิง Course / CourseRound จาก app course
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    round = models.ForeignKey(
        "course.CourseRound",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings"
    )

    owner_full_name = models.CharField(max_length=120, default="")
    owner_nickname = models.CharField(max_length=80, blank=True, default="")
    owner_phone = models.CharField(max_length=20, default="")

    dog_name = models.CharField(max_length=100, blank=True, default="")
    dog_count = models.PositiveIntegerField(default=1)
    dog_gender = models.CharField(
        max_length=10,
        choices=DogGender.choices,
        blank=True,
        default=""
    )
    dog_age_year = models.PositiveIntegerField(default=0)
    dog_breed = models.CharField(max_length=120, blank=True, default="")

    message = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking({self.user_id} -> {self.course_id} / {self.status})"
