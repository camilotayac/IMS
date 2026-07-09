"""Shared types and utilities for the 10-agent system"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Hallazgo:
    archivo: str
    linea: int
    tipo: str
    severidad: str  # CRITICAL | HIGH | MEDIUM | LOW | OK
    detalle: str
    sugerencia: str = ""
    agente: str = ""
    puede_autofix: bool = False

@dataclass
class TablaDOCX:
    id: str
    inicio: int
    fin: int
    columnas: list
    filas: list
    contenido_plano: str

@dataclass
class SeccionDOCX:
    nombre: str
    inicio: int
    fin: int
    nivel: int  # 0=portada, 1=parte, 2=capítulo, 3=subcapítulo

@dataclass
class ParrafoDOCX:
    idx: int
    texto: str
    estilo: Optional[str]
    sz: Optional[int]
    bold: bool
    es_tabla: bool = False
