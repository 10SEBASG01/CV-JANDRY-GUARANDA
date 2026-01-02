from django.db import models

from django.db import models

class DatosPersonales(models.Model):
    idperfil = models.IntegerField(primary_key=True)
    fotoperfil = models.ImageField(upload_to='perfil/', null=True, blank=True)
    email_contacto = models.EmailField(max_length=100, null=True, blank=True)
    archivocv = models.FileField(upload_to='cv/', null=True, blank=True)
    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.IntegerField()
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)
    fechanacimiento = models.DateField()
    numerocedula = models.CharField(max_length=10, unique=True)
    sexo_choices = [('H', 'Hombre'), ('M', 'Mujer')]
    sexo = models.CharField(max_length=1, choices=sexo_choices)
    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        verbose_name_plural = "Datos Personales"


class ExperienciaLaboral(models.Model):
    idexperiencilaboral = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50)
    emailempresa = models.EmailField(max_length=100)
    sitiowebempresa = models.URLField(max_length=100, blank=True, null=True)
    nombrecontactoempresarial = models.CharField(max_length=100)
    telefonocontactoempresarial = models.CharField(max_length=60)
    fechainiciogestion = models.DateField()
    fechafingestion = models.DateField(blank=True, null=True)
    descripcionfunciones = models.TextField(max_length=500)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to='certificados/experiencia/', blank=True, null=True)

    def __str__(self):
        return f"{self.cargodesempenado} en {self.nombrempresa}"

    class Meta:
        ordering = ['-fechainiciogestion']

class Reconocimientos(models.Model):
    TIPO_CHOICES = [('Académico', 'Académico'), ('Público', 'Público'), ('Privado', 'Privado')]
    idreconocimiento = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES)
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100)
    telefonocontactoauspicia = models.CharField(max_length=60)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to='reconocimientos/', null=True, blank=True)
    archivo_recurso = models.FileField(upload_to='recursos_cursos/', null=True, blank=True)

    def __str__(self):
        return self.descripcionreconocimiento

class CursosRealizados(models.Model):
    idcursorealizado = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    totalhoras = models.IntegerField()
    descripcioncurso = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100)
    telefonocontactoauspicia = models.CharField(max_length=60)
    emailempresapatrocinadora = models.EmailField(max_length=60)
    idcursorealizado = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    totalhoras = models.IntegerField()
    descripcioncurso = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100)
    telefonocontactoauspicia = models.CharField(max_length=60)
    emailempresapatrocinadora = models.EmailField(max_length=60)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to='certificados/cursos/', blank=True, null=True)
    archivo_extra = models.FileField(upload_to='extras_reconocimientos/', null=True, blank=True)

    def __str__(self):
        return self.nombrecurso

class ProductosAcademicos(models.Model):
    idproductoacademico = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombrerecurso = models.CharField(max_length=100)
    clasificador = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    def __str__(self):
        return self.nombrerecurso

class ProductosLaborales(models.Model):
    idproductoslaborales = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=100)
    fechaproducto = models.DateField()
    descripcion = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreproducto

class VentaGarage(models.Model):
    ESTADO_CHOICES = [('Bueno', 'Bueno'), ('Regular', 'Regular')]
    idventagarage = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=100)
    estadoproducto = models.CharField(max_length=40, choices=ESTADO_CHOICES)
    descripcion = models.CharField(max_length=100)
    valordelbien = models.DecimalField(max_digits=5, decimal_places=2)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    documento_interes = models.FileField(upload_to='garage/documentos/', null=True, blank=True,
    verbose_name="Documento Adicional (PDF/Foto)"
    )

    def __str__(self):
        return f"{self.nombreproducto} - ${self.valordelbien}"