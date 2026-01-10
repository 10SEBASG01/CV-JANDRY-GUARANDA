import io
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

# Librerías necesarias (pip install xhtml2pdf PyPDF2)
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

# Importación de tus modelos
from Perfil.models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, VentaGarage,
    Reconocimientos, ProductosAcademicos, ProductosLaborales
)

def get_active_profile():
    return DatosPersonales.objects.filter(perfilactivo=1).first()

# FUNCIÓN ESENCIAL PARA RENDER: Traduce URLs a rutas físicas para el PDF
def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri
    return path

# --- VISTAS ---
def home(request):
    perfil = get_active_profile()
    context = {
        'perfil': perfil,
        'resumen_exp': ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_cursos': CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_garage': VentaGarage.objects.filter(idperfilconqueestaactivo=perfil)[:5],
        'resumen_rec': Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_acad': ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil)[:3],
        'resumen_lab': ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil)[:3],
    }
    return render(request, 'home.html', context)

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

    # 1. Generar Hoja Maestra (Texto + Foto)
    template = get_template('cv_pdf_maestro.html')
    html = template.render(context)
    pdf_texto = io.BytesIO()
    
    # Se incluye el link_callback para que la foto no falle
    pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")), 
        dest=pdf_texto,
        link_callback=link_callback
    )

    merger = PdfMerger()
    pdf_texto.seek(0)
    merger.append(pdf_texto)

    # Función para adjuntar archivos binarios (Evita NotImplementedError)
    def adjuntar(campo):
        if campo and campo.name.lower().endswith('.pdf'):
            try:
                # Abrimos el archivo directamente desde el storage
                with campo.open(mode='rb') as archivo:
                    merger.append(io.BytesIO(archivo.read()))
            except Exception as e:
                print(f"Error al adjuntar: {e}")

    # 2. Adjuntar SOLO Cursos y Reconocimientos al final
    for curso in context['cursos']:
        adjuntar(curso.rutacertificado)

    for rec in context['reconocimientos']:
        adjuntar(rec.rutacertificado)

    # 3. Respuesta final
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    return response