# FabiCoin

FabiCoin es una implementación básica y limpia de una blockchain y sistema de billetera (wallet) en Python, estructurada siguiendo principios de arquitectura limpia (Clean Architecture).

Este es un repositorio público y educativo.

## Características

- **Block (Bloque)**: Contiene el índice, timestamp, datos, hash previo, nonce y hash actual. Incluye lógica de hashing determinista basada en SHA-256 y prueba de trabajo (Proof of Work) mediante minado con dificultad variable.
- **Blockchain**: Mantiene la cadena de bloques, crea el bloque Génesis, añade bloques minados y permite verificar la validez e integridad de toda la cadena.
- **Wallet (Billetera)**: Maneja balances, depósitos y retiros con control de fondos insuficientes.
- **Estructura Limpia**: Separación de responsabilidades con un diseño extensible.
- **Pruebas Automatizadas**: Suite completa de pruebas unitarias escritas con `pytest`.

## Requisitos

- Python 3.12 o superior.

## Instalación y Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Fabian0594/FabiCoin.git
   cd FabiCoin
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows (cmd):
   .venv\Scripts\activate.bat
   # En Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # En macOS/Linux:
   source .venv/bin/activate
   ```

3. Instalar las dependencias de desarrollo:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución de Pruebas

Para correr la suite de pruebas unitarias con `pytest`:

```bash
pytest
```

## Calidad de Código y Formateo

El proyecto utiliza las siguientes herramientas para asegurar la calidad de código:
- **Ruff**: Linter rápido de Python para detectar errores de estilo y bugs.
- **Black**: Formateador de código automático y determinista.

Para revisar y corregir el estilo del código:
```bash
# Ejecutar Ruff linter
ruff check .

# Formatear código con Black
black .
```

## Recomendaciones de Seguridad

- **No guardes credenciales**: Nunca expongas llaves privadas de producción, contraseñas ni archivos `.env` en este repositorio.
- **Entorno virtual excluido**: El archivo `.gitignore` configurado evita subir el entorno virtual (`.venv`), cachés de pruebas (`.pytest_cache`), cachés del linter (`.ruff_cache`) y otros archivos temporales generados localmente.
