from django import forms
from django.core.exceptions import ValidationError
from .models import TrainerApplication

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

        # ✅ ไม่บังคับกรอก
        self.fields["intro"].required = False
        self.fields["portfolio_link"].required = False
