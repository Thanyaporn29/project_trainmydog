# courses/urls.py
from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("trainer/", views.course_trainer, name="course_trainer"),
    path("trainer/create/", views.create_course, name="create_course"),
    path("trainer/<int:pk>/edit/", views.update_course, name="update_course"),
    path("trainer/<int:pk>/delete/", views.delete_course, name="delete_course"),
    
    path("<int:pk>/", views.course_detail, name="course_detail"),
]
