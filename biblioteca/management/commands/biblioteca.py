from django.core.management.base import BaseCommand
from django.db import models
from biblioteca.models import Libro, Socio, Reserva

class Command(BaseCommand):
    help = "Inicia el sistema de biblioteca por consola"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("¡Sistema de biblioteca iniciado con éxito!"))

        while True:
            print("\n=============================")
            print("      BIBLIOTECA")
            print("=============================")
            print("1. Listar libros")
            print("2. Registrar libro")
            print("3. Editar libro")
            print("4. Buscar libro (ISBN, Título o Autor)")
            print("5. Registrar socio")
            print("6. Cambiar estado de socio (Activo/Inactivo)")
            print("7. Listar socios")
            print("8. Realizar reserva")
            print("9. Cancelar reserva")
            print("10. Retirar libro reservado")
            print("11. Devolver libro")
            print("12. Listar todas las reservas")
            print("13. Listar reservas de un socio")
            print("0. Salir")
            
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                libros = Libro.objects.all()
                if not libros:
                    print("\nNo hay libros registrados.")
                else:
                    print("\n--- LISTA DE LIBROS ---")
                    for libro in libros:
                        print(libro)

            elif opcion == "2":
                print("\n--- REGISTRAR NUEVO LIBRO ---")
                titulo = input("Título: ")
                autor = input("Autor: ")
                isbn = input("ISBN: ")
                anio = int(input("Año de publicación: "))
                cantidad = int(input("Cantidad de ejemplares: "))
                
                try:
                    Libro.objects.create(
                        titulo=titulo, autor=autor, isbn=isbn,
                        anio_publicacion=anio, cantidad_total=cantidad,
                        cantidad_disponible=cantidad
                    )
                    print("¡Libro registrado correctamente!")
                except Exception as e:
                    print(f"[Error] No se pudo registrar el libro (verifique si el ISBN ya existe).")

            elif opcion == "3":
                print("\n--- EDITAR LIBRO ---")
                isbn_búsqueda = input("Ingrese el ISBN del libro a editar: ")
                try:
                    libro = Libro.objects.get(isbn=isbn_búsqueda)
                    print(f"Editando: {libro.titulo}")
                    
                    nuevo_titulo = input(f"Nuevo título [{libro.titulo}]: ") or libro.titulo
                    nuevo_autor = input(f"Nuevo autor [{libro.autor}]: ") or libro.autor
                    nuevo_isbn = input(f"Nuevo ISBN [{libro.isbn}]: ") or libro.isbn
                    
                    libro.titulo = nuevo_titulo
                    libro.autor = nuevo_autor
                    libro.isbn = nuevo_isbn
                    libro.save()
                    print("¡Libro actualizado con éxito!")
                except Libro.DoesNotExist:
                    print("[Error] No se encontró un libro con ese ISBN.")

            elif opcion == "4":
                print("\n--- BUSCAR LIBRO ---")
                criterio = input("Ingrese ISBN, Título o Autor a buscar: ").strip()
                # Coincidencia exacta por ISBN o parcial (icontains) por título o autor
                libros = Libro.objects.filter(
                    models.Q(isbn__exact=criterio) |
                    models.Q(titulo__icontains=criterio) |
                    models.Q(autor__icontains=criterio)
                )
                if libros.exists():
                    print(f"\nSe encontraron {libros.count()} libro(s):")
                    for l in libros:
                        print(l)
                else:
                    print("[Información] No se encontraron libros que coincidan con la búsqueda.")

            elif opcion == "5":
                print("\n--- REGISTRAR NUEVO SOCIO ---")
                num_socio = int(input("Número de socio: "))
                nombre = input("Nombre: ")
                apellido = input("Apellido: ")
                dni = input("DNI: ")
                email = input("Email: ")
                
                try:
                    Socio.objects.create(
                        numero_socio=num_socio, nombre=nombre,
                        apellido=apellido, dni=dni, email=email
                    )
                    print("¡Socio registrado correctamente!")
                except Exception:
                    print("[Error] No se pudo registrar el socio (verifique DNI o Número de socio duplicado).")

            elif opcion == "6":
                print("\n--- CAMBIAR ESTADO DE SOCIO ---")
                num_socio = int(input("Ingrese el número de socio: "))
                try:
                    socio = Socio.objects.get(numero_socio=num_socio)
                    print(f"Estado actual de {socio.nombre} {socio.apellido}: {socio.estado}")
                    nuevo_estado = input("Ingrese nuevo estado (1: Activo, 2: Inactivo): ")
                    if nuevo_estado == "1":
                        socio.estado = "Activo"
                    elif nuevo_estado == "2":
                        socio.estado = "Inactivo"
                    else:
                        print("Opción no válida. No se realizaron cambios.")
                        continue
                    socio.save()
                    print(f"¡Estado del socio actualizado a '{socio.estado}'!")
                except Socio.DoesNotExist:
                    print("[Error] No existe un socio con ese número.")

            elif opcion == "7":
                socios = Socio.objects.all()
                if not socios:
                    print("\nNo hay socios registrados.")
                else:
                    print("\n--- LISTA DE SOCIOS ---")
                    for socio in socios:
                        print(socio)

            elif opcion == "8":
                print("\n--- REALIZAR RESERVA ---")
                num_socio = int(input("Ingrese el número de socio: "))
                isbn_libro = input("Ingrese el ISBN del libro: ")

                try:
                    socio = Socio.objects.get(numero_socio=num_socio)
                    libro = Libro.objects.get(isbn=isbn_libro)

                    # Regla de negocio 1: Socio activo
                    if not socio.esta_activo():
                        print("[Error] El socio está inactivo y no puede reservar.")
                    # Regla de negocio 2: Ejemplares disponibles
                    elif libro.cantidad_disponible <= 0:
                        print("[Error] No hay ejemplares disponibles de este libro.")
                    else:
                        # Regla de negocio 3: El socio no debe tener reserva activa previa del mismo libro
                        reserva_activa = Reserva.objects.filter(
                            socio=socio, 
                            libro=libro, 
                            estado__in=['Pendiente', 'Retirada']
                        ).exists()

                        if reserva_activa:
                            print("[Error] El socio ya posee una reserva activa o pendiente de este libro.")
                        else:
                            libro.prestar_ejemplar()
                            Reserva.objects.create(socio=socio, libro=libro)
                            print("¡Reserva realizada con éxito!")

                except Socio.DoesNotExist:
                    print("[Error] No se encontró un socio con ese número.")
                except Libro.DoesNotExist:
                    print("[Error] No se encontró un libro con ese ISBN.")

            elif opcion == "9":
                print("\n--- CANCELAR RESERVA ---")
                id_reserva = int(input("Ingrese el ID de la reserva a cancelar: "))
                try:
                    reserva = Reserva.objects.get(id=id_reserva)
                    if reserva.cancelar():
                        print("¡Reserva cancelada con éxito y ejemplar devuelto al stock!")
                    else:
                        print("[Error] La reserva no se puede cancelar (debe estar en estado Pendiente).")
                except Reserva.DoesNotExist:
                    print("[Error] No existe una reserva con ese ID.")

            elif opcion == "10":
                print("\n--- RETIRAR LIBRO ---")
                id_reserva = int(input("Ingrese el ID de la reserva a retirar: "))
                try:
                    reserva = Reserva.objects.get(id=id_reserva)
                    if reserva.retirar():
                        print("¡Libro retirado con éxito! Estado de reserva: Retirada.")
                    else:
                        print("[Error] No se puede retirar (la reserva debe estar Pendiente).")
                except Reserva.DoesNotExist:
                    print("[Error] No existe una reserva con ese ID.")

            elif opcion == "11":
                print("\n--- DEVOLVER LIBRO ---")
                id_reserva = int(input("Ingrese el ID de la reserva a devolver: "))
                try:
                    reserva = Reserva.objects.get(id=id_reserva)
                    if reserva.finalizar():
                        print("¡Libro devuelto con éxito! Reserva Finalizada y stock repuesto.")
                    else:
                        print("[Error] No se puede devolver (el libro debió estar previamente Retirado).")
                except Reserva.DoesNotExist:
                    print("[Error] No existe una reserva con ese ID.")

            elif opcion == "12":
                reservas = Reserva.objects.all()
                if not reservas:
                    print("\nNo hay reservas registradas.")
                else:
                    print("\n--- LISTA DE RESERVAS ---")
                    for r in reservas:
                        print(r)

            elif opcion == "13":
                print("\n--- LISTAR RESERVAS DE UN SOCIO ---")
                num_socio = int(input("Ingrese el número de socio: "))
                try:
                    socio = Socio.objects.get(numero_socio=num_socio)
                    reservas = Reserva.objects.filter(socio=socio)
                    if not reservas.exists():
                        print(f"\nEl socio {socio.nombre} {socio.apellido} no tiene reservas registradas.")
                    else:
                        print(f"\n--- RESERVAS DEL SOCIO {socio.nombre} {socio.apellido} ---")
                        for r in reservas:
                            print(r)
                except Socio.DoesNotExist:
                    print("[Error] No se encontró un socio con ese número.")

            elif opcion == "0":
                print("\nSaliendo del sistema. ¡Hasta luego!")
                break
            else:
                print("\n[Error] Opción inválida.")