"""Agente 3: Párrafos - detecta y sugiere división de párrafos largos"""
import re, os
from typing import List
from comparador import Hallazgo

LIMITE_PARRAFO = 500
LIMITE_CRITICO = 800

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        # Merge lines into paragraphs
        parrafos = []
        current = []
        inicio = 1
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == '' and current:
                parrafos.append((inicio, ' '.join(current)))
                current = []
                inicio = i + 1
            elif stripped != '' and not stripped.startswith('#') and not stripped.startswith('|') and not stripped.startswith('>') and not stripped.startswith('```') and not stripped.startswith(':::'):
                current.append(stripped)
            elif stripped == '' and not current:
                inicio = i + 1
        if current:
            parrafos.append((inicio, ' '.join(current)))

        for inicio_para, texto in parrafos:
            if len(texto) > LIMITE_CRITICO:
                severidad = 'HIGH'
            elif len(texto) > LIMITE_PARRAFO:
                severidad = 'MEDIUM'
            else:
                continue

            # Count sentences
            oraciones = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])', texto)
            if len(oraciones) <= 1:
                # Single sentence, harder to split
                continue

            hallazgos.append(Hallazgo(
                archivo=rel, linea=inicio_para,
                tipo='PARRAFO_LARGO',
                severidad=severidad,
                detalle=f'Párrafo de {len(texto)} caracteres ({len(oraciones)} oraciones)',
                sugerencia=f'Dividir en {min(len(oraciones), 3)} párrafos separados por tema',
                agente='03_parrafos',
                puede_autofix=False
            ))

    return hallazgos
