#!/usr/bin/env python3
"""
Point d'entrée principal de l'application LDVH Companion.

Ce fichier lance le serveur FastAPI avec la configuration appropriée.
"""

import uvicorn

if __name__ == "__main__":
    # Configuration du serveur
    config = {
        "host": "0.0.0.0",  # Écoute sur toutes les interfaces
        "port": 8080,  # Port par défaut
        "reload": True,  # Rechargement automatique en développement
        "log_level": "info",  # Niveau de log
    }

    print("🚀 Démarrage de LDVH Companion...")
    print(f"📖 Application accessible sur: http://localhost:{config['port']}")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("-" * 50)

    # Lancement du serveur
    uvicorn.run("src.ldvh_companion.api:app", **config)
