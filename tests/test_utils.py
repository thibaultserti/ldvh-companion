"""Tests pour les utilitaires de l'application."""

import pytest

from src.ldvh_companion.utils import calculate_initial_stats, roll_1d6, roll_2d6, roll_dice, validate_character_stats


class TestDiceRolling:
    """Tests pour les fonctions de lancement de dés."""

    def test_roll_1d6(self):
        """Test que roll_1d6 retourne une valeur entre 1 et 6."""
        result = roll_1d6()
        assert 1 <= result <= 6

    def test_roll_2d6(self):
        """Test que roll_2d6 retourne une valeur entre 2 et 12."""
        result = roll_2d6()
        assert 2 <= result <= 12

    def test_roll_dice_valid(self):
        """Test que roll_dice fonctionne avec des paramètres valides."""
        result = roll_dice(3, 6)
        assert 3 <= result <= 18

    def test_roll_dice_invalid_dice_count(self):
        """Test que roll_dice lève une erreur avec un nombre de dés invalide."""
        with pytest.raises(ValueError, match="Le nombre de dés doit être positif"):
            roll_dice(0, 6)

    def test_roll_dice_invalid_sides(self):
        """Test que roll_dice lève une erreur avec un nombre de faces invalide."""
        with pytest.raises(ValueError, match="le nombre de faces >= 2"):
            roll_dice(1, 1)


class TestCharacterStats:
    """Tests pour les fonctions de statistiques de personnage."""

    def test_calculate_initial_stats(self):
        """Test que calculate_initial_stats retourne des valeurs valides."""
        skill, stamina, luck = calculate_initial_stats()

        # Vérifier les plages de valeurs
        assert 7 <= skill <= 12
        assert 14 <= stamina <= 24
        assert 7 <= luck <= 12

    def test_validate_character_stats_valid(self):
        """Test que validate_character_stats accepte des statistiques valides."""
        assert validate_character_stats(8, 16, 9) is True
        assert validate_character_stats(7, 14, 7) is True
        assert validate_character_stats(12, 24, 12) is True

    def test_validate_character_stats_invalid_skill(self):
        """Test que validate_character_stats rejette une habileté invalide."""
        assert validate_character_stats(6, 16, 9) is False  # Trop bas
        assert validate_character_stats(13, 16, 9) is False  # Trop haut

    def test_validate_character_stats_invalid_stamina(self):
        """Test que validate_character_stats rejette une endurance invalide."""
        assert validate_character_stats(8, 13, 9) is False  # Trop bas
        assert validate_character_stats(8, 25, 9) is False  # Trop haut

    def test_validate_character_stats_invalid_luck(self):
        """Test que validate_character_stats rejette une chance invalide."""
        assert validate_character_stats(8, 16, 6) is False  # Trop bas
        assert validate_character_stats(8, 16, 13) is False  # Trop haut
