from django import forms
from django.core.exceptions import ValidationError

from .models import TrainerApplication, Booking


class TrainerApplicationForm(forms.ModelForm):
    certificate = forms.FileField(
        label="แนบไฟล์เกียรติบัตร/ผลงาน (ไฟล์เดียว)",
        required=False,
        help_text="รองรับ PDF หรือรูปภาพ 1 ไฟล์"
    )

    class Meta:
        model = TrainerApplication
        fields = ["full_name", "age", "gender", "phone", "email_snapshot", "intro", "portfolio_link"]
        labels = {
            "full_name": "ชื่อ-นามสกุล",
            "age": "อายุ",
            "gender": "เพศ",
            "phone": "เบอร์โทร",
            "email_snapshot": "อีเมล",
            "intro": "แนะนำตัว/เพิ่มเติม",
            "portfolio_link": "ลิงก์ผลงาน (ถ้ามี)",
        }
        widgets = {
            "intro": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = "mt-1 w-full border rounded px-3 py-2"
        for name in ["full_name", "age", "gender", "phone", "email_snapshot", "portfolio_link"]:
            self.fields[name].widget.attrs.update({"class": common})
        self.fields["intro"].widget.attrs.update({"class": common})

        # ไม่บังคับกรอก
        self.fields["intro"].required = False
        self.fields["portfolio_link"].required = False


# ===== Booking =====
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "owner_full_name", "owner_nickname", "owner_phone",
            "dog_name", "dog_count", "dog_gender", "dog_age_year", "dog_breed",
            "round", "message",
        ]
        labels = {
            "owner_full_name": "ชื่อ-นามสกุล (เจ้าของสุนัข)",
            "owner_nickname": "ชื่อเล่น",
            "owner_phone": "เบอร์โทรศัพท์",
            "dog_name": "ชื่อสุนัข",
            "dog_count": "จำนวนสุนัขที่จะฝึก",
            "dog_gender": "เพศ",
            "dog_age_year": "อายุ (ปี)",
            "dog_breed": "สายพันธุ์",
            "round": "เลือกรอบที่ต้องการ",
            "message": "ข้อความถึงครูฝึก (ถ้ามี)",
        }
        widgets = {
            "owner_full_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
            "owner_nickname": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
            "owner_phone": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2",
                "inputmode": "tel",
                "placeholder": "เช่น 08x-xxx-xxxx",
            }),

            "dog_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
            "dog_count": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2",
                "min": 1
            }),
            "dog_gender": forms.Select(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
            "dog_age_year": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2",
                "min": 0
            }),
            "dog_breed": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),

            "round": forms.Select(attrs={
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
            "message": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full rounded-xl border border-slate-300 px-3 py-2"
            }),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        # จำกัด round ให้เลือกเฉพาะของคอร์สนั้น
        if course:
            self.fields["round"].queryset = course.rounds.all()
            if not course.rounds.exists():
                self.fields["round"].widget = forms.HiddenInput()
                self.fields["round"].required = False


class TrainerBookingActionForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["status", "message"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in [Booking.Status.APPROVED, Booking.Status.REJECTED]:
            raise ValidationError("สถานะไม่ถูกต้อง")
        return status
