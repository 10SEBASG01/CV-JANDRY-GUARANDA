import io
import requests
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from pypdf import PdfWriter 

from Perfil.models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, Reconocimientos, 
    ProductosAcademicos, ProductosLaborales, VentaGarage
)

def get_active_profile():
    return DatosPersonales.objects.filter(perfilactivo=1).first()

# --- VISTA HOME (CORREGIDA PARA QUE SALGAN LOS DATOS) ---
def home(request):
    perfil = get_active_profile()
    if not perfil:
        return render(request, 'home.html', {'perfil': None})

    context = {
        'perfil': perfil,
        'resumen_exp': ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)[:3],
        'resumen_cursos': CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)[:3],
        'resumen_rec': Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)[:3],
        'resumen_acad': ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)[:3],
        'resumen_lab': ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)[:3],
        'resumen_garage': VentaGarage.objects.all()[:5],
    }
    return render(request, 'home.html', context)

# --- VISTAS DE NAVEGACIÓN RESTANTES ---
def experiencia(request): return render(request, 'experiencia.html', {'datos': ExperienciaLaboral.objects.all(), 'perfil': get_active_profile()})
def productos_academicos(request): return render(request, 'productos_academicos.html', {'datos': ProductosAcademicos.objects.all(), 'perfil': get_active_profile()})
def productos_laborales(request): return render(request, 'productos_laborales.html', {'datos': ProductosLaborales.objects.all(), 'perfil': get_active_profile()})
def cursos(request): return render(request, 'cursos.html', {'datos': CursosRealizados.objects.all(), 'perfil': get_active_profile()})
def reconocimientos(request): return render(request, 'reconocimientos.html', {'datos': Reconocimientos.objects.all(), 'perfil': get_active_profile()})
def garage(request): return render(request, 'garage.html', {'datos': VentaGarage.objects.all(), 'perfil': get_active_profile()})

# --- VISTA DEL PDF (MAESTRA) ---
def exportar_cv_completo(request):
    perfil = get_object_or_404(DatosPersonales, perfilactivo=1)
    
    # Datos para el PDF
    experiencias = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    academicos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    laborales = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    cursos_objs = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    reco_objs = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)

    # 1. Crear el PDF del CV base
    template = get_template('cv_pdf_maestro.html')
    html = template.render({
        'perfil': perfil, 'items': experiencias, 'productos': academicos,
        'productos_laborales': laborales, 'cursos': cursos_objs, 'reconocimientos': reco_objs
    })
    
    buffer_cv = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=buffer_cv)

    # 2. Unir anexos
    writer = PdfWriter()
    buffer_cv.seek(0)
    writer.append(buffer_cv)

    def pegar_certificados(queryset):
        for obj in queryset:
            if obj.rutacertificado:
                try:
                    r = requests.get(obj.rutacertificado.url, timeout=10)
                    if r.status_code == 200:
                        writer.append(io.BytesIO(r.content))
                except: pass

    pegar_certificados(cursos_objs)
    pegar_certificados(reco_objs)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    writer.write(response)
    writer.close()
    return response