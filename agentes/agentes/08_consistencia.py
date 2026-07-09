"""Agente 8: Consistencia Visual - normaliza negritas, cursivas, comillas"""
import re, os
from typing import List
from collections import defaultdict
from comparador import Hallazgo

TERMINOS_TECNICOS = ['STEM', 'EAU', 'DUA', 'PIAR', 'SIEE', 'PRAE', 'GEEMPA', 'CLEI',
                     'ABP', 'TIC', 'EdTech', 'ODS', 'FFIE', 'PMI', 'FSE', 'PPP',
                     'COPASST', 'COCOLA', 'SG-SST', 'PTA', 'PAE', 'SIMAT', 'ICFES',
                     'DANE', 'NIT', 'MEN', 'SEM']

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []

    # Track first appearance of each technical term
    primera_aparicion = {}

    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detect direct quotes without formatting
            for m in re.finditer(r'[\u201C\u201D]([^\u201C\u201D]{20,})[\u201C\u201D]', stripped):
                quote = m.group(0)
                # Check if it's already inside a blockquote or italic
                if not stripped.startswith('>') and '*' not in stripped[:stripped.find(quote)] if quote in stripped else True:
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='CITA_SIN_FORMATO',
                        severidad='LOW',
                        detalle=f'Texto entre comillas sin formato de cita',
                        sugerencia='Usar > blockquote para citas textuales o *cursiva*',
                        agente='08_consistencia',
                        puede_autofix=False
                    ))

            # Detect inconsistently formatted technical terms
            for termino in TERMINOS_TECNICOS:
                # Find terms that appear without bold formatting
                idx = stripped.find(termino)
                if idx >= 0:
                    # Check if already bold
                    before = stripped[max(0,idx-2):idx]
                    after = stripped[idx+len(termino):idx+len(termino)+2]
                    is_bold = '**' in before or '**' in after

                    if termino not in primera_aparicion:
                        primera_aparicion[termino] = (rel, i)
                        if not is_bold and termino in ['STEM', 'EAU', 'DUA', 'PIAR']:
                            hallazgos.append(Hallazgo(
                                archivo=rel, linea=i, tipo='TERMINO_SIN_FORMATO',
                                severidad='LOW',
                                detalle=f'Primera aparición de "{termino}" sin énfasis',
                                sugerencia=f'Usar *{termino}* en la primera aparición',
                                agente='08_consistencia',
                                puede_autofix=False
                            ))

    return hallazgos
