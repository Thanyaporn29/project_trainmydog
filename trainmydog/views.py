# trainmydog/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from course.models import Course          # ✅ โมเดลคอร์ส (app: course)
from base.models import Profile           # ✅ โมเดล Profile (ใช้ role = TRAINER)

from .models import TrainerApplication, TrainerCertificate
from .forms import TrainerApplicationForm


def home_view(request):
    """
    หน้าแรก (Landing/Home)
    แสดง Hero + รายการคอร์สที่ 'เผยแพร่แล้ว' จากครูฝึก
    """

    # ดึงเฉพาะคอร์สที่เผยแพร่ และเจ้าของเป็น TRAINER
    courses = (
        Course.objects
        .filter(
            is_published=True,
            trainer__profile__role=Profile.Role.TRAINER
        )
        .select_related('trainer', 'trainer__profile')
        .order_by('-created_at')  # เอาคอร์สที่สร้างล่าสุดขึ้นก่อน
    )

    return render(request, 'home.html', {'courses': courses})


def course_detail_view(request, pk):
    """
    ดูรายละเอียดคอร์ส (หน้า public สำหรับผู้ใช้ทั่วไป)
    ใช้ template: trainmydog/templates/course_detail.html
    """

    course = get_object_or_404(
        Course.objects.select_related('trainer', 'trainer__profile'),
        pk=pk,
        is_published=True,
        trainer__profile__role=Profile.Role.TRAINER,
    )

    # ✅ ตรงนี้ใช้ชื่อไฟล์ให้ตรงกับที่คุณบอกว่าอยู่ที่:
    # trainmydog/templates/course_detail.html
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
