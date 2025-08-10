# Changelog - LDVH Companion

## Version 0.2.0 - Modifications des feuilles d'aventure

### Modifications apportées

#### 1. Suppression du nom du personnage obligatoire
- Le nom du personnage n'est plus requis lors de la création d'une fiche
- Le champ est maintenant optionnel avec un placeholder "Laissez vide pour l'instant"

#### 2. Numéro de tentative automatique
- Le numéro de tentative est maintenant calculé automatiquement
- L'utilisateur ne peut plus le modifier (champ en lecture seule)
- Affichage d'un message "Calculé automatiquement"

#### 3. Suppression de la section rencontres de monstres
- La section "Rencontres de monstres" a été supprimée du formulaire de création
- Les rencontres sont maintenant gérées uniquement en mode jeu

#### 4. Nouvelle vue de jeu
- Ajout d'une nouvelle route `/adventure-sheets/{sheet_id}/game`
- Nouveau template `adventure_sheet_game.html` pour l'utilisation pendant le jeu
- Bouton "Mode jeu" (icône gamepad) ajouté à chaque fiche dans la liste

#### 5. Séparation des statistiques initiales et courantes
- **Statistiques initiales** (non modifiables) :
  - `initial_skill` : Habileté de départ
  - `initial_stamina` : Endurance de départ
  - `initial_luck` : Chance de départ
- **Statistiques courantes** (modifiables pendant le jeu) :
  - `current_skill` : Habileté actuelle
  - `current_stamina` : Endurance actuelle
  - `current_luck` : Chance actuelle

#### 6. Gestion des rencontres de monstres en mode jeu
- Formulaire dynamique pour ajouter/supprimer des rencontres
- Champs pour chaque rencontre :
  - Nom du monstre
  - Numéro de paragraphe de rencontre
  - Habileté du monstre
  - Endurance du monstre
- Sauvegarde automatique des rencontres au format JSON

#### 7. Interface de jeu améliorée
- Tous les champs sont modifiables sauf les statistiques initiales
- Bouton de sauvegarde pour conserver les modifications
- Navigation entre la liste des fiches et le mode jeu
- Affichage des statistiques initiales et courantes côte à côte

### Modifications techniques

#### Modèles de données
- `AdventureSheet` : Ajout des champs `initial_*` et `current_*`
- `AdventureSheetCreate` : Mise à jour pour les nouveaux champs
- `AdventureSheetUpdate` : Mise à jour pour les statistiques courantes
- `AdventureSheetResponse` : Mise à jour pour tous les nouveaux champs

#### API
- Nouvelle route GET `/adventure-sheets/{sheet_id}/game`
- Mise à jour de la création automatique des statistiques courantes
- Gestion automatique du numéro de tentative

#### Templates
- `adventure_sheets.html` : Suppression des champs non désirés
- `adventure_sheet_game.html` : Nouveau template pour le mode jeu
- Amélioration de l'affichage des statistiques

### Migration de la base de données
- Script de migration automatique pour les bases existantes
- Conversion des anciens champs `skill`, `stamina`, `luck` vers les nouveaux
- Conservation des données existantes

### Utilisation

#### Création d'une fiche
1. Sélectionner la série et le livre
2. Le numéro de tentative est calculé automatiquement
3. Les statistiques peuvent être calculées automatiquement ou saisies manuellement
4. Le nom du personnage est optionnel

#### Mode jeu
1. Cliquer sur l'icône gamepad (🎮) d'une fiche
2. Modifier les statistiques courantes selon l'évolution du jeu
3. Ajouter les rencontres de monstres au fur et à mesure
4. Sauvegarder régulièrement les modifications
5. Retourner à la liste des fiches via le bouton "Retour aux fiches"

### Compatibilité
- Les anciennes fiches sont automatiquement migrées
- Toutes les fonctionnalités existantes sont préservées
- Interface rétrocompatible avec les données existantes
