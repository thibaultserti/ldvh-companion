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


def get_next_attempt_number(book_id: int, db_session: "Session") -> int:
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


# Fonctions pour le système de combat
def start_combat(
    monster_name: str,
    monster_skill: int,
    monster_stamina: int,
    player_skill: int,
    player_stamina: int,
    player_luck: int,
) -> "CombatState":
    """Commence un nouveau combat.

    Args:
        monster_name: Nom du monstre
        monster_skill: Habileté du monstre
        monster_stamina: Endurance du monstre
        player_skill: Habileté du joueur
        player_stamina: Endurance actuelle du joueur
        player_luck: Chance actuelle du joueur

    Returns:
        État initial du combat
    """
    from .models import CombatState

    return CombatState(
        monster_name=monster_name,
        monster_skill=monster_skill,
        monster_stamina=monster_stamina,
        monster_max_stamina=monster_stamina,
        player_skill=player_skill,
        player_stamina=player_stamina,
        player_luck=player_luck,
        player_max_luck=player_luck,
        round_number=1,
        is_active=True,
        winner=None,
    )


def execute_combat_round(
    combat_state: "CombatState", attempt_luck: bool = False
) -> tuple["CombatRoundResult", "CombatState"]:
    """Exécute un round de combat.

    Args:
        combat_state: État actuel du combat
        attempt_luck: Si le joueur tente sa chance

    Returns:
        Résultat du round de combat et nouvel état
    """
    from .models import CombatRoundResult, CombatState

    # Lancer les dés pour le joueur et le monstre
    player_dice = [roll_1d6(), roll_1d6()]
    monster_dice = [roll_1d6(), roll_1d6()]

    # Calculer les forces d'attaque
    player_attack_strength = combat_state.player_skill + sum(player_dice)
    monster_attack_strength = combat_state.monster_skill + sum(monster_dice)

    # Déterminer le gagnant du round
    if player_attack_strength > monster_attack_strength:
        round_winner = "player"
    elif monster_attack_strength > player_attack_strength:
        round_winner = "monster"
    else:
        round_winner = "draw"

    # Initialiser les dégâts
    damage_to_player = 0
    damage_to_monster = 0

    # Calculer les dégâts de base
    if round_winner == "player":
        damage_to_monster = 2
    elif round_winner == "monster":
        damage_to_player = 2

    # Gérer le test de chance
    luck_attempted = attempt_luck
    luck_dice = None
    luck_success = None
    player_luck_after = combat_state.player_luck

    if attempt_luck and combat_state.player_luck > 0:
        luck_dice = [roll_1d6(), roll_1d6()]
        luck_total = sum(luck_dice)
        luck_success = luck_total <= combat_state.player_luck
        player_luck_after = max(0, combat_state.player_luck - 1)  # Réduire la chance de 1

        if luck_success:
            if round_winner == "player":
                # Si le joueur a gagné le round et réussit sa chance, 1 blessure de plus
                damage_to_monster += 1
            elif round_winner == "monster":
                # Si le joueur a perdu le round et réussit sa chance, 1 blessure de moins
                damage_to_player = max(0, damage_to_player - 1)
        else:
            # Échec du test de chance - effet inverse
            if round_winner == "player":
                # Si le joueur a gagné mais échoue sa chance, 1 blessure de moins
                damage_to_monster = max(0, damage_to_monster - 1)
            elif round_winner == "monster":
                # Si le joueur a perdu et échoue sa chance, 1 blessure de plus
                damage_to_player += 1

    # Appliquer les dégâts
    player_stamina_after = max(0, combat_state.player_stamina - damage_to_player)
    monster_stamina_after = max(0, combat_state.monster_stamina - damage_to_monster)

    # Vérifier si le combat est terminé
    combat_ended = player_stamina_after <= 0 or monster_stamina_after <= 0
    combat_winner = None

    if combat_ended:
        if player_stamina_after <= 0 and monster_stamina_after <= 0:
            combat_winner = "draw"
        elif player_stamina_after <= 0:
            combat_winner = "monster"
        else:
            combat_winner = "player"

    # Créer le résultat du round
    round_result = CombatRoundResult(
        round_number=combat_state.round_number,
        player_dice=player_dice,
        monster_dice=monster_dice,
        player_attack_strength=player_attack_strength,
        monster_attack_strength=monster_attack_strength,
        winner=round_winner,
        luck_attempted=luck_attempted,
        luck_dice=luck_dice,
        luck_success=luck_success,
        damage_to_player=damage_to_player,
        damage_to_monster=damage_to_monster,
        player_stamina_after=player_stamina_after,
        monster_stamina_after=monster_stamina_after,
        player_luck_after=player_luck_after,
        combat_ended=combat_ended,
        combat_winner=combat_winner,
    )

    # Mettre à jour l'état du combat
    new_combat_state = CombatState(
        monster_name=combat_state.monster_name,
        monster_skill=combat_state.monster_skill,
        monster_stamina=monster_stamina_after,
        monster_max_stamina=combat_state.monster_max_stamina,
        player_skill=combat_state.player_skill,
        player_stamina=player_stamina_after,
        player_luck=player_luck_after,
        player_max_luck=combat_state.player_max_luck,
        round_number=combat_state.round_number + 1,
        is_active=not combat_ended,
        winner=combat_winner,
    )

    return round_result, new_combat_state
