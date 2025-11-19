from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ระบบสมาชิก (login/register/profile)
    path('auth/', include(('base.urls', 'base'), namespace='Authen')),

    path('', include(('trainmydog.urls', 'trainmydog'), namespace='trainmydog')),
    path('courses/', include(('course.urls', 'course'), namespace='courses')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
