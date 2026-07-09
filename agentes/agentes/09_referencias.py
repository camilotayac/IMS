"""Agente 9: Referencias Cruzadas - verifica enlaces internos y referencias a tablas"""
import re, os
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []

    # Collect all headings and their anchors
    todos_headers = {}  # header_text -> (archivo, linea)
    todas_tablas = set()

    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Collect headers
            m = re.match(r'^(#{1,4})\s+(.+?)(?:\s*\{[^}]+\})?$', stripped)
            if m:
                header_text = m.group(2).strip().lower()
                todos_headers[header_text] = (rel, i)

            # Collect table markers
            if '{#tbl-' in stripped:
                tbl_id = re.search(r'{#(tbl-[^}]+)}', stripped)
                if tbl_id:
                    todas_tablas.add(tbl_id.group(1))

            # Detect references to tables/figures
            for ref in re.finditer(r'(?:Tabla|tabla|Figura|figura|Capítulo|capítulo|Sección|sección)\s+(\d[\d.]*)', stripped):
                ref_text = ref.group(0)
                # Check if there's a proper cross-reference syntax
                if '@' not in stripped and '{#tbl-' not in stripped and '{#fig-' not in stripped:
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='REF_PLANA',
                        severidad='MEDIUM',
                        detalle=f'Referencia plana a "{ref_text}" sin crossref Quarto',
                        sugerencia=f'Usar @tbl-xxx o @fig-xxx en lugar de texto plano',
                        agente='09_referencias',
                        puede_autofix=False
                    ))

    # Find references to non-existent headers
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        for i, line in enumerate(lines, 1):
            # Find links to other chapters/files
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.qmd(?:#[^)]*)?)\)', line):
                link_text = m.group(1)
                link_target = m.group(2)
                # Check if target file exists
                target_path = os.path.join(os.path.dirname(fp), link_target.split('#')[0])
                if not os.path.exists(target_path):
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='LINK_ROTO',
                        severidad='HIGH',
                        detalle=f'Link a archivo inexistente: {link_target}',
                        sugerencia='Corregir ruta del enlace',
                        agente='09_referencias',
                        puede_autofix=False
                    ))

    return hallazgos
