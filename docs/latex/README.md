#  Documento LaTeX del Proyecto - Momento III

Este directorio contiene el documento académico escrito en LaTeX para el Proyecto de Electricidad y Magnetismo, **listo para compilar en Overleaf**.

---

##  Integrantes del Grupo
- Drako David Salazar Torres
- Cristhian Santiago Parra Erazo
- Jenifer Daniela Urbano Cordoba
- Nicolas Alejandro Diaz Acosta
- Juan Camilo Lopez Diaz

---

##  Estructura del Documento

```
latex/
 main.tex              # Archivo principal (configurado para Overleaf)
 Makefile              # Script de compilación (para entorno local)
 referencias.bib       # Bibliografía (solo materiales del profesor)
 README.md             # Este archivo
 GUIA_OVERLEAF.md      #  Guía detallada para usar en Overleaf

 secciones/            # Capítulos del documento
    portada.tex       # Portada (actualizada con los 5 estudiantes)
    introduccion.tex  # Capítulo 1: Introducción
    marco_teorico.tex # Capítulo 2: Marco Teórico
    metodologia.tex   # Capítulo 3: Metodología
    resultados.tex    # Capítulo 4: Resultados (imágenes para Overleaf)
    conclusiones.tex  # Capítulo 5: Conclusiones
```

##  Requisitos de Compilación

Para compilar el documento, necesitas:
- **TeX Live** o **MiKTeX** (distribución de LaTeX)
- **pdflatex**: Compilador de LaTeX
- **biber**: Procesador de bibliografía para BibLaTeX

### Instalación en macOS
```bash
brew install --cask mactex
```

### Instalación en Linux (Debian/Ubuntu)
```bash
sudo apt-get install texlive-full biber
```

##  Compilación del Documento

### Usando Make (recomendado)
```bash
cd docs/latex
make          # Compilar el documento
make clean    # Eliminar archivos temporales
make cleanall # Eliminar archivos temporales y PDF
make help     # Mostrar ayuda
```

### Compilación manual
Si prefieres compilar manualmente:
```bash
pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Se necesitan **3 pasadas de pdflatex** para generar correctamente:
- Índice general
- Índice de figuras
- Índice de tablas
- Referencias cruzadas
- Bibliografía

##  Características del Documento

El documento incluye:
-  Portada formal
-  Índice general, de figuras y de tablas
-  5 capítulos completos
-  Ecuaciones matemáticas con `amsmath`
-  Tablas profesionales con `booktabs`
-  Figuras con referencias cruzadas
-  Bibliografía en formato IEEE con `biblatex`
-  Enlaces internos y externos con `hyperref`
-  Formato: A4, 12pt, márgenes 2.5cm, interlineado 1.5
-  Fuente: Times New Roman (compatible)

##  Personalización

### Datos del estudiante
Edita el archivo `secciones/portada.tex` y modifica:
- Tu nombre completo
- Tu código estudiantil
- La fecha

### Bibliografía
Agrega tus referencias en el archivo `referencias.bib` en formato BibTeX.

### Figuras
Las figuras se referencian desde `../../results/figures/` (la carpeta de resultados del proyecto). Si quieres copiarlas aquí:
```bash
cp ../../results/figures/*.png figuras/
```
Y actualiza las rutas en `secciones/resultados.tex`.

##  Paquetes LaTeX Utilizados

- `geometry`: Configuración de márgenes
- `setspace`: Interlineado
- `amsmath, amssymb, amsthm`: Matemáticas
- `graphicx`: Inclusión de figuras
- `booktabs`: Tablas profesionales
- `hyperref`: Enlaces
- `biblatex`: Bibliografía
- `fancyhdr`: Encabezados y pies de página
- `csquotes`: Citas
- `physics`: Notación física
