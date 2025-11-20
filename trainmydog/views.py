# trainmydog/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from course.models import Course          # โมเดลคอร์ส (app: course)
from base.models import Profile           # Profile ใช้ role = TRAINER

from .models import TrainerApplication, TrainerCertificate, Booking
from .forms import TrainerApplicationForm, BookingForm, TrainerBookingActionForm


def trainer_required(view_func):
    """
    decorator สำหรับ view ที่อนุญาตเฉพาะผู้ใช้ role = TRAINER
    """
    return login_required(
        user_passes_test(
            lambda u: hasattr(u, "profile") and u.profile.role == Profile.Role.TRAINER,
            login_url="Authen:login"
        )(view_func)
    )


def home_view(request):
    """
    หน้าแรก (Landing/Home)
    แสดง Hero + รายการคอร์สที่ 'เผยแพร่แล้ว' จากครูฝึก
    """
    courses = (
        Course.objects
        .filter(
            is_published=True,
            trainer__profile__role=Profile.Role.TRAINER
        )
        .select_related('trainer', 'trainer__profile')
        .order_by('-created_at')
    )

    return render(request, 'home.html', {'courses': courses})


def course_detail_view(request, pk):
    """
    ดูรายละเอียดคอร์ส (หน้า public สำหรับผู้ใช้ทั่วไป)
    """
    course = get_object_or_404(
        Course.objects.select_related('trainer', 'trainer__profile'),
        pk=pk,
        is_published=True,
        trainer__profile__role=Profile.Role.TRAINER,
    )

    return render(request, 'course_detail.html', {
        'course': course,
    })


@login_required
def apply_trainer_view(request):
    latest = TrainerApplication.objects.filter(user=request.user).order_by('-created_at').first()
    block_resubmit = False
    block_message = None

    if latest:
        if latest.status == TrainerApplication.Status.PENDING:
            block_resubmit = True
            block_message = "คุณมีคำร้องที่รอดดำเนินการอยู่ จึงไม่สามารถส่งคำร้องอีกได้"
        elif latest.status == TrainerApplication.Status.APPROVED:
            block_resubmit = True
            block_message = "คุณได้รับการอนุมัติแล้ว ไม่สามารถส่งคำร้องใหม่ได้"

    if request.method == 'POST':
        if block_resubmit:
            messages.warning(request, block_message)
            return redirect('trainmydog:home')

        form = TrainerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.email_snapshot = form.cleaned_data.get("email_snapshot") or request.user.email
            app.save()

            cert_file = form.cleaned_data.get("certificate")
            if cert_file:
                TrainerCertificate.objects.create(application=app, file=cert_file)

            messages.success(request, "ส่งคำขอเรียบร้อย รอแอดมินตรวจสอบ")
            return redirect('trainmydog:home')
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอก")
    else:
        initial = {
            "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "email_snapshot": request.user.email,
        }
        prof = getattr(request.user, "profile", None)
        if prof and prof.phone:
            initial["phone"] = prof.phone
        form = TrainerApplicationForm(initial=initial)

    return render(request, 'apply_trainer.html', {
        'form': form,
        'latest': latest,
        'block_resubmit': block_resubmit,
        'block_message': block_message,
    })


# ====== จองคอร์ส (สมาชิก) ======
@login_required
def booking_create(request, course_pk):
    course = get_object_or_404(
        Course,
        pk=course_pk,
        is_published=True,
        trainer__profile__role=Profile.Role.TRAINER,
    )

    # กันไม่ให้ครูฝึกจองคอร์สตัวเอง
    if request.user == course.trainer:
        messages.warning(request, "คุณไม่สามารถจองคอร์สของตัวเองได้")
        return redirect("trainmydog:course_detail", pk=course.pk)

    if request.method == "POST":
        form = BookingForm(request.POST, course=course)
        if form.is_valid():
            bk = form.save(commit=False)
            bk.user = request.user
            bk.course = course
            bk.save()
            messages.success(request, "ส่งคำขอจองเรียบร้อย รอครูฝึกอนุมัติ")
            return redirect("trainmydog:booking_history")
    else:
        form = BookingForm(course=course)

    return render(request, "booking_form.html", {
        "course": course,
        "form": form,
    })


@login_required
def booking_history(request):
    """
    ประวัติการจองของสมาชิก (ดึงตาม user)
    """
    qs = (
        Booking.objects
        .filter(user=request.user)
        .select_related("course", "round", "course__trainer")
        .order_by("-created_at")
    )
    return render(request, "history_booking.html", {"bookings": qs})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related("course", "round", "course__trainer"),
        pk=pk,
        user=request.user
    )
    return render(request, "booking_detail.html", {"booking": booking})


# ====== ครูฝึกดูคำขอจองในคอร์สของตัวเอง ======
@trainer_required
def trainer_booking_list(request):
    status = request.GET.get("status", "")
    qs = (
        Booking.objects
        .filter(course__trainer=request.user)
        .select_related("user", "course", "round")
        .order_by("-created_at")
    )

    if status in {
        Booking.Status.PENDING,
        Booking.Status.APPROVED,
        Booking.Status.REJECTED,
        Booking.Status.CANCELED
    }:
        qs = qs.filter(status=status)

    pending_count = Booking.objects.filter(
        course__trainer=request.user,
        status=Booking.Status.PENDING
    ).count()

    return render(request, "trainer_booking_list.html", {
        "bookings": qs,
        "status": status,
        "pending_count": pending_count,
    })


@require_POST
@trainer_required
def trainer_booking_update_status(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        course__trainer=request.user
    )

    # เปลี่ยนได้เฉพาะตอนยัง pending
    if booking.status != Booking.Status.PENDING:
        messages.warning(request, "ไม่สามารถเปลี่ยนสถานะได้ รายการนี้ถูกดำเนินการแล้ว")
        return redirect("trainmydog:trainer_booking_list")

    new_status = (request.POST.get("status") or "").strip().lower()
    if new_status not in (Booking.Status.APPROVED, Booking.Status.REJECTED):
        messages.error(request, "ค่าสถานะไม่ถูกต้อง")
        return redirect("trainmydog:trainer_booking_list")

    booking.status = new_status
    booking.save(update_fields=["status"])

    if new_status == Booking.Status.APPROVED:
        messages.success(request, "อนุมัติการจองเรียบร้อย")
    else:
        messages.success(request, "ปฏิเสธการจองเรียบร้อย")

    next_url = request.POST.get("next")
    return redirect(next_url or "trainmydog:trainer_booking_list")


@require_POST
@trainer_required
def trainer_booking_delete(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        course__trainer=request.user
    )
    booking.delete()
    messages.success(request, "ลบรายการจองเรียบร้อยแล้ว")
    next_url = request.POST.get("next")
    return redirect(next_url or "trainmydog:trainer_booking_list")
