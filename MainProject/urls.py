from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static,re_path
from . import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('MainApp.urls')),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }), ]

handler404 = 'MainApp.views.handler404'
handler500 = 'MainApp.views.handler500'
handler403 = 'MainApp.views.handler403'
handler400 = 'MainApp.views.handler400'