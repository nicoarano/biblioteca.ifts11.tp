from django.db import models
from django.utils import timezone

class Libro(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    anio_publicacion = models.IntegerField()
    cantidad_total = models.IntegerField()
    cantidad_disponible = models.IntegerField()

    def prestar_ejemplar(self) -> bool:
        if self.cantidad_disponible > 0:
            self.cantidad_disponible -= 1
            self.save()
            return True
        return False

    def devolver_ejemplar(self):
        if self.cantidad_disponible < self.cantidad_total:
            self.cantidad_disponible += 1
            self.save()

    def __str__(self):
        return f"'{self.titulo}' de {self.autor} [Disponibles: {self.cantidad_disponible}/{self.cantidad_total}]"


class Socio(models.Model):
    numero_socio = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    estado = models.CharField(max_length=20, default="Activo")

    def esta_activo(self) -> bool:
        return self.estado == "Activo"

    def __str__(self):
        return f"Socio N° {self.numero_socio}: {self.nombre} {self.apellido} ({self.estado})"


class Reserva(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Retirada', 'Retirada'),
        ('Cancelada', 'Cancelada'),
        ('Finalizada', 'Finalizada'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    def cancelar(self):
        """Una reserva solo se puede cancelar si está pendiente. Devuelve el ejemplar."""
        if self.estado == 'Pendiente':
            self.estado = 'Cancelada'
            self.libro.devolver_ejemplar()
            self.save()
            return True
        return False

    def retirar(self):
        """Pasa la reserva de Pendiente a Retirada."""
        if self.estado == 'Pendiente':
            self.estado = 'Retirada'
            self.save()
            return True
        return False

    def finalizar(self):
        """Pasa la reserva a Finalizada al devolver el libro y repone el ejemplar."""
        if self.estado == 'Retirada':
            self.estado = 'Finalizada'
            self.libro.devolver_ejemplar()
            self.save()
            return True
        return False

    def __str__(self):
        fecha_fmt = self.fecha_reserva.strftime("%d/%m/%Y %H:%M")
        return f"ID Res: {self.id} | [{self.estado}] | Fecha: {fecha_fmt} - Socio: {self.socio.nombre} {self.socio.apellido} | Libro: {self.libro.titulo} | ISBN: {self.libro.isbn}"