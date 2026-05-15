#  Guía para Compilar en Overleaf

Esta guía explica cómo configurar y compilar el documento LaTeX en **Overleaf** (www.overleaf.com).

---

##  Paso 1: Preparar los Archivos

Antes de subir a Overleaf, organiza los archivos en tu computadora:

### Estructura Recomendada para Overleaf
```
Proyecto_FisicaII_Overleaf/

 main.tex                    # Archivo principal
 referencias.bib              # Bibliografía

 secciones/                  # Capítulos del documento
    portada.tex
    introduccion.tex
    marco_teorico.tex
    metodologia.tex
    resultados.tex
    conclusiones.tex

 [TODAS LAS IMÁGENES PNG]    #  Copia todas las figuras aquí!
     comparison_initial_vs_final.png
     scatter_initial.png
     scatter_final.png
     energy_vs_iteration.png
     energy_log_scale.png
     potential_heatmap.png
     electric_field_quiver.png
     electric_field_magnitude.png
     distance_histogram.png
     radial_distribution.png
     acceptance_rate.png
     (todas las demás .png de results/figures/)
```

###  Importante: Copiar las Imágenes
Las imágenes **NO deben estar en subcarpetas** para Overleaf (o si lo están, ajusta `\graphicspath`). La forma más sencilla es:

1. Copia **todos los archivos .png** de `results/figures/` a la carpeta raíz del proyecto Overleaf
2. Asegúrate de que los nombres coincidan exactamente (mayúsculas/minúsculas importan!)

---

##  Paso 2: Subir a Overleaf

1. **Crear un nuevo proyecto en Overleaf**:
   - Ve a [www.overleaf.com](https://www.overleaf.com)
   - Haz clic en **New Project** → **Blank Project**
   - Nombra el proyecto: `Proyecto_Electricidad_Magnetismo_MomentoIII`

2. **Subir los archivos**:
   - Arrastra y suelta todos los archivos a la ventana de Overleaf
   - O usa el botón **Upload** en la esquina superior izquierda
   - Asegúrate de que `main.tex` sea el archivo principal (debe estar seleccionado en el menú superior)

3. **Verificar la estructura**:
   - La estructura en Overleaf debe verse igual que la descrita arriba
   - Todas las imágenes deben estar en la carpeta raíz (o en `figuras/` si prefieres)

---

##  Paso 3: Configurar Overleaf

1. **Cambiar el compilador**:
   - Ve al menú **Menu** (esquina superior izquierda)
   - En **Compiler**, selecciona **XeLaTeX** o **LuaLaTeX** (recomendado para español y caracteres especiales)
   - **O bien**, usa **pdflatex** (también funciona)

2. **Configurar el idioma (si es necesario)**:
   - El paquete `babel[spanish]` ya está incluido, no requiere configuración adicional

---

##  Paso 4: Compilar el Documento

1. Haz clic en el botón **Recompile** (flecha verde en la esquina superior izquierda)
2. Espera a que termine la compilación
3. Si todo sale bien, verás el PDF en el panel derecho

---

##  Solución de Problemas Comunes

### Error: "File not found" para las imágenes
- **Solución**: Asegúrate de que todas las imágenes estén en la carpeta raíz del proyecto Overleaf
- Verifica que los nombres de los archivos coincidan exactamente (incluyendo mayúsculas/minúsculas)

### Error con biber/bibliografía
- **Solución**: Overleaf usa biber por defecto con biblatex. Asegúrate de que:
  - El archivo `referencias.bib` esté en la carpeta raíz
  - En el Menú → Compiler esté seleccionado **XeLaTeX** o **LuaLaTeX**

### El idioma no es español
- **Solución**: Verifica que la línea `\usepackage[spanish]{babel}` esté en `main.tex` (sí está)

---

##  Descargar el PDF Final

1. Cuando el documento compile sin errores
2. Haz clic en el botón **Menu** → **Download PDF**
3. Guarda el archivo en tu computadora

---

##  Lista de Verificación Pre-Entrega

Antes de entregar, marca todas las casillas:

- [ ] Todas las imágenes están en la carpeta raíz de Overleaf
- [ ] La portada tiene los 5 nombres del grupo
- [ ] No hay referencias a código estudiantil
- [ ] Todas las citas están correctamente vinculadas
- [ ] El documento compila sin errores
- [ ] El índice general, de figuras y de tablas se genera correctamente
- [ ] La bibliografía aparece al final
- [ ] Todas las figuras están en su lugar con las captiones correctas

---

##  Ayuda Adicional

Si tienes problemas:
1. Revisa los logs de Overleaf (panel inferior)
2. Verifica que todos los archivos estén correctamente nombrados
3. Asegúrate de que la estructura sea la correcta

¡Éxito con tu proyecto! 
