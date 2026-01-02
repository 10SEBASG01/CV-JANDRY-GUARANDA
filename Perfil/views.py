from django.shortcuts import render
from .models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, VentaGarage,
    Reconocimientos, ProductosAcademicos, ProductosLaborales
)

def get_active_profile():
    """Función auxiliar para obtener el perfil marcado como activo."""
    return DatosPersonales.objects.filter(perfilactivo=1).first()

def home(request):
    perfil = get_active_profile()
    context = {
        'perfil': perfil,
        'resumen_exp': ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_cursos': CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_garage': VentaGarage.objects.filter(idperfilconqueestaactivo=perfil)[:5],
        # Nuevos resúmenes
        'resumen_rec': Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_acad': ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_lab': ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil)[:3],
    }
    return render(request, 'home.html', context)

# Vistas para las futuras secciones (por ahora solo renderizan con el perfil)
def experiencia(request):
    perfil = get_active_profile()
    # Importante: traemos los datos de ExperienciaLaboral
    datos = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'experiencia.html', {'datos': datos, 'perfil': perfil})

def productos_academicos(request):
    perfil = get_active_profile()
    # Traemos los productos académicos del perfil activo
    datos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'productos_academicos.html', {'datos': datos, 'perfil': perfil})

def productos_laborales(request):
    perfil = get_active_profile()
    # Filtramos por el perfil activo y los marcados como visibles
    datos = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by('-fechaproducto')
    return render(request, 'productos_laborales.html', {'datos': datos, 'perfil': perfil})

def cursos(request):
    perfil = get_active_profile()
    datos = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    # QUITAMOS EL "secciones/" AQUÍ ABAJO:
    return render(request, 'cursos.html', {'datos': datos, 'perfil': perfil})

def reconocimientos(request):
    perfil = get_active_profile()
    datos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by('-fechareconocimiento')
    return render(request, 'reconocimientos.html', {'datos': datos, 'perfil': perfil})

def garage(request):
    perfil = get_active_profile()
    # Traemos los productos de la venta de garage
    datos = VentaGarage.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'garage.html', {'datos': datos, 'perfil': perfil})