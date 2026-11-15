"""Cada criterio de specs/acceptance-criteria.md debe tener al menos una prueba."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SPEC = RAIZ / "specs" / "acceptance-criteria.md"
PATRON_SPEC = re.compile(r"^\*\*(AC-\d{2})", re.MULTILINE)
PATRON_TEST = re.compile(r'ac\("(AC-\d{2})"\)')


def criterios_en_spec() -> set[str]:
    return set(PATRON_SPEC.findall(SPEC.read_text(encoding="utf-8")))


def criterios_con_prueba() -> set[str]:
    encontrados = set()
    for archivo in (RAIZ / "tests").rglob("test_*.py"):
        encontrados |= set(PATRON_TEST.findall(archivo.read_text(encoding="utf-8")))
    return encontrados


def test_la_spec_define_criterios():
    assert len(criterios_en_spec()) >= 22


def test_todo_criterio_tiene_prueba():
    faltan = sorted(criterios_en_spec() - criterios_con_prueba())
    assert not faltan, f"Criterios sin prueba automatizada: {faltan}"


def test_no_hay_pruebas_de_criterios_inexistentes():
    sobran = sorted(criterios_con_prueba() - criterios_en_spec())
    assert not sobran, f"Pruebas que citan criterios que no están en la spec: {sobran}"
