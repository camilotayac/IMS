#!/usr/bin/env python3
"""Orquestador (Agente 10): Coordina la ejecución de los 9 agentes de calidad,
aplica auto-fixes, y genera reporte consolidado."""
import os, sys, json, re, importlib, time
from datetime import datetime
from typing import List
from comparador import Hallazgo
from comparador.docx_parser import analisis_completo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRO_DIR = os.path.join(BASE_DIR, '..')
AGENTES_DIR = os.path.join(BASE_DIR, 'agentes')
REPORTES_DIR = os.path.join(BASE_DIR, 'reportes')
DOCX_PATH = os.path.join(BASE_DIR, '../../PEI IEMS VERSION 3 -2026.docx')

ORDER = [
    ('04_completitud', []),
    ('02_tablas', []),
    ('01_estructura', ['03_parrafos']),
    ('05_duplicados', ['07_listas', '08_consistencia']),
    ('09_referencias', ['06_metadatos']),
]

AUTO_FIXABLE_TYPES = {
    'POSIBLE_H3_FALSO',
    'H3_REDUNDANTE_CON_H1',
    'VIÑETA_PLANA',
}

def discover_qmd_files():
    qmd_files = []
    for root, dirs, files in os.walk(LIBRO_DIR):
        skip = {'agentes', '_site', '_book', '.quarto'}
        dirs[:] = [d for d in dirs if d not in skip]
        for f in sorted(files):
            if f.endswith('.qmd'):
                qmd_files.append(os.path.join(root, f))
    return qmd_files

def load_agent(module_name):
    mod = importlib.import_module(f'agentes.{module_name}')
    return mod

def run_agent(module_name, qmd_files, docx_data=None):
    mod = load_agent(module_name)
    try:
        if module_name == '04_completitud':
            return mod.analizar(qmd_files, docx_parrafos=docx_data['parrafos'] if docx_data else None)
        return mod.analizar(qmd_files)
    except Exception as e:
        return [Hallazgo(
            archivo='orquestador', linea=0, tipo='ERROR_AGENTE',
            severidad='CRITICAL',
            detalle=f'Error en agente {module_name}: {e}',
            agente='10_orquestador'
        )]

def apply_auto_fixes(hallazgos, qmd_files):
    fixes_applied = 0
    for h in hallazgos:
        if not h.puede_autofix or h.tipo not in AUTO_FIXABLE_TYPES:
            continue
        fp = os.path.join(BASE_DIR, h.archivo)
        if not os.path.exists(fp):
            continue
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        changed = False
        idx = h.linea - 1
        if idx < 0 or idx >= len(lines):
            continue
        line = lines[idx]
        stripped = line.rstrip()

        if h.tipo == 'POSIBLE_H3_FALSO':
            m = re.match(r'^###\s+(.+)$', stripped)
            if m:
                lines[idx] = line.replace('###', '**', 1).replace(stripped.split(m.group(1))[-1], '**' + m.group(1) + '**', 1) if '**' not in stripped else line
                if '**' not in stripped:
                    rest = line[line.index(m.group(1)):]
                    lines[idx] = line[:line.index(m.group(1))] + '**' + m.group(1) + '**\n'
                changed = True

        elif h.tipo == 'H3_REDUNDANTE_CON_H1':
            if stripped.startswith('### '):
                lines[idx] = ''  # remove the redundant H3
                changed = True

        elif h.tipo == 'VIÑETA_PLANA':
            if stripped.startswith('•'):
                indent = line[:len(line) - len(line.lstrip())]
                lines[idx] = f'{indent}- {stripped[1:].strip()}\n'
                changed = True

        if changed:
            with open(fp, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            fixes_applied += 1

    return fixes_applied

def generate_report(hallazgos, tiempos, fixes_applied):
    os.makedirs(REPORTES_DIR, exist_ok=True)
    por_severidad = {}
    por_agente = {}
    for h in hallazgos:
        por_severidad.setdefault(h.severidad, []).append(h)
        por_agente.setdefault(h.agente, []).append(h)

    reporte = {
        'fecha': datetime.now().isoformat(),
        'resumen': {
            'total_hallazgos': len(hallazgos),
            'fixes_aplicados': fixes_applied,
            'por_severidad': {k: len(v) for k, v in sorted(por_severidad.items())},
            'por_agente': {k: len(v) for k, v in sorted(por_agente.items())},
        },
        'tiempos_ejecucion': tiempos,
        'hallazgos': [
            {
                'archivo': h.archivo,
                'linea': h.linea,
                'tipo': h.tipo,
                'severidad': h.severidad,
                'detalle': h.detalle,
                'sugerencia': h.sugerencia,
                'agente': h.agente,
                'autofix': h.puede_autofix,
            }
            for h in hallazgos
        ],
    }
    rp = os.path.join(REPORTES_DIR, 'reporte.json')
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return rp

def print_summary(hallazgos, tiempos):
    print(f"\n{'='*60}")
    print(f"  ORQUESTADOR - REPORTE DE CALIDAD")
    print(f"{'='*60}")
    sev = {}
    for h in hallazgos:
        sev.setdefault(h.severidad, 0)
        sev[h.severidad] += 1
    for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OK']:
        if s in sev:
            print(f"  {s:12s}: {sev[s]}")
    print(f"  {'TOTAL':12s}: {len(hallazgos)}")
    print(f"\n  Tiempo total: {sum(tiempos.values()):.2f}s")
    print(f"  Agentes ejecutados: {len(tiempos)}")
    print(f"{'='*60}\n")

def main():
    print("Inicializando análisis del libro PEI...\n")

    # Discover files
    qmd_files = discover_qmd_files()
    print(f"  Archivos .qmd encontrados: {len(qmd_files)}")

    # Load DOCX
    print("  Cargando DOCX fuente...")
    docx_data = analisis_completo()
    print(f"    {docx_data['total_parrafos']} párrafos, {docx_data['total_tablas']} tablas nativas")

    # Run agents in defined order
    all_hallazgos = []
    tiempos = {}

    for agent_group in ORDER:
        if isinstance(agent_group, tuple):
            primary = agent_group[0]
            parallels = agent_group[1]
            agents_to_run = [primary] + parallels
        else:
            agents_to_run = [agent_group]

        for agent_name in agents_to_run:
            t0 = time.time()
            print(f"  Ejecutando agente {agent_name}...", end=' ', flush=True)
            hallazgos = run_agent(agent_name, qmd_files, docx_data)
            elapsed = time.time() - t0
            tiempos[agent_name] = elapsed
            all_hallazgos.extend(hallazgos)
            print(f"{len(hallazgos)} hallazgos en {elapsed:.2f}s")

    # Apply auto-fixes
    print("\n  Aplicando auto-fixes...", end=' ', flush=True)
    fixes = apply_auto_fixes(all_hallazgos, qmd_files)
    print(f"{fixes} fixes aplicados")

    # Generate report
    rp = generate_report(all_hallazgos, tiempos, fixes)
    print(f"  Reporte guardado: {rp}")

    # Summary
    print_summary(all_hallazgos, tiempos)

    # Group by severity for actionable output
    criticos = [h for h in all_hallazgos if h.severidad == 'CRITICAL']
    altos = [h for h in all_hallazgos if h.severidad == 'HIGH']
    if criticos:
        print("  HALLAZGOS CRÍTICOS:")
        for h in criticos:
            print(f"    - {h.archivo}:{h.linea} [{h.tipo}] {h.detalle}")
    if altos:
        print(f"  HALLAZGOS HIGH (primeros 10):")
        for h in altos[:10]:
            print(f"    - {h.archivo}:{h.linea} [{h.tipo}] {h.detalle[:100]}")

    return all_hallazgos

if __name__ == '__main__':
    sys.path.insert(0, BASE_DIR)
    main()
