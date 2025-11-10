from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # สาธารณะ
    path("<int:pk>/", views.course_detail, name="course_detail"),

    # สำหรับครูฝึก
    path("trainer/", views.trainer_course_list, name="trainer_course_list"),
    path("trainer/create/", views.trainer_course_create, name="trainer_course_create"),
    path("trainer/<int:pk>/edit/", views.trainer_course_update, name="trainer_course_update"),
    path("trainer/<int:pk>/delete/", views.trainer_course_delete, name="trainer_course_delete"),
]
