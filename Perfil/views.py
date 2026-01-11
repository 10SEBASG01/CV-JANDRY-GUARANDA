import io
import requests
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from pypdf import PdfWriter  # Asegúrate de tener: pip install pypdf

from Perfil.models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, Reconocimientos, 
    ProductosAcademicos, ProductosLaborales
)

def link_callback(uri, rel):
    """Necesario para que xhtml2pdf cargue la foto de perfil en el PDF"""
    return uri

def crear_caratula(titulo):
    """Genera una página de separación simple en memoria"""
    html = f"""
    <html><body style="font-family: Helvetica; text-align: center; padding-top: 10cm;">
        <h1 style="font-size: 40pt; color: #004085; border: 5px solid #004085; padding: 20px;">{titulo}</h1>
    </body></html>
    """
    buffer = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=buffer)
    return buffer

def pdf_datos_personales(request):
    perfil = get_object_or_404(DatosPersonales, perfilactivo=1)
    
    # Consultas filtradas exactamente como las tienes
    experiencias = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    productos_academicos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    productos_laborales = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    cursos_objs = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    reconocimientos_objs = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)

    # --- PARTE A: GENERAR EL CV BASE ---
    template = get_template('cv_pdf_maestro.html')
    context = {
        'perfil': perfil,
        'items': experiencias,
        'productos': productos_academicos,
        'productos_laborales': productos_laborales,
        'cursos': cursos_objs,
        'reconocimientos': reconocimientos_objs,
    }
    html = template.render(context)
    buffer_cv_base = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=buffer_cv_base, link_callback=link_callback)

    # --- PARTE B: UNIR CON LOS PDFs (Anexos) ---
    writer = PdfWriter()
    buffer_cv_base.seek(0)
    writer.append(buffer_cv_base)

    # 1. Anexar Cursos
    cursos_con_pdf = [c for c in cursos_objs if c.rutacertificado]
    if cursos_con_pdf:
        caratula = crear_caratula("Certificados de Cursos")
        caratula.seek(0)
        writer.append(caratula)
        for curso in cursos_con_pdf:
            try:
                response = requests.get(curso.rutacertificado.url, timeout=15)
                if response.status_code == 200:
                    writer.append(io.BytesIO(response.content))
            except: pass

    # 2. Anexar Reconocimientos
    reco_con_pdf = [r for r in reconocimientos_objs if r.rutacertificado]
    if reco_con_pdf:
        caratula = crear_caratula("Reconocimientos")
        caratula.seek(0)
        writer.append(caratula)
        for reco in reco_con_pdf:
            try:
                response = requests.get(reco.rutacertificado.url, timeout=15)
                if response.status_code == 200:
                    writer.append(io.BytesIO(response.content))
            except: pass

    # --- PARTE C: RESPUESTA ---
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    writer.write(response)
    writer.close()
    return response