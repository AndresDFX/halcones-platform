"""Modelo de datos de la plataforma Halcones Paracaidismo.

Cubre los cuatro pilares del negocio:
  1. Cursos (informativo)      -> Course, CourseLevel, MediaResource
  2. Seguimiento estudiantes   -> User(StudentProfile), Enrollment, LevelProgress
  3. Finanzas                  -> Payment (+ balances calculados sobre Enrollment)
  4. Programación de saltos    -> Aircraft, JumpDay, Load, LoadSlot
"""
import enum
from datetime import datetime, date

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer,
    Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


# --------------------------------------------------------------------------- #
#  Enums
# --------------------------------------------------------------------------- #
class Role(str, enum.Enum):
    admin = "admin"
    instructor = "instructor"
    estudiante = "estudiante"


class EnrollmentStatus(str, enum.Enum):
    activo = "activo"
    completado = "completado"
    pausado = "pausado"
    cancelado = "cancelado"


class LevelStatus(str, enum.Enum):
    pendiente = "pendiente"
    en_progreso = "en_progreso"
    aprobado = "aprobado"
    repetir = "repetir"


class MediaType(str, enum.Enum):
    video = "video"
    manual = "manual"
    documento = "documento"


class PaymentMethod(str, enum.Enum):
    transferencia = "transferencia"
    consignacion = "consignacion"
    efectivo = "efectivo"
    link = "link"


class PaymentConcept(str, enum.Enum):
    reserva = "reserva"
    abono = "abono"
    saldo = "saldo"
    otro = "otro"


class InstructorPayConcept(str, enum.Enum):
    """Conceptos de pago HACIA el instructor (su compensación)."""
    por_salto = "por_salto"
    salario = "salario"
    bono = "bono"
    comision = "comision"
    otro = "otro"


class NotificationType(str, enum.Enum):
    recordatorio_salto = "recordatorio_salto"   # recordar próximo salto al estudiante
    oferta_curso = "oferta_curso"               # ofrecer curso a quien saltó una sola vez


class NotificationStatus(str, enum.Enum):
    pendiente = "pendiente"     # generada, aún no enviada
    enviado = "enviado"         # enviada por SMTP correctamente
    simulado = "simulado"       # SMTP no configurado: se registró pero no se envió
    error = "error"             # falló el envío


class LoadStatus(str, enum.Enum):
    programado = "programado"
    abordando = "abordando"
    en_vuelo = "en_vuelo"
    completado = "completado"
    cancelado = "cancelado"


class SlotRole(str, enum.Enum):
    alumno = "alumno"
    instructor = "instructor"
    camara = "camara"
    tandem = "tandem"
    deportista = "deportista"


# --------------------------------------------------------------------------- #
#  Usuarios
# --------------------------------------------------------------------------- #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(160), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.estudiante, index=True)
    telefono = Column(String(40))
    cedula = Column(String(40))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Datos específicos de estudiante (opcionales para otros roles)
    peso_kg = Column(Float)
    fecha_nacimiento = Column(Date)
    eps = Column(String(120))
    direccion = Column(String(255))
    contacto_emergencia_nombre = Column(String(160))
    contacto_emergencia_telefono = Column(String(40))
    # Datos de instructor
    licencia = Column(String(80))          # p.ej. "Instructor AFF / USPA"
    especialidad = Column(String(120))     # p.ej. "AFF, Tándem, Cámara"

    enrollments = relationship(
        "Enrollment", back_populates="student",
        foreign_keys="Enrollment.student_id", cascade="all, delete-orphan",
    )

    @property
    def role_label(self):
        return {"admin": "Administrador", "instructor": "Instructor",
                "estudiante": "Estudiante"}[self.role.value]

    @property
    def iniciales(self):
        partes = self.nombre.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[1][0]).upper()
        return self.nombre[:2].upper()


# --------------------------------------------------------------------------- #
#  Cursos
# --------------------------------------------------------------------------- #
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(160), nullable=False)
    modalidad = Column(String(60), nullable=False)         # AFF, Tándem, Wingsuit...
    resumen = Column(String(400))
    descripcion = Column(Text)
    incluye = Column(Text)                                  # una línea por ítem
    requisitos = Column(Text)
    niveles_total = Column(Integer, default=7)
    altura_salto_ft = Column(Integer, default=10000)
    duracion = Column(String(120))                          # texto libre
    precio = Column(Numeric(14, 2), default=0)
    reserva_minima = Column(Numeric(14, 2), default=0)
    moneda = Column(String(8), default="COP")
    activo = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)
    color = Column(String(16), default="#7E0704")
    created_at = Column(DateTime, default=datetime.utcnow)

    levels = relationship(
        "CourseLevel", back_populates="course",
        cascade="all, delete-orphan", order_by="CourseLevel.numero",
    )
    media = relationship(
        "MediaResource", back_populates="course",
        cascade="all, delete-orphan", order_by="MediaResource.orden",
    )
    enrollments = relationship("Enrollment", back_populates="course")

    @property
    def incluye_lista(self):
        return [x.strip() for x in (self.incluye or "").splitlines() if x.strip()]

    @property
    def requisitos_lista(self):
        return [x.strip() for x in (self.requisitos or "").splitlines() if x.strip()]


class CourseLevel(Base):
    """Nivel/salto o módulo teórico dentro de un curso."""
    __tablename__ = "course_levels"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    objetivos = Column(Text)
    es_teorico = Column(Boolean, default=False)

    course = relationship("Course", back_populates="levels")
    progresos = relationship("LevelProgress", back_populates="level")


class MediaResource(Base):
    """Video, manual o documento asociado a un curso (y opcionalmente a un nivel)."""
    __tablename__ = "media_resources"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("course_levels.id"), nullable=True)
    tipo = Column(Enum(MediaType), nullable=False, default=MediaType.video)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    url = Column(String(500))            # enlace externo (YouTube, Vimeo, descarga)
    archivo = Column(String(500))        # ruta de archivo subido (relativa a uploads)
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="media")
    level = relationship("CourseLevel")

    @property
    def youtube_embed(self):
        """Devuelve la URL embebible si es un enlace de YouTube."""
        if not self.url:
            return None
        u = self.url
        vid = None
        if "youtu.be/" in u:
            vid = u.split("youtu.be/")[1].split("?")[0].split("&")[0]
        elif "watch?v=" in u:
            vid = u.split("watch?v=")[1].split("&")[0]
        elif "/embed/" in u:
            return u.split("&")[0]
        if vid:
            return f"https://www.youtube.com/embed/{vid}"
        return None


# --------------------------------------------------------------------------- #
#  Inscripciones y seguimiento
# --------------------------------------------------------------------------- #
class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course"),)

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_inscripcion = Column(Date, default=date.today)
    estado = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.activo)
    precio_acordado = Column(Numeric(14, 2), default=0)
    nivel_actual = Column(Integer, default=0)
    notas = Column(Text)

    student = relationship("User", back_populates="enrollments", foreign_keys=[student_id])
    instructor = relationship("User", foreign_keys=[instructor_id])
    course = relationship("Course", back_populates="enrollments")
    payments = relationship("Payment", back_populates="enrollment", cascade="all, delete-orphan")
    progresos = relationship(
        "LevelProgress", back_populates="enrollment",
        cascade="all, delete-orphan", order_by="LevelProgress.id",
    )

    @property
    def total_pagado(self):
        return float(sum(float(p.monto) for p in self.payments))

    @property
    def saldo(self):
        return float(self.precio_acordado or 0) - self.total_pagado

    @property
    def porcentaje_pagado(self):
        if not self.precio_acordado or float(self.precio_acordado) == 0:
            return 0
        return min(100, round(self.total_pagado / float(self.precio_acordado) * 100))

    @property
    def niveles_aprobados(self):
        return sum(1 for p in self.progresos if p.estado == LevelStatus.aprobado)

    @property
    def porcentaje_avance(self):
        total = self.course.niveles_total if self.course else 0
        if not total:
            return 0
        return round(self.niveles_aprobados / total * 100)


class LevelProgress(Base):
    """Bitácora: registro del avance del estudiante en cada nivel/salto."""
    __tablename__ = "level_progress"

    id = Column(Integer, primary_key=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("course_levels.id"), nullable=False)
    estado = Column(Enum(LevelStatus), default=LevelStatus.pendiente)
    fecha = Column(Date)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nota = Column(Text)
    video_url = Column(String(500))
    altura_ft = Column(Integer)

    enrollment = relationship("Enrollment", back_populates="progresos")
    level = relationship("CourseLevel", back_populates="progresos")
    instructor = relationship("User", foreign_keys=[instructor_id])


# --------------------------------------------------------------------------- #
#  Finanzas
# --------------------------------------------------------------------------- #
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    fecha = Column(Date, default=date.today)
    monto = Column(Numeric(14, 2), nullable=False)
    metodo = Column(Enum(PaymentMethod), default=PaymentMethod.transferencia)
    concepto = Column(Enum(PaymentConcept), default=PaymentConcept.abono)
    referencia = Column(String(120))
    nota = Column(String(255))
    registrado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollment = relationship("Enrollment", back_populates="payments")
    registrado_por = relationship("User", foreign_keys=[registrado_por_id])


class InstructorPayment(Base):
    """Pago realizado A un instructor (su compensación / nómina).

    Es información separada de las finanzas del negocio: el instructor solo ve
    lo relativo a sus propios pagos, nunca los ingresos ni la cartera de la escuela.
    """
    __tablename__ = "instructor_payments"

    id = Column(Integer, primary_key=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    fecha = Column(Date, default=date.today)
    monto = Column(Numeric(14, 2), nullable=False)
    concepto = Column(Enum(InstructorPayConcept), default=InstructorPayConcept.por_salto)
    metodo = Column(Enum(PaymentMethod), default=PaymentMethod.transferencia)
    referencia = Column(String(120))
    nota = Column(String(255))
    saltos = Column(Integer)                 # nº de saltos que cubre (opcional)
    jump_day_id = Column(Integer, ForeignKey("jump_days.id"), nullable=True)
    registrado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    instructor = relationship("User", foreign_keys=[instructor_id])
    registrado_por = relationship("User", foreign_keys=[registrado_por_id])
    jump_day = relationship("JumpDay")


# --------------------------------------------------------------------------- #
#  Programación de saltos (manifiesto)
# --------------------------------------------------------------------------- #
class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(20), unique=True, nullable=False)
    modelo = Column(String(80), nullable=False)
    capacidad = Column(Integer, default=4)
    activo = Column(Boolean, default=True)
    notas = Column(String(255))


class JumpDay(Base):
    """Jornada de saltos en un día puntual."""
    __tablename__ = "jump_days"

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, index=True)
    zona = Column(String(160), default="Braaap Park · Vía Rozo–Cali")
    estado = Column(String(30), default="programada")   # programada / en_curso / cerrada
    clima = Column(String(120))
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    loads = relationship(
        "Load", back_populates="jump_day",
        cascade="all, delete-orphan", order_by="Load.numero",
    )


class Load(Base):
    """Vuelo (load) dentro de una jornada: un avión sube con varias personas."""
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True)
    jump_day_id = Column(Integer, ForeignKey("jump_days.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=True)
    numero = Column(Integer, default=1)
    hora_estimada = Column(String(10))
    altura_ft = Column(Integer, default=10000)
    estado = Column(Enum(LoadStatus), default=LoadStatus.programado)
    notas = Column(String(255))

    jump_day = relationship("JumpDay", back_populates="loads")
    aircraft = relationship("Aircraft")
    slots = relationship(
        "LoadSlot", back_populates="load",
        cascade="all, delete-orphan", order_by="LoadSlot.id",
    )

    @property
    def ocupados(self):
        return len(self.slots)

    @property
    def capacidad(self):
        return self.aircraft.capacidad if self.aircraft else 0


class LoadSlot(Base):
    """Asignación de una persona a un vuelo: quién va en cada vuelo."""
    __tablename__ = "load_slots"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("loads.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    person_nombre = Column(String(160))   # respaldo por si es alguien externo
    rol = Column(Enum(SlotRole), default=SlotRole.alumno)
    tipo_salto = Column(String(120))      # p.ej. "AFF Nivel 3", "Tándem", "Freefly"
    level_id = Column(Integer, ForeignKey("course_levels.id"), nullable=True)
    notas = Column(String(255))

    load = relationship("Load", back_populates="slots")
    person = relationship("User", foreign_keys=[person_id])
    level = relationship("CourseLevel")

    @property
    def display_nombre(self):
        return self.person.nombre if self.person else (self.person_nombre or "—")


# --------------------------------------------------------------------------- #
#  Notificaciones (programables desde el panel del administrador)
# --------------------------------------------------------------------------- #
class NotificationRule(Base):
    """Regla de notificación por correo, configurable por el administrador.

    Dos tipos:
      - recordatorio_salto: recuerda al estudiante su próximo salto (N días antes).
      - oferta_curso: ofrece el curso AFF a quien saltó una sola vez (tras X días).
    """
    __tablename__ = "notification_rules"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(160), nullable=False)
    tipo = Column(Enum(NotificationType), nullable=False)
    activo = Column(Boolean, default=True)
    asunto = Column(String(200), nullable=False)
    cuerpo = Column(Text, nullable=False)
    dias_antelacion = Column(Integer, default=2)    # recordatorio: días antes del salto
    intervalo_dias = Column(Integer, default=30)    # oferta: días desde el último salto
    frecuencia = Column(String(20), default="diaria")  # diaria / semanal / manual
    ultima_ejecucion = Column(DateTime)
    creada_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("NotificationLog", back_populates="rule",
                        cascade="all, delete-orphan")

    @property
    def tipo_label(self):
        return {"recordatorio_salto": "Recordatorio de salto",
                "oferta_curso": "Oferta de curso"}[self.tipo.value]


class NotificationLog(Base):
    """Registro de cada notificación generada (enviada, simulada o con error)."""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("notification_rules.id"), nullable=True)
    tipo = Column(Enum(NotificationType), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String(160), nullable=False)
    asunto = Column(String(200), nullable=False)
    cuerpo = Column(Text, nullable=False)
    estado = Column(Enum(NotificationStatus), default=NotificationStatus.pendiente)
    error = Column(String(300))
    clave = Column(String(200), index=True)   # dedupe: evita reenvíos duplicados
    fecha_generado = Column(DateTime, default=datetime.utcnow)
    fecha_envio = Column(DateTime)

    rule = relationship("NotificationRule", back_populates="logs")
    destinatario = relationship("User", foreign_keys=[destinatario_id])


class Setting(Base):
    """Configuración clave-valor editable por el administrador (p.ej. SMTP).

    Permite parametrizar el envío de correo desde el panel sin tocar variables
    de entorno. Los valores aquí tienen prioridad sobre las variables de entorno.
    """
    __tablename__ = "settings"

    clave = Column(String(60), primary_key=True)
    valor = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
