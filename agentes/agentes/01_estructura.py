"""Agente 1: Estructura Jerárquica - valida H1→H2→H3→H4 correctamente anidados"""
import re, os
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))
        ultimo = {1: None, 2: None, 3: None}
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            m = re.match(r'^(#{1,4})\s+(.+)$', stripped)
            if not m:
                continue
            nivel = len(m.group(1))
            texto = m.group(2).strip()

            # H1 debe ser único por archivo
            if nivel == 1:
                if sum(1 for l in lines if l.startswith('# ') and not l.startswith('##')) > 1:
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='H1_MULTIPLE',
                        severidad='MEDIUM',
                        detalle=f'Múltiples H1 en el mismo archivo',
                        sugerencia='Usar solo un H1 por archivo',
                        agente='01_estructura'
                    ))
                ultimo[1] = texto
                ultimo[2] = None
                ultimo[3] = None
                continue

            # Verificar que tenga un header del nivel superior antes
            if nivel == 2 and ultimo[1] is None:
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=i, tipo='H2_SIN_H1',
                    severidad='HIGH',
                    detalle=f'H2 "{texto}" sin H1 antes',
                    sugerencia='Agregar H1 o cambiar a H1 si es el título principal',
                    agente='01_estructura'
                ))
                ultimo[2] = texto
            elif nivel == 3 and ultimo[2] is None:
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=i, tipo='H3_SIN_H2',
                    severidad='HIGH',
                    detalle=f'H3 "{texto}" sin H2 antes',
                    sugerencia='Agregar H2 o cambiar a H2',
                    agente='01_estructura'
                ))
                ultimo[3] = texto
            elif nivel == 4 and ultimo[3] is None:
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=i, tipo='H4_SIN_H3',
                    severidad='MEDIUM',
                    detalle=f'H4 "{texto}" sin H3 antes',
                    sugerencia='Agregar H3 o cambiar a H3',
                    agente='01_estructura'
                ))

            if nivel == 2:
                ultimo[2] = texto
                ultimo[3] = None
            elif nivel == 3:
                ultimo[3] = texto

            # Detectar H3 falsos (texto corto + mayúscula sostenida = probable dato, no header)
            if nivel == 3 and len(texto) < 60 and texto.isupper() and not any(c in texto for c in 'áéíóúñ'):
                # Check if it's followed by data-like content (not more headers)
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=i, tipo='POSIBLE_H3_FALSO',
                    severidad='MEDIUM',
                    detalle=f'H3 parece ser dato de tabla: "{texto}"',
                    sugerencia='Reemplazar con **texto** si es un valor de tabla',
                    agente='01_estructura',
                    puede_autofix=True
                ))

        # Check: does # title match ### TITLE pattern?
        lines_stripped = [l.strip() for l in lines]
        for i in range(len(lines_stripped) - 1):
            if lines_stripped[i].startswith('# ') and not lines_stripped[i].startswith('## '):
                h1 = lines_stripped[i][2:].strip()
                if i + 1 < len(lines_stripped) and lines_stripped[i+1].startswith('### '):
                    h3 = lines_stripped[i+1][4:].strip()
                    if h1.upper() == h3.upper() or h1.upper() in h3.upper() or h3.upper() in h1.upper():
                        hallazgos.append(Hallazgo(
                            archivo=rel, linea=i+2, tipo='H3_REDUNDANTE_CON_H1',
                            severidad='LOW',
                            detalle=f'H3 "{h3}" repite H1 "{h1}"',
                            sugerencia='Eliminar H3, solo dejar H1',
                            agente='01_estructura',
                            puede_autofix=True
                        ))

    return hallazgos
