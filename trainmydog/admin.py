# trainmydog/admin.py
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from base.models import Profile  
from .models import TrainerApplication, TrainerCertificate


# ===== แนบ Profile ในหน้า User (ไว้ดู/แก้ role ได้สะดวก) =====
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "get_role",
                    "is_staff", "is_active")
    list_select_related = ("profile",)

    def get_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return "แอดมิน"
        prof = getattr(obj, "profile", None)
        return prof.get_role_display() if prof else "-"
    get_role.short_description = "Role"


# ลงทะเบียน User ใหม่ (กัน error หากยังไม่ถูก unregister)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


# ===== แนบไฟล์เกียรติบัตรในหน้า Application =====
class TrainerCertificateInline(admin.TabularInline):
    model = TrainerCertificate
    extra = 0
    fields = ("file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


# ===== หน้าจัดการคำขอเป็นครูฝึก =====
@admin.register(TrainerApplication)
class TrainerApplicationAdmin(admin.ModelAdmin):
    list_display = ( "id", "user", "full_name", "phone", "status","created_at", "reviewed_by", "reviewed_at",)
    list_filter = ("status", ("created_at", admin.DateFieldListFilter))
    search_fields = ("user__username", "user__email", "full_name", "phone", "email_snapshot")
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [TrainerCertificateInline]

    readonly_fields = ("created_at", "reviewed_by", "reviewed_at")
    actions = ["approve_applications", "reject_applications"]

    # บันทึกผู้ตรวจ/เวลาเมื่อมีการเปลี่ยนสถานะ และอัปเกรดบทบาทเมื่ออนุมัติ
    def save_model(self, request, obj, form, change):
        status_changed = change and ("status" in getattr(form, "changed_data", []))
        if status_changed:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

        if obj.status == TrainerApplication.Status.APPROVED:
            profile, _ = Profile.objects.get_or_create(user=obj.user)
            if profile.role != Profile.Role.TRAINER:
                profile.role = Profile.Role.TRAINER
                profile.save(update_fields=["role"])

    # ------- Bulk actions -------
    def approve_applications(self, request, queryset):
        count = 0
        for app in queryset.exclude(status=TrainerApplication.Status.APPROVED):
            app.status = TrainerApplication.Status.APPROVED
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save()

            profile, _ = Profile.objects.get_or_create(user=app.user)
            if profile.role != Profile.Role.TRAINER:
                profile.role = Profile.Role.TRAINER
                profile.save(update_fields=["role"])
            count += 1
        self.message_user(request, f"อนุมัติคำร้องและอัปเกรดเป็นผู้ฝึกแล้ว {count} รายการ")
    approve_applications.short_description = "อนุมัติคำร้อง"

    def reject_applications(self, request, queryset):
        updated = 0
        for app in queryset.exclude(status=TrainerApplication.Status.REJECTED):
            app.status = TrainerApplication.Status.REJECTED
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save()
            updated += 1
        self.message_user(request, f"ปฏิเสธคำร้องแล้ว {updated} รายการ")
    reject_applications.short_description = "ปฏิเสธคำร้อง"


# ===== เมนูแยกสำหรับดู/ค้นไฟล์เกียรติบัตร =====
@admin.register(TrainerCertificate)
class TrainerCertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "file", "uploaded_at")
    search_fields = ("application__full_name", "application__user__email")
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)
    list_per_page = 25
