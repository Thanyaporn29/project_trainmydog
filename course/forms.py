from django import forms
from django.forms import inlineformset_factory
from .models import Course, CourseRound

class CourseForm(forms.ModelForm): 
    class Meta:
        model = Course
        fields = [
            "cover_image", "title", "duration_hr", "max_dogs",
            "description", "price", "deposit_price", "location",
            "benefits", "is_published",
        ]
        labels = {
            "cover_image": "รูปภาพคอร์สของคุณ",
            "title": "ชื่อคอร์ส",
            "duration_hr": "ระยะเวลาฝึก (ชั่วโมงรวม)",
            "max_dogs": "จำนวนสุนัขที่รับฝึก",
            "description": "เกี่ยวกับคอร์ส",
            "price": "ราคาคอร์ส",
            "deposit_price": "ราคามัดจำคอร์ส",
            "location": "สถานที่",
            "benefits": "สิ่งที่สุนัขจะได้รับในระหว่างฝึก",
            "is_published": "เผยแพร่คอร์สนี้",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-xl border border-slate-300 px-3 py-2"}),
            "benefits": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-xl border border-slate-300 px-3 py-2", "placeholder": "เช่น อาบน้ำฟรีหลังฝึก"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "block w-full text-sm", "accept": "image/*"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2"}),
            "duration_hr": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2", "min": 1}),
            "max_dogs": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2", "min": 1}),
            "price": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2", "min": 0, "step": "0.01"}),
            "deposit_price": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2", "min": 0, "step": "0.01"}),
            "location": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-3 py-2", "placeholder": "เช่น สนามฝึกสุนัข ..."}),
            "is_published": forms.CheckboxInput(attrs={"class": "h-4 w-4"}),
        }

class CourseRoundForm(forms.ModelForm):
    # แสดง checkbox หลายวัน
    days = forms.MultipleChoiceField(
        choices=Course.Day.choices, required=False,
        widget=forms.CheckboxSelectMultiple, label="เลือกหลายวัน",
    )

    class Meta:
        model = CourseRound
        fields = ["days", "start_time", "end_time"]
        labels = {"start_time": "เวลาเริ่ม", "end_time": "เวลาสิ้นสุด"}
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "w-full rounded-xl border border-slate-300 px-3 py-2"}, format="%H:%M"),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "w-full rounded-xl border border-slate-300 px-3 py-2"}, format="%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initial: list[int] -> list[str] เพื่อให้ checkbox ติ๊กถูก
        if self.instance and self.instance.pk and isinstance(self.instance.days, list):
            self.fields["days"].initial = [str(x) for x in self.instance.days or []]

    def clean_days(self):
        data = self.cleaned_data.get("days") or []
        return [int(x) for x in data]

    def clean(self):
        cleaned = super().clean()
        days = cleaned.get("days") or []
        st = cleaned.get("start_time")
        et = cleaned.get("end_time")
        if days:
            if not st or not et:
                raise forms.ValidationError("กรุณาระบุเวลาเริ่มและเวลาสิ้นสุด")
            if st >= et:
                raise forms.ValidationError("เวลาสิ้นสุดต้องมากกว่าเวลาเริ่ม")
        return cleaned

CourseRoundFormSet = inlineformset_factory(
    parent_model=Course,
    model=CourseRound,
    form=CourseRoundForm,
    fields=["days", "start_time", "end_time"],
    extra=1,
    can_delete=True,
)
