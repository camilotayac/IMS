"""Agente 6: Metadatos - valida YAML frontmatter, imágenes, bibliografía"""
import os, yaml, re
from typing import List
from comparador import Hallazgo

def analizar(archivos: List[str]) -> List[Hallazgo]:
    hallazgos = []
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    images_dir = os.path.join(base_dir, 'images')
    quarto_yml = os.path.join(base_dir, '_quarto.yml')

    # Check _quarto.yml exists
    if not os.path.exists(quarto_yml):
        hallazgos.append(Hallazgo(
            archivo='_quarto.yml', linea=0, tipo='FALTANTE',
            severidad='CRITICAL',
            detalle='No existe _quarto.yml',
            agente='06_metadatos'
        ))
        return hallazgos

    with open(quarto_yml, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
        except Exception as e:
            hallazgos.append(Hallazgo(
                archivo='_quarto.yml', linea=0, tipo='YAML_INVALIDO',
                severidad='CRITICAL',
                detalle=f'Error parseando _quarto.yml: {e}',
                agente='06_metadatos'
            ))
            return hallazgos

    # Check book config
    book = config.get('book', {})
    if not book.get('title'):
        hallazgos.append(Hallazgo(
            archivo='_quarto.yml', linea=0, tipo='SIN_TITULO',
            severidad='HIGH',
            detalle='Falta title en book',
            agente='06_metadatos'
        ))
    if not book.get('author'):
        hallazgos.append(Hallazgo(
            archivo='_quarto.yml', linea=0, tipo='SIN_AUTOR',
            severidad='MEDIUM',
            detalle='Falta author en book',
            agente='06_metadatos'
        ))
    if not book.get('date'):
        hallazgos.append(Hallazgo(
            archivo='_quarto.yml', linea=0, tipo='SIN_FECHA',
            severidad='LOW',
            detalle='Falta date en book',
            agente='06_metadatos'
        ))

    # Check cover-image
    cover = book.get('cover-image', '')
    if cover:
        cover_path = os.path.join(base_dir, cover)
        if not os.path.exists(cover_path):
            hallazgos.append(Hallazgo(
                archivo='_quarto.yml', linea=0, tipo='IMAGEN_FALTANTE',
                severidad='HIGH',
                detalle=f'Cover image no encontrada: {cover}',
                agente='06_metadatos'
            ))

    # Check favicon
    favicon = book.get('favicon', '')
    if favicon:
        favicon_path = os.path.join(base_dir, favicon)
        if not os.path.exists(favicon_path):
            hallazgos.append(Hallazgo(
                archivo='_quarto.yml', linea=0, tipo='FAVICON_FALTANTE',
                severidad='MEDIUM',
                detalle=f'Favicon no encontrado: {favicon}',
                agente='06_metadatos'
            ))

    # Check chapters referenced exist
    chapters = []
    for ch in book.get('chapters', []):
        if isinstance(ch, dict):
            chapters.extend(ch.get('chapters', []))
        elif isinstance(ch, str):
            chapters.append(ch)
    for ch in book.get('appendices', []):
        if isinstance(ch, str):
            chapters.append(ch)

    for ch_ref in chapters:
        ch_path = os.path.join(base_dir, ch_ref)
        if not os.path.exists(ch_path):
            hallazgos.append(Hallazgo(
                archivo='_quarto.yml', linea=0, tipo='CHAPTER_FALTANTE',
                severidad='HIGH',
                detalle=f'Chapter referenciado no existe: {ch_ref}',
                agente='06_metadatos'
            ))

    # Check images used in files exist
    for fp in sorted(archivos):
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(fp, start=base_dir)
        for img_match in re.finditer(r'!\[.*?\]\((.+?)\)', content):
            img_path = img_match.group(1)
            full_path = os.path.join(os.path.dirname(fp), img_path)
            if not os.path.exists(full_path):
                hallazgos.append(Hallazgo(
                    archivo=rel, linea=0, tipo='IMG_FALTANTE',
                    severidad='HIGH',
                    detalle=f'Imagen referenciada no existe: {img_path}',
                    agente='06_metadatos'
                ))

    # Check bibliography
    bib = config.get('bibliography', '')
    if bib:
        bib_path = os.path.join(base_dir, bib)
        if not os.path.exists(bib_path):
            hallazgos.append(Hallazgo(
                archivo='_quarto.yml', linea=0, tipo='BIB_FALTANTE',
                severidad='MEDIUM',
                detalle=f'Bibliografía no encontrada: {bib}',
                agente='06_metadatos'
            ))

    return hallazgos
