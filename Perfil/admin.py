from django.contrib import admin
from .models import (
    DatosPersonales, ExperienciaLaboral, Reconocimientos, 
    CursosRealizados, ProductosAcademicos, ProductosLaborales, VentaGarage
)

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'numerocedula', 'email_contacto')
    fields = (
        'idperfil', 'fotoperfil', 'archivocv', 
        'nombres', 'apellidos', 'descripcionperfil', 
        'email_contacto', 'telefonofijo', 'telefonoconvencional',
        'numerocedula', 'nacionalidad', 'fechanacimiento', 'lugarnacimiento',
        'sexo', 'estadocivil', 'licenciaconducir',
        'direcciondomiciliaria', 'direcciontrabajo', 'sitioweb', 'perfilactivo'
    )
    
@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = ('cargodesempenado', 'nombrempresa', 'fechainiciogestion', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront', 'nombrempresa')

@admin.register(Reconocimientos)
class ReconocimientosAdmin(admin.ModelAdmin):
    list_display = ('descripcionreconocimiento', 'tiporeconocimiento', 'entidadpatrocinadora')
    list_filter = ('tiporeconocimiento',)

@admin.register(CursosRealizados)
class CursosRealizadosAdmin(admin.ModelAdmin):
    list_display = ('nombrecurso', 'entidadpatrocinadora', 'totalhoras')

@admin.register(ProductosAcademicos)
class ProductosAcademicosAdmin(admin.ModelAdmin):
    list_display = ('nombrerecurso', 'clasificador', 'activarparaqueseveaenfront')

@admin.register(ProductosLaborales)
class ProductosLaboralesAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'fechaproducto', 'activarparaqueseveaenfront')

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'valordelbien', 'estadoproducto', 'activarparaqueseveaenfront')
    list_filter = ('estadoproducto', 'activarparaqueseveaenfront')