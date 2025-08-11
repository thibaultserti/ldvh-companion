"""Modèles de données pour l'application LDVH Companion."""

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Series(Base):
    """Modèle pour une série de livres."""

    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    books = relationship("Book", back_populates="series", cascade="all, delete-orphan")


class Book(Base):
    """Modèle pour un tome de la série."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    book_number = Column(Integer, nullable=False)  # Numéro du tome dans la série
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    series = relationship("Series", back_populates="books")
    adventure_sheets = relationship("AdventureSheet", back_populates="book", cascade="all, delete-orphan")


class AdventureSheet(Base):
    """Modèle pour une feuille d'aventure."""

    __tablename__ = "adventure_sheets"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)  # Numéro de la tentative
    character_name = Column(String(100), nullable=True)

    # Statistiques de base (initiales)
    initial_skill = Column(Integer, nullable=False)
    initial_stamina = Column(Integer, nullable=False)
    initial_luck = Column(Integer, nullable=False)

    # Statistiques courantes (modifiables pendant le jeu)
    current_skill = Column(Integer, nullable=False)
    current_stamina = Column(Integer, nullable=False)
    current_luck = Column(Integer, nullable=False)

    # Inventaire
    gold = Column(Integer, default=0)
    jewelry = Column(Text, nullable=True)
    potions = Column(Text, nullable=True)
    provisions = Column(Text, nullable=True)
    equipment = Column(Text, nullable=True)

    # Monstres rencontrés (JSON stocké en texte)
    monster_encounters = Column(Text, nullable=True)

    # États des combats actifs (JSON stocké en texte)
    active_combats = Column(Text, nullable=True)

    # Historique des combats terminés (JSON stocké en texte)
    combat_history = Column(Text, nullable=True)

    # Métadonnées
    is_active = Column(Boolean, default=True)  # Fiche active ou terminée
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    book = relationship("Book", back_populates="adventure_sheets")


# Modèles Pydantic pour l'API
class SeriesCreate(BaseModel):
    """Modèle pour créer une série."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class SeriesResponse(BaseModel):
    """Modèle de réponse pour une série."""

    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    """Modèle pour créer un livre."""

    title: str = Field(..., min_length=1, max_length=200)
    series_id: int
    book_number: int = Field(..., gt=0)
    description: str | None = None


class BookResponse(BaseModel):
    """Modèle de réponse pour un livre."""

    id: int
    title: str
    series_id: int
    book_number: int
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdventureSheetCreate(BaseModel):
    """Modèle pour créer une feuille d'aventure."""

    book_id: int
    attempt_number: int | None = None  # Si None, sera calculé automatiquement
    character_name: str | None = None
    initial_skill: int | None = None  # Si None, sera calculé automatiquement
    initial_stamina: int | None = None  # Si None, sera calculé automatiquement
    initial_luck: int | None = None  # Si None, sera calculé automatiquement


class AdventureSheetUpdate(BaseModel):
    """Modèle pour mettre à jour une feuille d'aventure."""

    character_name: str | None = None
    current_skill: int | None = None
    current_stamina: int | None = None
    current_luck: int | None = None
    gold: int | None = None
    jewelry: str | None = None
    potions: str | None = None
    provisions: str | None = None
    equipment: str | None = None
    monster_encounters: str | None = None
    active_combats: str | None = None
    combat_history: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class AdventureSheetResponse(BaseModel):
    """Modèle de réponse pour une feuille d'aventure."""

    id: int
    book_id: int
    attempt_number: int
    character_name: str | None = None
    initial_skill: int
    initial_stamina: int
    initial_luck: int
    current_skill: int
    current_stamina: int
    current_luck: int
    gold: int
    jewelry: str | None = None
    potions: str | None = None
    provisions: str | None = None
    equipment: str | None = None
    monster_encounters: str | None = None
    active_combats: str | None = None
    combat_history: str | None = None
    is_active: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiceRoll(BaseModel):
    """Modèle pour un lancer de dés."""

    dice_count: int = Field(..., ge=1, le=10)
    sides: int = Field(default=6, ge=2, le=100)


# Modèles pour le système de combat
class CombatState(BaseModel):
    """État d'un combat en cours."""

    monster_name: str
    monster_skill: int
    monster_stamina: int
    monster_max_stamina: int

    player_skill: int
    player_stamina: int
    player_luck: int
    player_max_luck: int

    round_number: int = 1
    is_active: bool = True
    winner: str | None = None  # "player", "monster", ou None si combat en cours


class CombatRoundResult(BaseModel):
    """Résultat d'un round de combat."""

    round_number: int

    # Lancer de dés
    player_dice: list[int]
    monster_dice: list[int]

    # Force d'attaque calculée
    player_attack_strength: int
    monster_attack_strength: int

    # Résultat du round
    winner: str  # "player", "monster", "draw"

    # Test de chance (si applicable)
    luck_attempted: bool = False
    luck_dice: list[int] | None = None
    luck_success: bool | None = None

    # Dégâts infligés
    damage_to_player: int = 0
    damage_to_monster: int = 0

    # État après le round
    player_stamina_after: int
    monster_stamina_after: int
    player_luck_after: int

    # Combat terminé ?
    combat_ended: bool = False
    combat_winner: str | None = None


class CombatAction(BaseModel):
    """Action du joueur pour un round de combat."""

    attempt_luck: bool = False


class CombatStart(BaseModel):
    """Données pour commencer un combat."""

    monster_name: str
    monster_skill: int
    monster_stamina: int
