# trainmydog/urls.py
from django.urls import path
from django.views.generic import RedirectView

from .views import (
    home_view,
    apply_trainer_view,
    course_detail_view,
    booking_create,
    booking_history,
    booking_detail,
    trainer_booking_list,
    trainer_booking_update_status,
    trainer_booking_delete,
)

app_name = 'trainmydog'

urlpatterns = [
    # หน้าแรกของเว็บไซต์
    path('', home_view, name='home'),
    path('home/', RedirectView.as_view(pattern_name='trainmydog:home', permanent=False)),

    # สมัครเป็นครูฝึก
    path('trainer/apply/', apply_trainer_view, name='apply_trainer'),

    # รายละเอียดคอร์ส
    path('courses/<int:pk>/', course_detail_view, name='course_detail'),

    # จองคอร์ส
    path('courses/<int:course_pk>/book/', booking_create, name='booking_create'),

    # ประวัติการจองของสมาชิก
    path('bookings/history/', booking_history, name='booking_history'),
    path('bookings/<int:pk>/', booking_detail, name='booking_detail'),

    # จัดการคำขอจองของครูฝึก
    path('trainer/bookings/', trainer_booking_list, name='trainer_booking_list'),
    path(
        'trainer/bookings/<int:pk>/update/',
        trainer_booking_update_status,
        name='trainer_booking_update_status'
    ),
    path(
        'trainer/bookings/<int:pk>/delete/',
        trainer_booking_delete,
        name='trainer_booking_delete'
    ),
]
