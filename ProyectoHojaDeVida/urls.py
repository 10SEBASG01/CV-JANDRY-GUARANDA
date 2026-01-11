from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Perfil import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('experiencia/', views.experiencia, name='experiencia'),
    path('productos-academicos/', views.productos_academicos, name='productos_academicos'),
    path('productos-laborales/', views.productos_laborales, name='productos_laborales'),
    path('cursos/', views.cursos, name='cursos'),
    path('reconocimientos/', views.reconocimientos, name='reconocimientos'),
    path('garage/', views.garage, name='garage'),
    # Esta línea debe usar el nombre exacto que definimos en views.py
    path('exportar-cv-completo/', views.pdf_datos_personales, name='exportar_cv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)