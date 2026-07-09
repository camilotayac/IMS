#!/usr/bin/env bash
# Compilar libro PEI en HTML, PDF, EPUB y DOCX
# Uso: ./compile.sh [html|pdf|epub|docx|all]
set -euo pipefail

FORMAT="${1:-all}"

case "$FORMAT" in
  html)
    quarto render --to html
    ;;
  pdf)
    QUARTO_TEXMGR_AUTO_INSTALL=0 quarto render --to pdf
    ;;
  epub)
    QUARTO_TEXMGR_AUTO_INSTALL=0 quarto render --to epub
    ;;
  docx)
    quarto render --to docx
    ;;
  all)
    quarto render --to html
    QUARTO_TEXMGR_AUTO_INSTALL=0 quarto render --to pdf
    QUARTO_TEXMGR_AUTO_INSTALL=0 quarto render --to epub || echo "EPUB skipped (needs PDF first)"
    quarto render --to docx
    ;;
  *)
    echo "Uso: ./compile.sh [html|pdf|epub|docx|all]"
    exit 1
    ;;
esac

echo "✅ $FORMAT compilado en _book/"
