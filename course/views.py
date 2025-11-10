from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course
from .forms import CourseForm, CourseRoundFormSet

# อิงบทบาทจากแอปผู้ใช้เดิม (ปรับ import ให้ตรงโปรเจกต์คุณ)
from trainmydog.models import Profile  # <-- ถ้า Profile อยู่ที่อื่น ให้แก้ path นี้

def trainer_required(view_func):
    return login_required(user_passes_test(
        lambda u: hasattr(u, "profile") and u.profile.role == Profile.Role.TRAINER
    )(view_func))

# แสดงคอร์สสาธารณะ 1 รายการ
def course_detail(request, pk):
    course = get_object_or_404(
        Course, pk=pk, is_published=True, trainer__profile__role=Profile.Role.TRAINER
    )
    return render(request, "courses/course_detail.html", {"course": course})

# รายการคอร์สของครูฝึก
@trainer_required
def trainer_course_list(request):
    qs = Course.objects.filter(trainer=request.user).prefetch_related("rounds").order_by("-created_at")
    return render(request, "courses/trainer_course_list.html", {"courses": qs})

# สร้างคอร์ส
@trainer_required
def trainer_course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.trainer = request.user
            obj.save()
            round_formset = CourseRoundFormSet(request.POST, instance=obj, prefix="rounds")
            if round_formset.is_valid():
                round_formset.save()
                messages.success(request, "สร้างคอร์สเรียบร้อย")
                return redirect("courses:trainer_course_list")
            else:
                messages.error(request, "กรุณาตรวจสอบรอบสอนที่กรอก")
        else:
            round_formset = CourseRoundFormSet(request.POST or None, prefix="rounds")
            messages.error(request, "กรุณาตรวจสอบข้อมูลคอร์สที่กรอกอีกครั้ง")
    else:
        form = CourseForm()
        round_formset = CourseRoundFormSet(prefix="rounds")

    return render(request, "courses/create_course.html", {
        "form": form,
        "round_formset": round_formset,
        "mode": "create",
    })

# แก้ไขคอร์ส
@trainer_required
def trainer_course_update(request, pk):
    course = get_object_or_404(Course, pk=pk, trainer=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        round_formset = CourseRoundFormSet(request.POST, instance=course, prefix="rounds")
        if form.is_valid() and round_formset.is_valid():
            form.save()
            round_formset.save()
            messages.success(request, "บันทึกการแก้ไขแล้ว")
            return redirect("courses:trainer_course_list")
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = CourseForm(instance=course)
        round_formset = CourseRoundFormSet(instance=course, prefix="rounds")

    return render(request, "courses/create_course.html", {
        "form": form,
        "round_formset": round_formset,
        "mode": "update",
        "course": course,
    })

# ลบคอร์ส
@trainer_required
def trainer_course_delete(request, pk):
    if request.method != "POST":
        return redirect("courses:trainer_course_list")
    course = get_object_or_404(Course, pk=pk, trainer=request.user)
    course.delete()
    messages.success(request, "ลบคอร์สเรียบร้อย")
    return redirect("courses:trainer_course_list")
