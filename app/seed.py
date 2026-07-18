"""Carga de datos de ejemplo basada en el manual AFF y el chat real de Halcones.

Es idempotente: si ya existe el usuario administrador, no vuelve a sembrar.
"""
import os
import shutil
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from .config import settings
from .models import (
    User, Role, Course, CourseLevel, MediaResource, MediaType,
    Enrollment, EnrollmentStatus, LevelProgress, LevelStatus,
    Payment, PaymentMethod, PaymentConcept,
    InstructorPayment, InstructorPayConcept,
    Aircraft, JumpDay, Load, LoadStatus, LoadSlot, SlotRole,
    NotificationRule, NotificationType,
)
from .security import hash_password

SEED_ASSETS = os.path.join(os.path.dirname(__file__), "seed_assets")


# --------------------------------------------------------------------------- #
def _copy_manual() -> str | None:
    """Copia el manual PDF a la carpeta de uploads y devuelve su ruta relativa."""
    src = os.path.join(SEED_ASSETS, "MANUALAFF123.pdf")
    if not os.path.exists(src):
        return None
    dest_dir = os.path.join(settings.upload_dir, "curso-1")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "MANUALAFF123.pdf")
    if not os.path.exists(dest):
        shutil.copy(src, dest)
    return "curso-1/MANUALAFF123.pdf"


# --------------------------------------------------------------------------- #
NIVELES_AFF = [
    ("Nivel 1 · Estabilidad asistida",
     "Primer salto desde 10.000 ft con DOS instructores. Objetivo: mantener el arco, "
     "círculo de consciencia (horizonte, altímetro) y 3 prácticas de apertura. "
     "Los instructores asisten la estabilidad en todo momento."),
    ("Nivel 2 · Estabilidad y consciencia",
     "Con dos instructores. Se refuerza la posición de caída libre, el control de altura "
     "y se realizan 2 prácticas de apertura. Se busca estabilidad sin correcciones."),
    ("Nivel 3 · Liberación / vuelo con un instructor",
     "Transición de dos a un instructor. Salida estable, 1 práctica de apertura y "
     "demostración de estabilidad autónoma. Los instructores sueltan al alumno en el aire."),
    ("Nivel 4 · Giros de 90° y control de rumbo",
     "Con un instructor. El alumno aprende a mantener el rumbo y ejecutar giros suaves "
     "de 90°, recuperando siempre la referencia y la estabilidad."),
    ("Nivel 5 · Giros de 360°",
     "Giros completos de 360° a izquierda y derecha, con recuperación de estabilidad "
     "y control preciso de altura durante las maniobras."),
    ("Nivel 6 · Salida sin asistencia y volteretas",
     "Salida del avión sin asistencia del instructor, volteretas hacia adelante/atrás "
     "y recuperación de la posición estable (arco)."),
    ("Nivel 7 · Track y autonomía de vuelo",
     "Desplazamiento horizontal (track), consciencia de tráfico y demostración final. "
     "Al aprobar, el alumno tiene autonomía de vuelo y control del cuerpo en caída libre."),
]

INCLUYE_AFF = """Manual instructivo de AFF
Clases teóricas y prácticas en tierra
7 niveles o saltos en caída libre con instructor profesional
Alquiler de equipos: paracaídas, overol de salto, altímetro, casco, gafas y radio
Bitácora o libro de salto
Videos de todos los saltos"""

REQUISITOS_AFF = """Ser mayor de edad
Documento de identidad (cédula de ciudadanía)
Certificado de afiliación a EPS vigente
Exámenes médicos ocupacionales
Peso dentro del rango permitido por el equipo
Registrar un contacto de emergencia"""

DESCRIPCION_AFF = (
    "¡Felicidades por elegir el curso AFF como iniciación al paracaidismo! El AFF "
    "(Caída Libre Acelerada) es el método más extendido entre las escuelas del mundo. "
    "Desarrollado en EE.UU. a principios de los ochenta, está diseñado para una "
    "enseñanza individual y personalizada que, tras un corto periodo de entrenamiento, "
    "deja al alumno preparado para saltar por sí mismo con total seguridad.\n\n"
    "El alumno salta desde 10.000 ft acompañado de instructores, con cerca de 30 segundos "
    "de caída libre por salto. Progresa a lo largo de 7 niveles a su propio ritmo, "
    "aprendiendo a volar estable, recuperar la estabilidad, hacer giros de 360°, "
    "volteretas y desplazamiento (track). Cada salto se graba en video y se analiza "
    "con el instructor. La zona de salto es Braaap Park, vía Rozo–Cali, a 15 minutos "
    "del aeropuerto Alfonso Bonilla Aragón."
)


# --------------------------------------------------------------------------- #
def seed(db: Session):
    if db.query(User).filter(User.email == "admin@halcones.co").first():
        return  # ya sembrado

    # ---------------- Usuarios ----------------
    admin = User(nombre="Administración Halcones", email="admin@halcones.co",
                 password_hash=hash_password("admin123"), role=Role.admin,
                 telefono="+57 301 6265503", activo=True)

    instructor = User(nombre="Camilo Restrepo", email="instructor@halcones.co",
                      password_hash=hash_password("instructor123"), role=Role.instructor,
                      telefono="+57 301 6265503", cedula="94123456",
                      licencia="Instructor AFF certificado",
                      especialidad="AFF · Tándem · Cámara", activo=True)

    instructor2 = User(nombre="Laura Marín", email="laura@halcones.co",
                       password_hash=hash_password("instructor123"), role=Role.instructor,
                       telefono="+57 300 7654321", cedula="66754321",
                       licencia="Instructora AFF / Tándem",
                       especialidad="AFF · Tándem", activo=True)

    # Estudiante real del chat
    julian = User(
        nombre="Julián Andrés Castaño Espinosa", email="julian@example.com",
        password_hash=hash_password("estudiante123"), role=Role.estudiante,
        telefono="3188468892", cedula="1144194156", peso_kg=74,
        eps="EPS SURA", direccion="Cra 94A # 2A-80, Meléndez, Cali",
        contacto_emergencia_nombre="Jesús Cuesta",
        contacto_emergencia_telefono="317 5810029", activo=True)

    otros_estudiantes = [
        User(nombre="María Fernanda López", email="maria@example.com",
             password_hash=hash_password("estudiante123"), role=Role.estudiante,
             telefono="3105551122", cedula="1130456789", peso_kg=58,
             eps="Coomeva EPS", direccion="Cll 5 # 38-20, Cali",
             contacto_emergencia_nombre="Diana López",
             contacto_emergencia_telefono="311 2223344", activo=True),
        User(nombre="Andrés Ramírez Vélez", email="andres@example.com",
             password_hash=hash_password("estudiante123"), role=Role.estudiante,
             telefono="3124445566", cedula="16789012", peso_kg=82,
             eps="Sanitas EPS", direccion="Av 6N # 28-100, Cali",
             contacto_emergencia_nombre="Paula Vélez",
             contacto_emergencia_telefono="315 6667788", activo=True),
        User(nombre="Camila Torres Ruiz", email="camila@example.com",
             password_hash=hash_password("estudiante123"), role=Role.estudiante,
             telefono="3016667788", cedula="1144778899", peso_kg=61,
             eps="Nueva EPS", direccion="Cra 66 # 13-45, Cali",
             contacto_emergencia_nombre="Jorge Torres",
             contacto_emergencia_telefono="300 1112233", activo=True),
        User(nombre="Sebastián Gómez Arango", email="sebastian@example.com",
             password_hash=hash_password("estudiante123"), role=Role.estudiante,
             telefono="3009998877", cedula="1085223344", peso_kg=76,
             eps="EPS SURA", direccion="Cll 9 # 50-15, Cali",
             contacto_emergencia_nombre="Marcela Arango",
             contacto_emergencia_telefono="318 4445566", activo=True),
    ]

    db.add_all([admin, instructor, instructor2, julian, *otros_estudiantes])
    db.flush()

    # ---------------- Curso AFF ----------------
    aff = Course(
        codigo="AFF-01", nombre="Curso AFF · Caída Libre Acelerada", modalidad="AFF",
        resumen="El curso para iniciarse como deportista en el paracaidismo. "
                "7 niveles para lograr autonomía de vuelo y control del cuerpo en caída libre.",
        descripcion=DESCRIPCION_AFF, incluye=INCLUYE_AFF, requisitos=REQUISITOS_AFF,
        niveles_total=7, altura_salto_ft=10000,
        duracion="7 saltos + teoría (a tu ritmo)",
        precio=Decimal("6333333"), reserva_minima=Decimal("2000000"),
        moneda="COP", activo=True, destacado=True, color="#7E0704",
    )
    db.add(aff)
    db.flush()

    for i, (titulo, desc) in enumerate(NIVELES_AFF, start=1):
        db.add(CourseLevel(course_id=aff.id, numero=i, titulo=titulo,
                           descripcion=desc, es_teorico=False))
    db.flush()

    # Media del curso AFF
    manual_rel = _copy_manual()
    if manual_rel:
        db.add(MediaResource(course_id=aff.id, tipo=MediaType.manual,
                             titulo="Manual de Instrucción AFF (PDF)",
                             descripcion="Manual completo del curso de Caída Libre "
                                         "Acelerada — Categoría A.",
                             archivo=manual_rel, orden=0))
    db.add(MediaResource(course_id=aff.id, tipo=MediaType.video,
                         titulo="Video introductorio del curso AFF",
                         descripcion="Teoría inicial: equipo, posición de caída libre "
                                     "y procedimientos.",
                         url="https://youtu.be/xNAxRu28zak", orden=1))
    db.add(MediaResource(course_id=aff.id, tipo=MediaType.video,
                         titulo="Videos de tus saltos (enlace de descarga)",
                         descripcion="Grabaciones de los saltos realizadas por el "
                                     "instructor para análisis posterior.",
                         url="https://fromsmash.com/-1DHBX9jwO-et", orden=2))

    # ---------------- Curso Tándem (adicional, informativo) ----------------
    tandem = Course(
        codigo="TAN-01", nombre="Salto Tándem", modalidad="Tándem",
        resumen="Tu primera experiencia de caída libre saltando junto a un instructor "
                "certificado. Sin curso previo.",
        descripcion="El salto tándem es la forma más sencilla de vivir el paracaidismo: "
                    "vas firmemente asegurado al arnés de un instructor que controla todo "
                    "el salto. Ideal para tu primera vez desde ~10.000 ft.",
        incluye="Instructor tándem certificado\nEquipo completo\nBriefing de seguridad\n"
                "Opción de video y fotos",
        requisitos="Ser mayor de edad (o autorización de acudiente)\nPeso máximo 100 kg\n"
                   "No tener contraindicaciones médicas",
        niveles_total=1, altura_salto_ft=10000, duracion="Media jornada",
        precio=Decimal("850000"), reserva_minima=Decimal("300000"),
        moneda="COP", activo=True, destacado=False, color="#A93037",
    )
    db.add(tandem)
    db.flush()
    db.add(CourseLevel(course_id=tandem.id, numero=1, titulo="Salto Tándem",
                       descripcion="Salto en caída libre asegurado al instructor.",
                       es_teorico=False))

    # ---------------- Aviones ----------------
    cessna = Aircraft(matricula="HK-4512", modelo="Cessna 206", capacidad=5, activo=True,
                      notas="Avión principal de operación en la zona.")
    cessna2 = Aircraft(matricula="HK-2890", modelo="Cessna 182", capacidad=4, activo=True)
    db.add_all([cessna, cessna2])
    db.flush()

    # ---------------- Inscripciones y bitácora ----------------
    # Julián — inscrito, con reserva pagada y primeros niveles
    enr_julian = Enrollment(
        student_id=julian.id, course_id=aff.id, instructor_id=instructor.id,
        precio_acordado=Decimal("6333333"), fecha_inscripcion=date(2026, 7, 2),
        estado=EnrollmentStatus.activo, nivel_actual=1,
        notas="Reserva confirmada por transferencia el 2/7. Recibe teoría los fines de "
              "semana en la zona.")
    db.add(enr_julian)
    db.flush()

    niveles_aff = db.query(CourseLevel).filter_by(course_id=aff.id).order_by(
        CourseLevel.numero).all()
    for idx, lvl in enumerate(niveles_aff):
        if idx == 0:
            estado = LevelStatus.aprobado
            fecha = date(2026, 7, 6)
            nota = "Primer salto realizado. Buen arco, cumplió el círculo de consciencia."
            video = "https://fromsmash.com/-1DHBX9jwO-et"
        elif idx == 1:
            estado = LevelStatus.en_progreso
            fecha = None
            nota = "Programado para la próxima jornada."
            video = None
        else:
            estado = LevelStatus.pendiente
            fecha = None
            nota = None
            video = None
        db.add(LevelProgress(enrollment_id=enr_julian.id, level_id=lvl.id,
                             estado=estado, fecha=fecha, nota=nota, video_url=video,
                             altura_ft=10000 if estado != LevelStatus.pendiente else None,
                             instructor_id=instructor.id if estado != LevelStatus.pendiente else None))

    # Pagos de Julián: reserva + abono
    db.add(Payment(enrollment_id=enr_julian.id, fecha=date(2026, 7, 2),
                   monto=Decimal("2000000"), metodo=PaymentMethod.transferencia,
                   concepto=PaymentConcept.reserva, referencia="Transf. Bancolombia",
                   nota="Reserva del curso", registrado_por_id=admin.id))
    db.add(Payment(enrollment_id=enr_julian.id, fecha=date(2026, 7, 6),
                   monto=Decimal("1000000"), metodo=PaymentMethod.link,
                   concepto=PaymentConcept.abono, referencia="Link de pago",
                   nota="Abono tras primer salto", registrado_por_id=instructor.id))

    # Otros estudiantes con distintos estados
    def enroll_full(student, curso, instr, pagos, niveles_aprobados, estado_enr,
                    fecha_ins):
        e = Enrollment(student_id=student.id, course_id=curso.id,
                       instructor_id=instr.id if instr else None,
                       precio_acordado=curso.precio, fecha_inscripcion=fecha_ins,
                       estado=estado_enr, nivel_actual=niveles_aprobados)
        db.add(e)
        db.flush()
        lvls = db.query(CourseLevel).filter_by(course_id=curso.id).order_by(
            CourseLevel.numero).all()
        for i2, lvl in enumerate(lvls):
            if i2 < niveles_aprobados:
                st = LevelStatus.aprobado
            elif i2 == niveles_aprobados and estado_enr == EnrollmentStatus.activo:
                st = LevelStatus.en_progreso
            else:
                st = LevelStatus.pendiente
            db.add(LevelProgress(enrollment_id=e.id, level_id=lvl.id, estado=st,
                                 fecha=fecha_ins if st == LevelStatus.aprobado else None,
                                 instructor_id=instr.id if instr and st == LevelStatus.aprobado else None,
                                 altura_ft=10000 if st == LevelStatus.aprobado else None))
        for (monto, metodo, concepto, f) in pagos:
            db.add(Payment(enrollment_id=e.id, fecha=f, monto=Decimal(str(monto)),
                           metodo=metodo, concepto=concepto, registrado_por_id=admin.id))
        return e

    maria, andres, camila, sebastian = otros_estudiantes
    enroll_full(maria, aff, instructor2,
                [(6333333, PaymentMethod.transferencia, PaymentConcept.saldo, date(2026, 5, 10))],
                7, EnrollmentStatus.completado, date(2026, 4, 1))
    enroll_full(andres, aff, instructor,
                [(2000000, PaymentMethod.consignacion, PaymentConcept.reserva, date(2026, 6, 20)),
                 (2000000, PaymentMethod.efectivo, PaymentConcept.abono, date(2026, 7, 1))],
                3, EnrollmentStatus.activo, date(2026, 6, 20))
    enroll_full(camila, aff, instructor2,
                [(2000000, PaymentMethod.link, PaymentConcept.reserva, date(2026, 7, 10))],
                0, EnrollmentStatus.activo, date(2026, 7, 10))
    # Sebastián solo en tándem
    enroll_full(sebastian, tandem, instructor,
                [(300000, PaymentMethod.transferencia, PaymentConcept.reserva, date(2026, 7, 12))],
                0, EnrollmentStatus.activo, date(2026, 7, 12))

    # ---------------- Jornadas de salto (manifiesto) ----------------
    # Jornada pasada (domingo 6/7): Julián hizo su nivel 1
    jd_pasada = JumpDay(fecha=date(2026, 7, 6), estado="cerrada",
                        clima="Despejado", notas="Jornada regular de domingo.")
    db.add(jd_pasada)
    db.flush()
    load_p1 = Load(jump_day_id=jd_pasada.id, aircraft_id=cessna.id, numero=1,
                   hora_estimada="12:30", altura_ft=10000, estado=LoadStatus.completado)
    db.add(load_p1)
    db.flush()
    db.add_all([
        LoadSlot(load_id=load_p1.id, person_id=julian.id, rol=SlotRole.alumno,
                 tipo_salto="AFF Nivel 1"),
        LoadSlot(load_id=load_p1.id, person_id=instructor.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 1"),
        LoadSlot(load_id=load_p1.id, person_id=instructor2.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 1"),
        LoadSlot(load_id=load_p1.id, person_id=None, person_nombre="Camarógrafo",
                 rol=SlotRole.camara, tipo_salto="Video del salto"),
    ])

    # Próxima jornada (domingo 19/7): varios vuelos
    jd_prox = JumpDay(fecha=date(2026, 7, 19), estado="programada",
                      clima="Pronóstico favorable",
                      notas="2 vuelos entre 9:00 y 10:30. Julián inicia hacia el mediodía "
                            "(Nivel 2). Confirmar quién va en cada vuelo.")
    db.add(jd_prox)
    db.flush()

    load1 = Load(jump_day_id=jd_prox.id, aircraft_id=cessna.id, numero=1,
                 hora_estimada="09:00", altura_ft=10000, estado=LoadStatus.programado)
    load2 = Load(jump_day_id=jd_prox.id, aircraft_id=cessna2.id, numero=2,
                 hora_estimada="10:00", altura_ft=10000, estado=LoadStatus.programado)
    load3 = Load(jump_day_id=jd_prox.id, aircraft_id=cessna.id, numero=3,
                 hora_estimada="12:00", altura_ft=10000, estado=LoadStatus.programado)
    db.add_all([load1, load2, load3])
    db.flush()

    db.add_all([
        # Vuelo 1 — deportistas y un tándem
        LoadSlot(load_id=load1.id, person_id=andres.id, rol=SlotRole.alumno,
                 tipo_salto="AFF Nivel 4"),
        LoadSlot(load_id=load1.id, person_id=instructor.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 4"),
        LoadSlot(load_id=load1.id, person_id=sebastian.id, rol=SlotRole.tandem,
                 tipo_salto="Salto Tándem"),
        LoadSlot(load_id=load1.id, person_id=instructor2.id, rol=SlotRole.instructor,
                 tipo_salto="Tándem"),
        # Vuelo 2 — otra alumna
        LoadSlot(load_id=load2.id, person_id=camila.id, rol=SlotRole.alumno,
                 tipo_salto="AFF Nivel 1"),
        LoadSlot(load_id=load2.id, person_id=instructor.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 1"),
        LoadSlot(load_id=load2.id, person_id=instructor2.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 1"),
        # Vuelo 3 — Julián nivel 2 (mediodía)
        LoadSlot(load_id=load3.id, person_id=julian.id, rol=SlotRole.alumno,
                 tipo_salto="AFF Nivel 2"),
        LoadSlot(load_id=load3.id, person_id=instructor.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 2"),
        LoadSlot(load_id=load3.id, person_id=instructor2.id, rol=SlotRole.instructor,
                 tipo_salto="AFF Nivel 2"),
    ])

    # ---------------- Nómina de instructores (pagos a instructores) ----------------
    db.add_all([
        InstructorPayment(instructor_id=instructor.id, fecha=date(2026, 7, 6),
                          monto=Decimal("240000"), concepto=InstructorPayConcept.por_salto,
                          metodo=PaymentMethod.transferencia, saltos=3,
                          nota="Saltos jornada del 6/7", registrado_por_id=admin.id),
        InstructorPayment(instructor_id=instructor.id, fecha=date(2026, 6, 30),
                          monto=Decimal("1200000"), concepto=InstructorPayConcept.salario,
                          metodo=PaymentMethod.transferencia,
                          nota="Salario junio", registrado_por_id=admin.id),
        InstructorPayment(instructor_id=instructor2.id, fecha=date(2026, 7, 6),
                          monto=Decimal("160000"), concepto=InstructorPayConcept.por_salto,
                          metodo=PaymentMethod.efectivo, saltos=2,
                          nota="Saltos jornada del 6/7", registrado_por_id=admin.id),
        InstructorPayment(instructor_id=instructor2.id, fecha=date(2026, 6, 30),
                          monto=Decimal("900000"), concepto=InstructorPayConcept.salario,
                          metodo=PaymentMethod.transferencia,
                          nota="Salario junio", registrado_por_id=admin.id),
    ])

    # ---------------- Saltador de una sola vez (para la oferta de curso) -------- #
    valentina = User(
        nombre="Valentina Ríos", email="valentina@example.com",
        password_hash=hash_password("estudiante123"), role=Role.estudiante,
        telefono="3145559090", cedula="1112223334", peso_kg=55,
        eps="EPS SURA", direccion="Cll 44 # 5-30, Cali", activo=True)
    db.add(valentina)
    db.flush()
    jd_tandem = JumpDay(fecha=date(2026, 5, 4), estado="cerrada", clima="Despejado",
                        notas="Jornada de tándems.")
    db.add(jd_tandem)
    db.flush()
    load_t = Load(jump_day_id=jd_tandem.id, aircraft_id=cessna.id, numero=1,
                  hora_estimada="10:00", altura_ft=10000, estado=LoadStatus.completado)
    db.add(load_t)
    db.flush()
    db.add_all([
        LoadSlot(load_id=load_t.id, person_id=valentina.id, rol=SlotRole.tandem,
                 tipo_salto="Salto Tándem"),
        LoadSlot(load_id=load_t.id, person_id=instructor2.id, rol=SlotRole.instructor,
                 tipo_salto="Tándem"),
    ])

    # ---------------- Reglas de notificación (ejemplos) ---------------- #
    db.add(NotificationRule(
        nombre="Recordatorio de próximo salto",
        tipo=NotificationType.recordatorio_salto, activo=True,
        dias_antelacion=3, intervalo_dias=30, frecuencia="diaria",
        creada_por_id=admin.id,
        asunto="🪂 {nombre}, tu próximo salto es el {fecha_salto}",
        cuerpo=("Hola {nombre_completo},\n\n"
                "Te recordamos que tienes programado tu salto ({tipo_salto}) "
                "el {fecha_salto} a las {hora_salto}, en el vuelo {vuelo}.\n"
                "Zona: {zona}.\n\n"
                "Recuerda llegar con tiempo y con la teoría al día. ¡Nos vemos en el cielo!\n\n"
                "Halcones Paracaidismo")))
    db.add(NotificationRule(
        nombre="Oferta de curso a quienes saltaron una vez",
        tipo=NotificationType.oferta_curso, activo=True,
        dias_antelacion=2, intervalo_dias=30, frecuencia="semanal",
        creada_por_id=admin.id,
        asunto="🪂 {nombre}, ¿listo para volver a volar?",
        cuerpo=("Hola {nombre_completo},\n\n"
                "¡Sabemos que probaste la caída libre con nosotros y sentimos que el "
                "cielo te llama de nuevo! 🚀\n\n"
                "Da el siguiente paso con nuestro {curso}: 7 niveles para lograr "
                "autonomía de vuelo. Inversión: {precio} (reserva desde {reserva}).\n\n"
                "Escríbenos y coordinamos tu inicio. ¡Te esperamos!\n\n"
                "Halcones Paracaidismo")))

    db.commit()
