"""Agente 7: Listas y Viñetas - convierte viñetas planas a listas Markdown"""
import re, os
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fp, start=os.path.join(os.path.dirname(__file__), '..'))

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detect bullet character • without proper markdown list syntax
            if stripped.startswith('•') and not stripped.startswith('- '):
                # Check previous line - if it's a heading or empty, this should be list
                prev = lines[i-2].strip() if i >= 2 else ''
                if prev == '' or prev.startswith('#'):
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='VIÑETA_PLANA',
                        severidad='MEDIUM',
                        detalle=f'Viñeta "•" sin formato Markdown: "{stripped[:60]}"',
                        sugerencia='Reemplazar "•" por "- "',
                        agente='07_listas',
                        puede_autofix=True
                    ))

            # Detect emoji sequences that look like list items but without format
            if re.match(r'^[🚀🧪👥🌱🏛️❤️💻📝🤝🌍💡📜💎🧠🛡️🎵🟨🧬🕊️♿🧑👩👤🧩🏢🍉🎓💼🏡🗃️🔍🔄📋📊⚙️🏥👑♿]\s+\d?\.?\s*', stripped):
                # Check if it's already a header
                if not stripped.startswith('#'):
                    hallazgos.append(Hallazgo(
                        archivo=rel, linea=i, tipo='EMOJI_SIN_FORMATO',
                        severidad='LOW',
                        detalle=f'Emoji como item de lista sin formato: "{stripped[:60]}"',
                        sugerencia='Agregar "- " al inicio para lista, o "### " si es sub-sección',
                        agente='07_listas',
                        puede_autofix=False
                    ))

            # Detect bullet items inline (• separated within a single line)
            if stripped.count('•') > 1 and not stripped.startswith('-') and not stripped.startswith('#'):
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=i, tipo='VIÑETAS_INLINE',
                    severidad='LOW',
                    detalle=f'Múltiples • en una línea - deben ser items separados',
                    sugerencia='Dividir en líneas separadas con "- " cada una',
                    agente='07_listas',
                    puede_autofix=False
                ))

    return hallazgos
