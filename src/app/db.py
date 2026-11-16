"""Conexión SQLite, esquema y transacciones (data-model.md, architecture.md).

Cada conexión: isolation_level=None (transacciones a mano), busy_timeout,
foreign_keys y WAL. Nunca se comparte una conexión entre hilos a la vez.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS canchas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL UNIQUE,
    deporte     TEXT    NOT NULL,
    precio_hora INTEGER NOT NULL CHECK (precio_hora >= 0),
    activa      INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1)),
    creada_en   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reservas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo        TEXT    NOT NULL UNIQUE,
    cancha_id     INTEGER NOT NULL REFERENCES canchas(id),
    fecha         TEXT    NOT NULL,
    hora_inicio   TEXT    NOT NULL,
    nombre        TEXT    NOT NULL CHECK (length(nombre) BETWEEN 2 AND 60),
    telefono      TEXT    NOT NULL CHECK (telefono NOT GLOB '*[^0-9]*'
                                          AND length(telefono) BETWEEN 7 AND 15),
    precio_hora   INTEGER NOT NULL,
    estado        TEXT    NOT NULL CHECK (estado IN ('confirmada', 'cancelada')),
    cancelada_por TEXT    CHECK (cancelada_por IN ('jugador', 'admin')),
    creada_en     TEXT    NOT NULL,
    cancelada_en  TEXT
);

-- RN-01, RNF-01: una sola reserva confirmada por franja
CREATE UNIQUE INDEX IF NOT EXISTS ux_reserva_activa
    ON reservas (cancha_id, fecha, hora_inicio)
    WHERE estado = 'confirmada';
CREATE INDEX IF NOT EXISTS ix_reserva_telefono ON reservas (telefono, estado);
CREATE INDEX IF NOT EXISTS ix_reserva_agenda   ON reservas (cancha_id, fecha);

CREATE TABLE IF NOT EXISTS bloqueos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cancha_id   INTEGER NOT NULL REFERENCES canchas(id),
    fecha       TEXT    NOT NULL,
    hora_inicio TEXT    NOT NULL,
    motivo      TEXT,
    creado_en   TEXT    NOT NULL,
    UNIQUE (cancha_id, fecha, hora_inicio)
);

-- RN-02, RN-17: una franja no puede tener reserva confirmada y bloqueo a la vez
CREATE TRIGGER IF NOT EXISTS tr_reserva_sin_bloqueo
BEFORE INSERT ON reservas
WHEN NEW.estado = 'confirmada'
BEGIN
    SELECT RAISE(ABORT, 'franja_bloqueada')
    WHERE EXISTS (SELECT 1 FROM bloqueos
                  WHERE cancha_id = NEW.cancha_id AND fecha = NEW.fecha
                    AND hora_inicio = NEW.hora_inicio);
END;

CREATE TRIGGER IF NOT EXISTS tr_bloqueo_sin_reserva
BEFORE INSERT ON bloqueos
BEGIN
    SELECT RAISE(ABORT, 'franja_reservada')
    WHERE EXISTS (SELECT 1 FROM reservas
                  WHERE cancha_id = NEW.cancha_id AND fecha = NEW.fecha
                    AND hora_inicio = NEW.hora_inicio AND estado = 'confirmada');
END;
"""


def connect(db_path, busy_timeout_ms: int = 5000) -> sqlite3.Connection:
    conn = sqlite3.connect(
        str(db_path),
        isolation_level=None,
        timeout=busy_timeout_ms / 1000,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {int(busy_timeout_ms)}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path, busy_timeout_ms: int = 5000) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path, busy_timeout_ms)
    try:
        conn.executescript(ESQUEMA)
    finally:
        conn.close()


@contextmanager
def transaccion(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE: serializa a los escritores (architecture.md, RN-01)."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
