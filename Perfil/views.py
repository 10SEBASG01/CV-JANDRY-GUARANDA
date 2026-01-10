import io
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

from Perfil.models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, VentaGarage,
    Reconocimientos, ProductosAcademicos, ProductosLaborales
)

def get_active_profile():
    return DatosPersonales.objects.filter(perfilactivo=1).first()

def link_callback(uri, rel):
    """Manejo de rutas para que la foto de perfil aparezca en Render"""
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri
    return path

# --- VISTAS DE NAVEGACIÓN ---
def home(request):
    return render(request, 'home.html', {'perfil': get_active_profile()})

def experiencia(request):
    perfil = get_active_profile()
    datos = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'experiencia.html', {'datos': datos, 'perfil': perfil})

def productos_academicos(request):
    perfil = get_active_profile()
    datos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'productos_academicos.html', {'datos': datos, 'perfil': perfil})

def productos_laborales(request):
    perfil = get_active_profile()
    datos = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'productos_laborales.html', {'datos': datos, 'perfil': perfil})

def cursos(request):
    perfil = get_active_profile()
    datos = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'cursos.html', {'datos': datos, 'perfil': perfil})

def reconocimientos(request):
    perfil = get_active_profile()
    datos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'reconocimientos.html', {'datos': datos, 'perfil': perfil})

def garage(request):
    perfil = get_active_profile()
    datos = VentaGarage.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'garage.html', {'datos': datos, 'perfil': perfil})

# --- EXPORTAR PDF COMPLETO ---
def exportar_cv_completo(request):
    perfil = get_active_profile()
    context = {
        'perfil': perfil,
        'experiencias': ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'cursos': CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'reconocimientos': Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'academicos': ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'laborales': ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
    }

    # 1. Generar el PDF base (CV + Hojas de Separación integradas)
    template = get_template('cv_pdf_maestro.html')
    html = template.render(context)
    pdf_principal = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=pdf_principal, link_callback=link_callback)

    merger = PdfMerger()
    pdf_principal.seek(0)
    merger.append(pdf_principal)

    # 2. Adjuntar los PDFs de certificados reales
    def adjuntar(campo):
        if campo and campo.name.lower().endswith('.pdf'):
            try:
                # Lectura binaria directa para evitar errores de rutas absolutas
                with campo.open(mode='rb') as f:
                    merger.append(io.BytesIO(f.read()))
            except:
                pass

    # Importante: El orden aquí debe coincidir con el del HTML
    for c in context['cursos']:
        adjuntar(c.rutacertificado)
    for r in context['reconocimientos']:
        adjuntar(r.rutacertificado)

    # 3. Respuesta final
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    return response