from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Perfil import views # Importamos tus vistas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('experiencia/', views.experiencia, name='experiencia'),
    path('productos-academicos/', views.productos_academicos, name='productos_academicos'),
    path('productos-laborales/', views.productos_laborales, name='productos_laborales'),
    path('cursos/', views.cursos, name='cursos'),
    path('reconocimientos/', views.reconocimientos, name='reconocimientos'),
    path('garage/', views.garage, name='garage'),
]

# ESTO ES LO QUE HACE QUE EL NAVEGADOR PUEDA ABRIR TUS DIPLOMAS
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)