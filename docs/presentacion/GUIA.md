# Guía de Uso — Presentación Beamer

Esta guía explica cómo compilar y personalizar la presentación Beamer del proyecto.

---

## 📁 Estructura de la Presentación
```
docs/presentacion/
├── main.tex              # Archivo principal de Beamer
├── GUIA.md               # Esta guía
└── figuras/              # Carpeta con las figuras
    ├── comparison_initial_vs_final.png
    ├── energy_vs_iteration.png
    ├── potential_heatmap.png
    └── electric_field_quiver.png
```

---

## 🚀 Cómo Compilar la Presentación

### Método 1: Usar Overleaf (Recomendado)
1. Crea un nuevo proyecto en Overleaf
2. Sube el archivo `main.tex`
3. Sube las figuras a la carpeta del proyecto
4. Haz clic en "Recompile"

### Método 2: Compilar Localmente (LaTeX Instalado)
Si tienes LaTeX instalado en tu equipo:
```bash
cd docs/presentacion
pdflatex main.tex
pdflatex main.tex  # Ejecutar dos veces para generar el índice correctamente
```

---

## ✏️ Cómo Personalizar la Presentación

### 1. Cambiar Datos del Equipo
Edita la sección "DATOS DE LA PRESENTACIÓN" en `main.tex`:
```latex
\author[Equipo]{
  Drako David Salazar Torres \\
  Cristhian Santiago Parra Erazo \\
  Jenifer Daniela Urbano Cordoba \\
  Nicolas Alejandro Diaz Acosta \\
  Juan Camilo Lopez Diaz
}
```

### 2. Cambiar Colores
Los colores personalizados están definidos como:
```latex
\definecolor{UCCAzul}{RGB}{0, 51, 102}
\definecolor{UCCRojo}{RGB}{204, 0, 0}
```
Cambia los valores RGB para usar tus colores preferidos.

### 3. Agregar/Eliminar Diapositivas
- Para agregar una diapositiva: Usa `\begin{frame}{Título} ... \end{frame}`
- Para eliminar una diapositiva: Borra el bloque `frame` correspondiente

### 4. Cambiar las Figuras
1. Coloca tus nuevas figuras en la carpeta `figuras/`
2. Actualiza las rutas en los comandos `\includegraphics`
3. Ajusta el tamaño con `width=0.8\textwidth` o similar

---

## 🎨 Características de la Presentación
- ✅ Tema Madrid (profesional y limpio)
- ✅ Colores corporativos de la UCC
- ✅ Sin símbolos de navegación (menos distracción)
- ✅ Overlays (`\pause`) para revelar contenido paso a paso
- ✅ Bloques de resumen, alertas y ejemplos
- ✅ Tablas profesionales con `booktabs`
- ✅ Referencias bibliográficas
- ✅ Compatibilidad con resoluciones 16:9 (modernas)

---

## 📋 Lista de Verificación Antes de la Presentación
- [ ] Todas las figuras están en la carpeta `figuras/`
- [ ] Los nombres de los integrantes están correctos
- [ ] La presentación compila sin errores
- [ ] El índice se genera correctamente (compila dos veces)
- [ ] Las referencias bibliográficas están actualizadas
- [ ] La fecha es la correcta

---

## 🆘 Problemas Comunes

### Error: "File not found" al compilar
- Asegúrate de que las figuras estén en la carpeta `figuras/`
- Verifica que los nombres de los archivos coincidan exactamente (case-sensitive en Linux/macOS)

### Error: "Undefined control sequence"
- Asegúrate de tener todos los paquetes instalados (`amsmath`, `graphicx`, `booktabs`, etc.)
- Usa una distribución completa de LaTeX (TeX Live, MiKTeX, MacTeX)

### El índice no aparece o está incompleto
- Compila el archivo **dos veces** consecutivas con `pdflatex`

---

¡Listo para presentar! 🎤
