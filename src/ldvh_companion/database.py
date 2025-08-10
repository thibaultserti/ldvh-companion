"""Configuration de la base de données et gestion des sessions."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ldvh_companion.db")

# Création du moteur de base de données
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Générateur pour obtenir une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Crée toutes les tables de la base de données."""
    from .models import Base

    Base.metadata.create_all(bind=engine)


def init_db() -> None:
    """Initialise la base de données avec des données de base."""
    from .models import Book, Series

    db = SessionLocal()
    try:
        # Vérifier si des séries existent déjà
        if db.query(Series).first() is None:
            # Créer la série "Défis fantastiques"
            defis_fantastiques = Series(
                name="Défis fantastiques", description="Série de livres dont vous êtes le héros"
            )
            db.add(defis_fantastiques)
            db.commit()
            db.refresh(defis_fantastiques)

            # Créer les premiers tomes
            books_data = [
                {
                    "title": "Le Sorcier de la Montagne de Feu",
                    "book_number": 1,
                    "description": "Premier tome de la série Défis fantastiques",
                },
                {
                    "title": "La Citadelle du Chaos",
                    "book_number": 2,
                    "description": "Deuxième tome de la série Défis fantastiques",
                },
                {
                    "title": "La Forêt de la Malédiction",
                    "book_number": 3,
                    "description": "Troisième tome de la série Défis fantastiques",
                },
            ]

            for book_data in books_data:
                book = Book(
                    title=book_data["title"],
                    series_id=defis_fantastiques.id,
                    book_number=book_data["book_number"],
                    description=book_data["description"],
                )
                db.add(book)

            db.commit()
            print("Base de données initialisée avec succès!")
        else:
            print("La base de données contient déjà des données.")

    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        db.rollback()
    finally:
        db.close()
