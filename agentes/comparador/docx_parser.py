"""Parse the DOCX file extracting paragraphs, tables, images, and structure"""
import zipfile
import xml.etree.ElementTree as ET
import os
from typing import List
from comparador import ParrafoDOCX, TablaDOCX, SeccionDOCX

DOCX_PATH = os.path.join(os.path.dirname(__file__), '../../../PEI IEMS VERSION 3 -2026.docx')
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
       'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def parse_docx(path: str = DOCX_PATH):
    z = zipfile.ZipFile(path)
    doc = z.read('word/document.xml')
    root = ET.fromstring(doc)

    paras = root.findall('.//w:p', NS)

    parrafos = []
    for idx, p in enumerate(paras):
        texts = p.findall('.//w:t', NS)
        texto = ''.join(t.text for t in texts if t.text)

        pPr = p.find('.//w:pPr', NS)
        estilo = None
        if pPr is not None:
            se = pPr.find('.//w:pStyle', NS)
            if se is not None:
                estilo = se.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')

        rPr = p.find('.//w:rPr/w:sz', NS)
        sz = int(rPr.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')) if rPr is not None else None

        bold = p.find('.//w:rPr/w:b', NS) is not None

        is_tbl = p.find('.//w:tbl', NS) is not None

        parrafos.append(ParrafoDOCX(
            idx=idx, texto=texto.strip(),
            estilo=estilo, sz=sz, bold=bold,
            es_tabla=is_tbl
        ))

    return parrafos

def get_full_text(parrafos: List[ParrafoDOCX]) -> str:
    return '\n'.join(p.texto for p in parrafos)

def find_secciones(parrafos: List[ParrafoDOCX]) -> List[SeccionDOCX]:
    """Detect major sections from the DOCX based on font size and bold"""
    secciones = []
    current = None
    for p in parrafos:
        t = p.texto.strip()
        if not t:
            continue
        is_header = (p.sz and p.sz >= 24) or (p.bold and len(t) < 100 and t.isupper())
        if is_header:
            secciones.append(SeccionDOCX(
                nombre=t[:80], inicio=p.idx, fin=p.idx,
                nivel=0 if p.sz and p.sz >= 24 else 1
            ))
    return secciones

def find_tables_in_docx(path: str = DOCX_PATH):
    """Extract native Word tables from the DOCX"""
    z = zipfile.ZipFile(path)
    doc = z.read('word/document.xml')
    root = ET.fromstring(doc)

    tables = root.findall('.//w:tbl', NS)
    result = []
    for tidx, tbl in enumerate(tables):
        rows = tbl.findall('.//w:tr', NS)
        data = []
        for row in rows:
            cells = row.findall('.//w:tc', NS)
            row_data = []
            for cell in cells:
                texts = cell.findall('.//w:t', NS)
                cell_text = ''.join(t.text for t in texts if t.text).strip()
                row_data.append(cell_text)
            data.append(row_data)

        # Find paragraph index (look backwards for context)
        parent = tbl.getparent() if hasattr(tbl, 'getparent') else None
        para_idx = None
        for p in root.findall('.//w:p', NS):
            if tbl in list(p.iter()):
                para_idx = list(root.findall('.//w:p', NS)).index(p)
                break

        if data:
            result.append(TablaDOCX(
                id=f"DOCX_TABLA_{tidx+1}",
                inicio=para_idx or 0,
                fin=para_idx or 0,
                columnas=data[0] if data else [],
                filas=data[1:] if len(data) > 1 else [],
                contenido_plano=' | '.join([' | '.join(r) for r in data])
            ))
    return result

def analisis_completo():
    parrafos = parse_docx()
    tablas = find_tables_in_docx()
    secciones = find_secciones(parrafos)
    return {
        'parrafos': parrafos,
        'tablas': tablas,
        'secciones': secciones,
        'total_parrafos': len(parrafos),
        'total_tablas': len(tablas),
        'total_caracteres': sum(len(p.texto) for p in parrafos)
    }
