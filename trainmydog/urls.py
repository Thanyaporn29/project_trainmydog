# trainmydog/urls.py
from django.urls import path
from django.views.generic import RedirectView
from .views import home_view, apply_trainer_view, course_detail_view 

app_name = 'trainmydog'

urlpatterns = [
    # หน้าแรกของเว็บไซต์
    path('', home_view, name='home'),
    path('home/', RedirectView.as_view(pattern_name='trainmydog:home', permanent=False)),

    # สมัครเป็นครูฝึก
    path('trainer/apply/', apply_trainer_view, name='apply_trainer'),

    path('courses/<int:pk>/', course_detail_view, name='course_detail'),

]
