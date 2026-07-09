"""Agente 5: Duplicados - detecta texto repetido entre archivos y dentro de un archivo"""
import os, re
from typing import List
from collections import defaultdict
from comparador import Hallazgo

MIN_BLOCK_LEN = 100

def extraer_bloques(texto: str) -> List[str]:
    """Extract meaningful text blocks (paragraphs)"""
    bloques = []
    for p in texto.split('\n\n'):
        stripped = p.strip()
        if len(stripped) > MIN_BLOCK_LEN and not stripped.startswith('#') and not stripped.startswith('|') and not stripped.startswith('```'):
            bloques.append(stripped)
    return bloques

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []

    # Load all blocks from all files
    archivo_bloques = {}
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            texto = f.read()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))
        bloques = extraer_bloques(texto)
        archivo_bloques[rel] = bloques

    # Compare within each file (intra-file duplicates)
    for rel, bloques in archivo_bloques.items():
        vistos = {}
        for i, b in enumerate(bloques):
            # Normalize for comparison
            b_norm = re.sub(r'[^a-zA-Záéíóúñü0-9]', '', b.lower())
            if len(b_norm) < 30:
                continue
            if b_norm in vistos:
                prev_idx = vistos[b_norm]
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=0, tipo='DUPLICADO_INTRA',
                    severidad='HIGH',
                    detalle=f'Bloque duplicado (~{len(b)} chars): "{b[:80]}..."',
                    sugerencia=f'Eliminar copia duplicada (original en bloque #{prev_idx+1})',
                    agente='05_duplicados',
                    puede_autofix=False
                ))
            else:
                vistos[b_norm] = i

    # Compare across files (inter-file duplicates)
    archivos_lista = list(archivo_bloques.items())
    for i in range(len(archivos_lista)):
        for j in range(i+1, len(archivos_lista)):
            rel_a, bloques_a = archivos_lista[i]
            rel_b, bloques_b = archivos_lista[j]
            for ba in bloques_a:
                ba_norm = re.sub(r'[^a-zA-Záéíóúñü0-9]', '', ba.lower())
                if len(ba_norm) < 30:
                    continue
                for bb in bloques_b:
                    bb_norm = re.sub(r'[^a-zA-Záéíóúñü0-9]', '', bb.lower())
                    if len(bb_norm) < 30:
                        continue
                    # Check for near-identical blocks
                    if ba_norm == bb_norm:
                        hallazgos.append(Hallazgo(
                            archivo=rel_a, linea=0, tipo='DUPLICADO_INTER',
                            severidad='HIGH',
                            detalle=f'Bloque duplicado en {rel_b}: "{ba[:80]}..."',
                            sugerencia='Unificar o referenciar en lugar de duplicar',
                            agente='05_duplicados',
                            puede_autofix=False
                        ))
                        break

    return hallazgos
