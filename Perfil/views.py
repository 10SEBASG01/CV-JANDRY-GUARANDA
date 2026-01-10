import io
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

# Librerías necesarias (Instalar con: pip install xhtml2pdf PyPDF2)
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

# Importación absoluta para evitar errores de resolución en el editor
from Perfil.models import (
    DatosPersonales, ExperienciaLaboral, 
    CursosRealizados, VentaGarage,
    Reconocimientos, ProductosAcademicos, ProductosLaborales
)

def get_active_profile():
    """Obtiene el perfil marcado como activo."""
    return DatosPersonales.objects.filter(perfilactivo=1).first()

# --- VISTAS DE NAVEGACIÓN ---

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
    datos = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by('-fechaproducto')
    return render(request, 'productos_laborales.html', {'datos': datos, 'perfil': perfil})

def cursos(request):
    perfil = get_active_profile()
    datos = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'cursos.html', {'datos': datos, 'perfil': perfil})

def reconocimientos(request):
    perfil = get_active_profile()
    datos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by('-fechareconocimiento')
    return render(request, 'reconocimientos.html', {'datos': datos, 'perfil': perfil})

def garage(request):
    perfil = get_active_profile()
    datos = VentaGarage.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
    return render(request, 'garage.html', {'datos': datos, 'perfil': perfil})

# --- FUNCIÓN DE EXPORTACIÓN A PDF CONSOLIDADO ---

def exportar_cv_completo(request):
    perfil = get_active_profile()
    
    # Recopilación de todos los datos para el template
    context = {
        'perfil': perfil,
        'experiencias': ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'cursos': CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'reconocimientos': Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'academicos': ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
        'laborales': ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True),
    }

    # 1. Generar la hoja principal (CV en formato texto/diseño)
    template = get_template('cv_pdf_maestro.html')
    html = template.render(context)
    pdf_texto = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=pdf_texto)

    # 2. Inicializar el unidor de PDFs (Merger)
    merger = PdfMerger()
    pdf_texto.seek(0)
    merger.append(pdf_texto)

    # 3. Adjuntar certificados físicos (Solo si son archivos PDF existentes)
    # Lista de categorías que tienen campo 'rutacertificado'
    categorias_con_pdf = [
        context['experiencias'],
        context['cursos'],
        context['reconocimientos']
    ]

    for categoria in categorias_con_pdf:
        for item in categoria:
            if item.rutacertificado:
                # Verificamos que sea un PDF y que el archivo exista en el disco
                nombre_archivo = item.rutacertificado.name.lower()
                if nombre_archivo.endswith('.pdf'):
                    try:
                        ruta_fisica = item.rutacertificado.path
                        if os.path.exists(ruta_fisica):
                            merger.append(ruta_fisica)
                    except Exception as e:
                        print(f"No se pudo adjuntar el archivo: {e}")
                        continue

    # 4. Construir el archivo final
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    # 5. Retornar el PDF al navegador
    response = HttpResponse(output.read(), content_type='application/pdf')
    filename = f"Portafolio_{perfil.apellidos}_{perfil.nombres}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response