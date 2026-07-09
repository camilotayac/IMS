"""Agente 2: Conversión de Tablas - detecta tablas planas vs Markdown"""
import re, os
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []
    patron_tabla_md = re.compile(r'^\|.+\|$')
    patron_tabla_sep = re.compile(r'^\|[-:| ]+\|$')

    # Señales de tabla plana (pseudo-tabla)
    senales_tabla_plana = [
        'Matriz Técnica', 'TABLA ', 'Tabla ', 
        'Componente Técnico', 'Criterio de Evaluación', 'Indicador Operacional',
        'Eje Estratégico', 'Línea de Acción', 'Dimensión de Gestión',
        'Meta de Calidad', 'Símbolo', 'Elemento Constitutivo',
        'Principio DUA', 'Estrategia Metodológica',
    ]

    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        # Count markdown tables
        md_tables = 0
        in_table = False
        for i, line in enumerate(lines, 1):
            if patron_tabla_md.match(line):
                if not in_table:
                    md_tables += 1
                    in_table = True
            else:
                in_table = False

        # Detect pseudo-tables: sequences of TABLA / Matriz mentions followed by non-table data
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            for senal in senales_tabla_plana:
                if senal in stripped:
                    # Check next lines for column-like data
                    next_lines = lines[i:i+20]
                    # Look for patterns like: short lines separated by blank lines
                    col_count = 0
                    for nl in next_lines[:10]:
                        ns = nl.strip()
                        if len(ns) > 0 and len(ns) < 80 and not ns.startswith('#') and not ns.startswith('|') and not ns.startswith('*') and not ns.startswith('-'):
                            col_count += 1
                    if col_count >= 3:
                        hallazgos.append(Hallazgo(
                            archivo=rel, linea=i, tipo='TABLA_PLANA',
                            severidad='HIGH',
                            detalle=f'Posible tabla plana (columnas separadas como texto): "{stripped[:80]}"',
                            sugerencia='Convertir a | col1 | col2 | ... | formato Markdown',
                            agente='02_tablas',
                            puede_autofix=False
                        ))
                        break

    return hallazgos
