#===============================================================================
# Makefile para compilar el documento LaTeX
#===============================================================================

# Nombre del documento principal (sin .tex)
DOCNAME = main

# Compilador LaTeX
LATEX = pdflatex
BIBER = biber

# Opciones de compilación
LATEXFLAGS = -interaction=nonstopmode -file-line-error

# Archivos fuente
TEXFILES = $(wildcard *.tex) $(wildcard secciones/*.tex)
BIBFILES = referencias.bib

# Archivos generados
PDFFILE = $(DOCNAME).pdf
AUXFILES = $(DOCNAME).aux $(DOCNAME).log $(DOCNAME).out \
           $(DOCNAME).toc $(DOCNAME).lof $(DOCNAME).lot \
           $(DOCNAME).bbl $(DOCNAME).blg $(DOCNAME).bcf \
           $(DOCNAME).run.xml $(addsuffix .aux,$(basename $(wildcard secciones/*.tex)))

#===============================================================================
# Objetivos principales
#===============================================================================

.PHONY: all clean help

all: $(PDFFILE)

# Regla para compilar el PDF
$(PDFFILE): $(TEXFILES) $(BIBFILES)
	@echo "=========================================="
	@echo "  Compilando LaTeX (1ra pasada)..."
	@echo "=========================================="
	$(LATEX) $(LATEXFLAGS) $(DOCNAME)
	
	@echo "\n=========================================="
	@echo "  Procesando bibliografía con Biber..."
	@echo "=========================================="
	$(BIBER) $(DOCNAME)
	
	@echo "\n=========================================="
	@echo "  Compilando LaTeX (2da pasada)..."
	@echo "=========================================="
	$(LATEX) $(LATEXFLAGS) $(DOCNAME)
	
	@echo "\n=========================================="
	@echo "  Compilando LaTeX (3ra pasada)..."
	@echo "=========================================="
	$(LATEX) $(LATEXFLAGS) $(DOCNAME)
	
	@echo "\n=========================================="
	@echo "  ✅ Compilación completada!"
	@echo "  📄 Archivo: $(PDFFILE)"
	@echo "=========================================="

# Limpiar archivos generados
clean:
	@echo "=========================================="
	@echo "  Limpiando archivos temporales..."
	@echo "=========================================="
	rm -f $(AUXFILES)
	@echo "  ✅ Limpieza completada!"

# Limpiar todo, incluyendo el PDF
cleanall: clean
	@echo "  Eliminando PDF..."
	rm -f $(PDFFILE)
	@echo "  ✅ Limpieza completa!"

# Ayuda
help:
	@echo "Uso: make [objetivo]"
	@echo ""
	@echo "Objetivos disponibles:"
	@echo "  all       - Compilar el documento (predeterminado)"
	@echo "  clean     - Eliminar archivos temporales"
	@echo "  cleanall  - Eliminar archivos temporales y PDF"
	@echo "  help      - Mostrar esta ayuda"
