#!/usr/bin/env python3
"""
Point d'entrée principal de l'application LDVH Companion.

Ce fichier lance le serveur FastAPI avec la configuration appropriée.
"""

import os

import uvicorn

if __name__ == "__main__":
    if os.getenv("ENV") == "dev":
        reload = True
    else:
        reload = False
    print("🚀 Démarrage de LDVH Companion...")
    print("📖 Application accessible sur: http://localhost:8080")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("-" * 50)

    # Lancement du serveur
    uvicorn.run("ldvh_companion.api:app", host="0.0.0.0", port=8080, reload=reload, log_level="info")
