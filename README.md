# AniVerse (PC)

AniVerse es una aplicacion de escritorio en Python para descubrir y organizar anime con catalogo local en SQLite.

Estado del proyecto: finalizado para PC.

## Version final

- Version: v0.9.0
- Plataforma objetivo: Windows (PC)
- Paquete definitivo: dist/AniVerse-PC-definitivo.zip

## Contenido del ZIP definitivo

- AniVerse.exe
- _internal/assets/
- _internal/database/anime.db

## Ejecucion

1. Extrae dist/AniVerse-PC-definitivo.zip.
2. Ejecuta AniVerse.exe.

## Build local de PC

Comando:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build.ps1
```

Salida:

- dist/AniVerse/AniVerse.exe

## Instalador opcional (Windows)

El proyecto incluye el script de Inno Setup para generar instalador:

- packaging/AniVerse.iss

## Arquitectura

- UI: PySide6
- Datos: SQLite local
- Catalogo: 1000 registros locales
- Funciones principales: Home, Search, Random, Favorites, Lists, Details

## Nota de cierre

El alcance Android/APK fue retirado del repositorio para dejar una entrega estable y final de escritorio.
