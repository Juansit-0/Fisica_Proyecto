# 📝 Registro de Modificaciones del Documento LaTeX

Este archivo documenta todos los cambios realizados en el documento LaTeX para referencia futura.

---

## Modificación: Enlaces en Color Negro

**Fecha:** 2026-05-11
**Responsable:** Asistente de Trae
**Archivo Modificado:** `main.tex`

### Descripción
Se modificó la configuración del paquete `hyperref` para que todos los elementos interactivos (enlaces internos, citas, URLs) aparezcan en **color negro (#000000)** en el PDF generado.

### Cambios Realizados
En la sección "CONFIGURACIÓN DE HYPERREF" de `main.tex`:
- `linkcolor=blue` → `linkcolor=black` (enlaces internos: índice, referencias a figuras/tablas)
- `citecolor=blue` → `citecolor=black` (citas bibliográficas)
- `urlcolor=blue` → `urlcolor=black` (enlaces externos/URLs)

### Código Anterior
```latex
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue,
    ...
}
```

### Código Nuevo
```latex
% Todos los enlaces en color negro (#000000) para cumplir con el requisito
% WCAG 2.1: Contraste máximo (negro sobre blanco = 21:1, superior al requerido)
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=black,
    ...
}
```

### Consideraciones Importantes
1. **Formato de Documento**: Esto aplica a un documento LaTeX/PDF, **no a una página web**.
2. **Estados no aplicables**: En PDF no hay conceptos de "hover", "active" o "visited" como en CSS/HTML. Los enlaces son simplemente texto negro que se puede hacer clic.
3. **Accesibilidad WCAG 2.1**:
   - Contraste negro sobre blanco: **21:1** (superior al mínimo requerido de 4.5:1 para texto normal)
   - Cumplimiento total con los estándares de accesibilidad
4. **Usabilidad en móviles**: Los enlaces siguen siendo funcionales y se puede hacer clic en ellos en visores de PDF para móviles.

---

## Historial de Modificaciones
| Fecha | Cambio | Archivo |
|-------|--------|---------|
| 2026-05-11 | Enlaces cambiados de azul a negro | `main.tex` |
| 2026-05-11 | Portada actualizada con 5 estudiantes | `secciones/portada.tex` |
| 2026-05-11 | Rutas de imágenes para Overleaf | `secciones/resultados.tex` |
| 2026-05-11 | Configuración para Overleaf | `main.tex` |
