import io
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
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

def link_callback(uri, rel):
    """Manejo de rutas para Render"""
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri
    return path

# --- VISTAS DE NAVEGACIÓN ---
def home(request):
    perfil = get_active_profile()
    context = {'perfil': perfil}
    return render(request, 'home.html', context)

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

    merger = PdfMerger()

    # 1. Función para crear PDF desde HTML (CV y Separadores)
    def crear_pdf_en_memoria(template_name, extra_context):
        tmpl = get_template(template_name)
        html_content = tmpl.render(extra_context)
        result = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=result, link_callback=link_callback)
        result.seek(0)
        return result

    # 2. Agregar CV Principal
    merger.append(crear_pdf_en_memoria('cv_pdf_maestro.html', context))

    # 3. SECCIÓN DE CURSOS
    cursos_con_pdf = [c for c in context['cursos'] if c.rutacertificado]
    if cursos_con_pdf:
        # Página separadora
        merger.append(crear_pdf_en_memoria('separador_pdf.html', {'titulo': 'ANEXO: CERTIFICADOS DE CURSOS'}))
        for curso in cursos_con_pdf:
            try:
                with curso.rutacertificado.open(mode='rb') as f:
                    merger.append(io.BytesIO(f.read()))
            except: pass

    # 4. SECCIÓN DE RECONOCIMIENTOS
    recs_con_pdf = [r for r in context['reconocimientos'] if r.rutacertificado]
    if recs_con_pdf:
        # Página separadora
        merger.append(crear_pdf_en_memoria('separador_pdf.html', {'titulo': 'ANEXO: LOGROS Y RECONOCIMIENTOS'}))
        for rec in recs_con_pdf:
            try:
                with rec.rutacertificado.open(mode='rb') as f:
                    merger.append(io.BytesIO(f.read()))
            except: pass

    # 5. Respuesta
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    return response