from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from okszu.views import index, usermanage, useredit, do_attestation, attestation_done, view_admin_result_user, \
    profile, get_answer, make_result_into_excel, view_user_attestation


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('accounts/', include('accounts.urls')),
    path('profile/', profile, name='profile'),
    path('user-manage', usermanage, name='user-manage'),
    path('user-edit/<int:pk>/', useredit, name='user-edit'),
    path('doattest/<int:pk>/', do_attestation, name='doattest'),
    path('done/', attestation_done, name='done'),
    path('doanswer/<int:pk>/', get_answer, name='doanswer'),
    path('admin-result/<int:pk>/', view_admin_result_user, name='admin-result'),
    path('get-excel/<int:pk>/', make_result_into_excel, name='get-excel'),
    path('user-result/<int:pk>/', view_user_attestation, name='user-result'),
    path('adminwrap/', include('adminwrap.urls', namespace='adminwrap')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

