from django.urls import path
from . import views

app_name = 'queue_app'

urlpatterns = [
    path('',                                views.register,      name='register'),
    path('confirmation/<int:turn_number>/', views.confirmation,  name='confirmation'),
    path('display/',                        views.display,       name='display'),
    path('admin-panel/',                    views.admin_panel,   name='admin_panel'),
    path('call-next/',                      views.call_next,     name='call_next'),
    path('mark-attended/<int:entry_id>/',   views.mark_attended, name='mark_attended'),
    path('reset-queue/',                    views.reset_queue,   name='reset_queue'),
]
