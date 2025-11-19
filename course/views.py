from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course
from .forms import CourseForm, CourseRoundFormSet
from trainmydog.models import Profile


# แค่ตรวจสิทธิ์ครูฝึก
def trainer_required(view_func):
    return login_required(
        user_passes_test(
            lambda u: hasattr(u, "profile") and u.profile.role == Profile.Role.TRAINER
        )(view_func)
    )


# คอร์สสาธารณะ
def course_detail(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk,
        is_published=True,
        trainer__profile__role=Profile.Role.TRAINER,
    )
    return render(request, "courses/course_detail.html", {"course": course})


# คอร์สของครูฝึก
@trainer_required
def course_trainer(request):
    qs = (
        Course.objects.filter(trainer=request.user)
        .prefetch_related("rounds")
        .order_by("-created_at")
    )
    return render(request, "courses/course_trainer.html", {"courses": qs})


# สร้างคอร์ส
@trainer_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        round_formset = CourseRoundFormSet(request.POST, prefix="rounds")

        if form.is_valid() and round_formset.is_valid():
            obj = form.save(commit=False)
            obj.trainer = request.user
            obj.save()
            round_formset.instance = obj
            round_formset.save()
            return redirect("courses:course_trainer")
    else:
        form = CourseForm()
        round_formset = CourseRoundFormSet(prefix="rounds")

    return render(
        request,
        "courses/create_course.html",
        {
            "form": form,
            "round_formset": round_formset,
            "mode": "create",
        },
    )


# แก้ไขคอร์ส
@trainer_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk, trainer=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        round_formset = CourseRoundFormSet(request.POST, instance=course, prefix="rounds")

        if form.is_valid() and round_formset.is_valid():
            form.save()
            round_formset.save()
            return redirect("courses:course_trainer")
    else:
        form = CourseForm(instance=course)
        round_formset = CourseRoundFormSet(instance=course, prefix="rounds")

    return render(
        request,
        "courses/create_course.html",
        {
            "form": form,
            "round_formset": round_formset,
            "mode": "update",
            "course": course,
        },
    )


# ลบคอร์ส
@trainer_required
def delete_course(request, pk):
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk, trainer=request.user)
        course.delete()
    return redirect("courses:course_trainer")
