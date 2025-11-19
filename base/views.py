# base/views.py
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Profile
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm


class AuthLoginView(LoginView):
    """
    หน้าเข้าสู่ระบบ (ใช้ email เป็น username)
    """
    template_name = 'Authen/login.html'
    redirect_authenticated_user = True  # ถ้าล็อกอินแล้ว เด้งออกจากหน้า Login

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # ซ่อน Navbar/Footer ในหน้า Login (base.html เช็คตัวแปรนี้)
        ctx['hide_navbar'] = True
        return ctx


def logout_view(request):
    """
    ออกจากระบบ แล้วเด้งกลับหน้า home (trainmydog:home)
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('trainmydog:home')


def register_view(request):
    """
    สมัครสมาชิกใหม่ แล้วล็อกอินให้อัตโนมัติ จากนั้นเด้งกลับหน้า home
    """
    # กันไม่ให้คนที่ล็อกอินแล้วเข้าหน้าสมัคร
    if request.user.is_authenticated:
        return redirect('trainmydog:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # RegisterForm จัดการสร้าง user + profile (role=member) ให้แล้ว
            user = form.save()
            # กันกรณีสุดขั้ว: ถ้า signal ไม่ทำงาน, ensure ว่ามีโปรไฟล์
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('trainmydog:home')
    else:
        form = RegisterForm()

    return render(request, 'Authen/register.html', {
        'form': form,
        'hide_navbar': True,   # ซ่อน Navbar/Footer ในหน้า Register
    })


@login_required
def profile_view(request):
    """
    แสดงหน้าโปรไฟล์ของผู้ใช้ (อ่านอย่างเดียว)
    template: Authen/profile.html
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'Authen/profile.html', {
        'user_obj': request.user,
        'profile': profile,
        # ไม่ส่ง hide_navbar -> ให้ base.html แสดง navbar ตามปกติ
    })


@login_required
def profile_edit_view(request):
    """
    แก้ไขโปรไฟล์ผู้ใช้ (ชื่อ, นามสกุล, เบอร์โทร, รูปโปรไฟล์)
    template: Authen/profile_edit.html
    """
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    # เคสคลิกปุ่ม "ลบรูปโปรไฟล์"
    if request.method == 'POST' and 'delete_avatar' in request.POST:
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save(update_fields=['avatar'])
        return redirect('Authen:profile_edit')

    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=user, user=user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if uform.is_valid() and pform.is_valid():
            # ล็อกให้อีเมล/username เป็นค่าเดิม ห้ามเปลี่ยน
            u = uform.save(commit=False)
            current_email = (user.email or '').lower()
            u.email = current_email
            u.username = current_email
            u.save()

            pform.save()
            messages.success(request, 'อัปเดตข้อมูลเรียบร้อย')
            return redirect('Authen:profile')
    else:
        uform = UserUpdateForm(instance=user, user=user)
        pform = ProfileUpdateForm(instance=profile)

    return render(request, 'Authen/profile_edit.html', {
        'uform': uform,
        'pform': pform,
    })
