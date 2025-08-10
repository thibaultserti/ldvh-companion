"""Utilitaires pour l'application LDVH Companion."""

import random


def roll_dice(dice_count: int, sides: int = 6) -> int:
    """Lance un nombre donné de dés avec un nombre de faces spécifié.

    Args:
        dice_count: Nombre de dés à lancer
        sides: Nombre de faces par dé (défaut: 6)

    Returns:
        Somme des résultats des dés
    """
    if dice_count <= 0 or sides < 2:
        raise ValueError("Le nombre de dés doit être positif et le nombre de faces >= 2")

    return sum(random.randint(1, sides) for _ in range(dice_count))


def roll_1d6() -> int:
    """Lance 1d6."""
    return roll_dice(1, 6)


def roll_2d6() -> int:
    """Lance 2d6."""
    return roll_dice(2, 6)


def calculate_initial_stats() -> tuple[int, int, int]:
    """Calcule les statistiques initiales d'un personnage.

    Returns:
        Tuple (skill, stamina, luck) avec les valeurs calculées
    """
    skill = 6 + roll_1d6()  # 6 + 1d6
    stamina = 12 + roll_2d6()  # 12 + 2d6
    luck = 6 + roll_1d6()  # 6 + 1d6

    return skill, stamina, luck


def format_monster_encounters(encounters: list[dict]) -> str:
    """Formate la liste des rencontres de monstres en texte.

    Args:
        encounters: Liste des rencontres de monstres

    Returns:
        Texte formaté des rencontres
    """
    if not encounters:
        return ""

    formatted = []
    for i, encounter in enumerate(encounters, 1):
        skill = encounter.get("skill", "?")
        stamina = encounter.get("stamina", "?")
        name = encounter.get("name", f"Monstre {i}")
        formatted.append(f"{name}: Habileté={skill}, Endurance={stamina}")

    return "\n".join(formatted)


def parse_monster_encounters(text: str) -> list[dict]:
    """Parse le texte des rencontres de monstres en liste de dictionnaires.

    Args:
        text: Texte formaté des rencontres

    Returns:
        Liste des rencontres de monstres
    """
    if not text.strip():
        return []

    encounters = []
    lines = text.strip().split("\n")

    for line in lines:
        if ":" in line and "=" in line:
            parts = line.split(":")
            name = parts[0].strip()

            stats_part = parts[1].strip()
            skill = stamina = "?"

            if "Habileté=" in stats_part:
                skill = stats_part.split("Habileté=")[1].split(",")[0].strip()
            if "Endurance=" in stats_part:
                stamina = stats_part.split("Endurance=")[1].strip()

            encounters.append({"name": name, "skill": skill, "stamina": stamina})

    return encounters


def validate_character_stats(skill: int, stamina: int, luck: int) -> bool:
    """Valide que les statistiques du personnage sont dans des limites raisonnables.

    Args:
        skill: Valeur d'habileté
        stamina: Valeur d'endurance
        luck: Valeur de chance

    Returns:
        True si les statistiques sont valides, False sinon
    """
    # Habileté: 6 + 1d6 = 7-12
    if not (7 <= skill <= 12):
        return False

    # Endurance: 12 + 2d6 = 14-24
    if not (14 <= stamina <= 24):
        return False

    # Chance: 6 + 1d6 = 7-12
    if not (7 <= luck <= 12):
        return False

    return True


def get_next_attempt_number(book_id: int, db_session) -> int:
    """Obtient le prochain numéro de tentative pour un livre donné.

    Args:
        book_id: ID du livre
        db_session: Session de base de données

    Returns:
        Prochain numéro de tentative
    """
    from .models import AdventureSheet

    max_attempt = (
        db_session.query(AdventureSheet.attempt_number)
        .filter(AdventureSheet.book_id == book_id)
        .order_by(AdventureSheet.attempt_number.desc())
        .first()
    )

    if max_attempt is None:
        return 1

    return max_attempt[0] + 1
