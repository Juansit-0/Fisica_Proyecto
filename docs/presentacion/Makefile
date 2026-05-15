#===============================================================================
# Makefile — Presentación Beamer
#
# Targets:
#   make all        - Compilar la presentación completa (dos veces)
#   make clean      - Limpiar archivos temporales
#
# Autor: Proyecto Física II — Universidad Cooperativa de Colombia
#===============================================================================

# Compilador
LATEX = pdflatex

# Archivo principal
MAIN = main.tex

# PDF generado
PDF = $(MAIN:.tex=.pdf)

# ============================================================================
# Targets principales
# ============================================================================

.PHONY: all clean

# Compilar la presentación (dos veces para índice)
all: $(PDF)

$(PDF): $(MAIN) figuras/*.png
	@echo "Compilando primera vez..."
	$(LATEX) -interaction=nonstopmode $(MAIN) > /dev/null 2>&1
	@echo "Compilando segunda vez (índice)..."
	$(LATEX) -interaction=nonstopmode $(MAIN) > /dev/null 2>&1
	@echo ""
	@echo "  Presentación compilada exitosamente: $(PDF)"
	@echo ""

# Limpiar archivos temporales
clean:
	@echo "Limpiando archivos temporales..."
	rm -f *.aux *.log *.nav *.out *.snm *.toc
	@echo "Limpieza completa."
