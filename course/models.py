from django.db import models
from django.conf import settings


THAI_DAYS = {
    0: "จันทร์", 1: "อังคาร", 2: "พุธ", 3: "พฤหัสบดี",
    4: "ศุกร์", 5: "เสาร์", 6: "อาทิตย์",
}

def course_cover_upload_path(instance, filename):
    return f"courses/{instance.trainer_id}/{filename}"

class Course(models.Model):
    class Day(models.IntegerChoices):
        MON = 0, "จันทร์"
        TUE = 1, "อังคาร"
        WED = 2, "พุธ"
        THU = 3, "พฤหัสบดี"
        FRI = 4, "ศุกร์"
        SAT = 5, "เสาร์"
        SUN = 6, "อาทิตย์"

    trainer       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    title         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    duration_hr   = models.PositiveIntegerField(default=1, help_text="จำนวนชั่วโมงรวม (เป็นจำนวนเต็ม)")
    price         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="ราคามัดจำ")
    cover_image   = models.ImageField(upload_to=course_cover_upload_path, null=True, blank=True)
    location      = models.CharField(max_length=255, blank=True)
    training_days = models.JSONField(default=list, blank=True, help_text="ลิสต์วันในสัปดาห์")
    start_time    = models.TimeField(null=True, blank=True)
    end_time      = models.TimeField(null=True, blank=True)
    max_dogs      = models.PositiveIntegerField(null=True, blank=True)
    benefits      = models.TextField(blank=True, help_text="รายการสิ่งที่จะได้รับ")
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    is_published  = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_published", "created_at"])]

    def __str__(self):
        return f"{self.title} by {self.trainer.username}"

    @property
    def benefits_list(self):
        items = []
        for raw in (self.benefits or "").splitlines():
            item = raw.strip()
            if not item:
                continue
            while item and (item[0].isdigit() or item[0] in "-*)•."):
                item = item[1:].strip()
            items.append(item)
        return items

    def display_training_days(self):
        vals = self.training_days or []
        days_sorted = sorted(int(d) for d in vals)
        return ", ".join(THAI_DAYS.get(d, str(d)) for d in days_sorted)

class CourseRound(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="rounds")
    days       = models.JSONField(default=list, blank=True)  # list[int]
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return f"{self.display_days()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

    def display_days(self):
        lst = sorted([int(d) for d in (self.days or [])])
        return ", ".join(THAI_DAYS.get(d, str(d)) for d in lst)
