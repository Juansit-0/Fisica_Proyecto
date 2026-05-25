#!/usr/bin/env python3
"""
Script para analizar el contenido del PDF del proyecto
"""

from pathlib import Path
import sys

# Agregar directorio al path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def extraer_texto_pdf(ruta_pdf):
    """Intenta extraer texto de un PDF usando diferentes métodos"""
    try:
        import PyPDF2
        texto = ""
        with open(ruta_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texto += page.extract_text() + "\n"
        return texto
    except ImportError:
        print("PyPDF2 no está instalado. Instalando...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2"], check=True)
        return extraer_texto_pdf(ruta_pdf)
    except Exception as e:
        print(f"Error al extraer texto: {e}")
        return None

def main():
    pdf_path = PROJECT_ROOT / "Recursos" / "Proyecto_fisica_III.pdf"
    
    if not pdf_path.exists():
        print(f"ERROR: No se encontró el archivo {pdf_path}")
        return 1
    
    print("=" * 80)
    print(f"ANÁLISIS DEL ARCHIVO: {pdf_path.name}")
    print("=" * 80)
    print()
    
    texto = extraer_texto_pdf(pdf_path)
    if texto:
        print("CONTENIDO DEL PDF:")
        print("-" * 80)
        print(texto)
        print("-" * 80)
    else:
        print("No se pudo extraer el texto del PDF.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
