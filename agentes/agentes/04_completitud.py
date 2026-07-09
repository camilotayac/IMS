"""Agente 4: Completitud - coteja contenido del libro vs DOCX original"""
import os, re
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str], docx_parrafos: List = None) -> List[Hallazgo]:
    hallazgos = []

    # Load DOCX reference text
    if docx_parrafos is None:
        try:
            from comparador.docx_parser import parse_docx
            docx_parrafos = parse_docx()
        except Exception as e:
            hallazgos.append(Hallazgo(
                archivo='DOCX', linea=0, tipo='ERROR_CARGA',
                severidad='CRITICAL',
                detalle=f'No se pudo cargar el DOCX: {e}',
                agente='04_completitud'
            ))
            return hallazgos

    # Build full text of the book
    libro_texto_completo = ''
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            libro_texto_completo += f.read() + '\n'

    libro_texto_limpio = re.sub(r'[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ0-9]', '', libro_texto_completo.lower())

    # Check each DOCX paragraph against book
    perdidos = []
    for p in docx_parrafos:
        t = p.texto.strip()
        if len(t) < 20:
            continue
        t_limpio = re.sub(r'[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ0-9]', '', t.lower())
        if len(t_limpio) < 10:
            continue
        if t_limpio not in libro_texto_limpio:
            perdidos.append(p)

    if perdidos:
        hallazgos.append(Hallazgo(
            archivo='DOCX vs LIBRO', linea=0,
            tipo='CONTENIDO_NO_ENCONTRADO',
            severidad='HIGH',
            detalle=f'{len(perdidos)} párrafos del DOCX no encontrados en el libro',
            sugerencia='Revisar si falta contenido al extraer del DOCX',
            agente='04_completitud'
        ))
        # Show first 5 missing
        for p in perdidos[:5]:
            hallazgos.append(Hallazgo(
                archivo='DOCX', linea=p.idx,
                tipo='FRAGMENTO_PERDIDO',
                severidad='MEDIUM',
                detalle=f'Texto no encontrado en libro: "{p.texto[:100]}"',
                agente='04_completitud'
            ))

    return hallazgos
