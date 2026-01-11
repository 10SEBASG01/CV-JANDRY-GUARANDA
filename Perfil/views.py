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
    ProductosAcademicos, ProductosLaborales
)

# --- VISTAS DE NAVEGACIÓN ---
def get_active_profile():
    return DatosPersonales.objects.filter(perfilactivo=1).first()

def home(request): return render(request, 'home.html', {'perfil': get_active_profile()})
def experiencia(request): return render(request, 'experiencia.html', {'datos': ExperienciaLaboral.objects.all(), 'perfil': get_active_profile()})
def productos_academicos(request): return render(request, 'productos_academicos.html', {'datos': ProductosAcademicos.objects.all(), 'perfil': get_active_profile()})
def productos_laborales(request): return render(request, 'productos_laborales.html', {'datos': ProductosLaborales.objects.all(), 'perfil': get_active_profile()})
def cursos(request): return render(request, 'cursos.html', {'datos': CursosRealizados.objects.all(), 'perfil': get_active_profile()})
def reconocimientos(request): return render(request, 'reconocimientos.html', {'datos': Reconocimientos.objects.all(), 'perfil': get_active_profile()})
def garage(request): return render(request, 'garage.html', {'datos': garage.objects.all(), 'perfil': get_active_profile()})

# --- FUNCIÓN DEL PDF ---
def pdf_datos_personales(request):
    perfil = get_object_or_404(DatosPersonales, perfilactivo=1)
    
    # Consultas filtradas
    experiencias = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    productos_academicos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    productos_laborales = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    cursos_objs = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    reconocimientos_objs = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)

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
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=buffer_cv_base)

    writer = PdfWriter()
    buffer_cv_base.seek(0)
    writer.append(buffer_cv_base)

    # Lógica de anexos que tú pasaste
    def anexar_pdfs(queryset, titulo):
        validos = [o for o in queryset if o.rutacertificado]
        if validos:
            for obj in validos:
                try:
                    r = requests.get(obj.rutacertificado.url, timeout=15)
                    if r.status_code == 200:
                        writer.append(io.BytesIO(r.content))
                except: pass

    anexar_pdfs(cursos_objs, "Cursos")
    anexar_pdfs(reconocimientos_objs, "Reconocimientos")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Portafolio_{perfil.apellidos}.pdf"'
    writer.write(response)
    writer.close()
    return response