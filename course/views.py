from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course
from .forms import CourseForm, CourseRoundFormSet
from trainmydog.models import Profile  # ตรวจสอบ path ให้ตรงกับโปรเจกต์ของคุณ


# ✅ เฉพาะผู้ใช้ role = TRAINER เท่านั้นที่เข้าได้
def trainer_required(view_func):
    return login_required(user_passes_test(
        lambda u: hasattr(u, "profile") and u.profile.role == Profile.Role.TRAINER
    )(view_func))


# ✅ แสดงรายละเอียดคอร์สสาธารณะ (สำหรับผู้ใช้ทั่วไป)
def course_detail(request, pk):
    course = get_object_or_404(
        Course, pk=pk, is_published=True, trainer__profile__role=Profile.Role.TRAINER
    )
    return render(request, "courses/course_detail.html", {"course": course})


# ✅ แสดงรายการคอร์สของครูฝึก (My Courses)
@trainer_required
def course_trainer(request):
    qs = Course.objects.filter(trainer=request.user).prefetch_related("rounds").order_by("-created_at")
    return render(request, "courses/course_trainer.html", {"courses": qs})


# ✅ สร้างคอร์สใหม่
@trainer_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.trainer = request.user
            obj.save()

            round_formset = CourseRoundFormSet(request.POST, instance=obj, prefix="rounds")
            if round_formset.is_valid():
                round_formset.save()
                messages.success(request, "✅ สร้างคอร์สเรียบร้อยแล้ว")
                return redirect("courses:course_trainer")
            else:
                messages.error(request, "⚠️ กรุณาตรวจสอบรอบสอนที่กรอกอีกครั้ง")
        else:
            round_formset = CourseRoundFormSet(request.POST or None, prefix="rounds")
            messages.error(request, "⚠️ กรุณาตรวจสอบข้อมูลคอร์สที่กรอกอีกครั้ง")
    else:
        form = CourseForm()
        round_formset = CourseRoundFormSet(prefix="rounds")

    return render(request, "courses/create_course.html", {
        "form": form,
        "round_formset": round_formset,
        "mode": "create",
    })


# ✅ แก้ไขคอร์ส
@trainer_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk, trainer=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        round_formset = CourseRoundFormSet(request.POST, instance=course, prefix="rounds")

        if form.is_valid() and round_formset.is_valid():
            form.save()
            round_formset.save()
            messages.success(request, "✅ บันทึกการแก้ไขคอร์สแล้ว")
            return redirect("courses:course_trainer")
        else:
            messages.error(request, "⚠️ กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = CourseForm(instance=course)
        round_formset = CourseRoundFormSet(instance=course, prefix="rounds")

    return render(request, "courses/create_course.html", {
        "form": form,
        "round_formset": round_formset,
        "mode": "update",
        "course": course,
    })


# ✅ ลบคอร์ส
@trainer_required
def delete_course(request, pk):
    if request.method != "POST":
        return redirect("courses:course_trainer")

    course = get_object_or_404(Course, pk=pk, trainer=request.user)
    course.delete()
    messages.success(request, "🗑️ ลบคอร์สเรียบร้อยแล้ว")
    return redirect("courses:course_trainer")
