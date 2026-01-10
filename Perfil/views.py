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
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri
    return path

# --- VISTAS DE NAVEGACIÓN ---
def home(request): return render(request, 'home.html', {'perfil': get_active_profile()})
def experiencia(request): return render(request, 'experiencia.html', {'datos': ExperienciaLaboral.objects.all(), 'perfil': get_active_profile()})
def productos_academicos(request): return render(request, 'productos_academicos.html', {'datos': ProductosAcademicos.objects.all(), 'perfil': get_active_profile()})
def productos_laborales(request): return render(request, 'productos_laborales.html', {'datos': ProductosLaborales.objects.all(), 'perfil': get_active_profile()})
def cursos(request): return render(request, 'cursos.html', {'datos': CursosRealizados.objects.all(), 'perfil': get_active_profile()})
def reconocimientos(request): return render(request, 'reconocimientos.html', {'datos': Reconocimientos.objects.all(), 'perfil': get_active_profile()})
def garage(request): return render(request, 'garage.html', {'datos': VentaGarage.objects.all(), 'perfil': get_active_profile()})

# --- FUNCIÓN MAESTRA DE PDF ---
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

    # 1. Crear el CV base (Hoja de texto diseñada)
    template = get_template('cv_pdf_maestro.html')
    html = template.render(context)
    pdf_texto = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=pdf_texto, link_callback=link_callback)

    # 2. Preparar el Merger para unir archivos
    merger = PdfMerger()
    pdf_texto.seek(0)
    merger.append(pdf_texto)

    # 3. Función para pegar los PDFs reales (Certificados)
    def agregar_pdf(campo_archivo):
        if campo_archivo and hasattr(campo_archivo, 'name') and campo_archivo.name.lower().endswith('.pdf'):
            try:
                archivo_abierto = campo_archivo.open(mode='rb')
                merger.append(io.BytesIO(archivo_abierto.read()))
                archivo_abierto.close()
            except:
                pass

    # 4. Pegar documentos al final en orden
    for exp in context['experiencias']:
        agregar_pdf(exp.rutacertificado)
    for curso in context['cursos']:
        agregar_pdf(curso.rutacertificado)
    for rec in context['reconocimientos']:
        agregar_pdf(rec.rutacertificado)

    # 5. Generar Salida
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    return response