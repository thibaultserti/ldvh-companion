# LDVH Companion 🎲📚

**Votre compagnon numérique pour gérer et suivre vos feuilles d'aventures dans les livres dont vous êtes le héros !**

## 🎯 Description

LDVH Companion est une application web moderne développée avec FastAPI et Python qui vous permet de :

- 📚 **Gérer vos séries** de livres dont vous êtes le héros
- 📖 **Organiser vos tomes** par numéro et description
- 🎲 **Créer des feuilles d'aventures** avec calcul automatique des statistiques
- 📊 **Suivre vos personnages** : Habileté, Endurance, Chance
- 💰 **Gérer votre inventaire** : Or, bijoux, potions, provisions, équipement
- 👹 **Enregistrer vos rencontres** de monstres avec leurs statistiques
- 🎯 **Lancer des dés** intégrés (1d6, 2d6) pour vos parties

## ✨ Fonctionnalités

### 🎲 Outils de Jeu Intégrés
- **Lanceur de dés** : 1d6, 2d6 avec animations
- **Calcul automatique** des statistiques initiales du personnage
- **Validation** des statistiques selon les règles du jeu

### 📚 Gestion des Séries et Livres
- **Interface intuitive** pour créer et modifier des séries
- **Organisation par tomes** avec numérotation automatique
- **Recherche et filtrage** des livres par série

### 🎭 Feuilles d'Aventures Complètes
- **Statistiques du personnage** : Habileté (7-12), Endurance (14-24), Chance (7-12)
- **Inventaire détaillé** : Or, bijoux, potions, provisions, équipement
- **Suivi des rencontres** de monstres avec formatage automatique
- **Notes personnalisées** pour chaque aventure
- **Statut actif/terminé** pour organiser vos parties

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le repository**
   ```bash
   git clone <url-du-repo>
   cd ldvh-companion
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -e .
   ```

4. **Lancer l'application**
   ```bash
   python main.py
   ```

5. **Accéder à l'application**
   Ouvrez votre navigateur et allez sur : http://localhost:8000

## 🏗️ Architecture Technique

### Backend
- **FastAPI** : Framework web moderne et performant
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **Pydantic** : Validation des données et sérialisation
- **SQLite** : Base de données légère et portable

### Frontend
- **Jinja2** : Templates HTML avec héritage
- **Tailwind CSS** : Framework CSS utilitaire
- **JavaScript vanilla** : Interactivité et gestion des formulaires
- **Font Awesome** : Icônes modernes
- **Google Fonts** : Police médiévale "MedievalSharp"

### Structure du Projet
```
ldvh-companion/
├── main.py                          # Point d'entrée de l'application
├── pyproject.toml                   # Configuration du projet et dépendances
├── README.md                        # Documentation du projet
└── src/
    └── ldvh_companion/
        ├── __init__.py              # Package principal
        ├── api.py                   # Routes FastAPI et endpoints
        ├── models.py                # Modèles de données SQLAlchemy et Pydantic
        ├── database.py              # Configuration de la base de données
        ├── utils.py                 # Utilitaires (dés, calculs, validation)
        ├── templates/               # Templates Jinja2
        │   ├── base.html           # Template de base
        │   ├── index.html          # Page d'accueil
        │   ├── series.html         # Gestion des séries
        │   ├── books.html          # Gestion des livres
        │   └── adventure_sheets.html # Feuilles d'aventures
        └── static/                  # Fichiers statiques
            └── css/
                └── custom.css      # Styles personnalisés
```

## 📖 Guide d'Utilisation

### 1. Première Utilisation
- L'application se lance avec des données d'exemple (série "Défis fantastiques")
- Vous pouvez commencer à créer vos propres séries et livres

### 2. Créer une Série
- Allez dans "Séries" depuis le menu
- Cliquez sur "Nouvelle Série"
- Remplissez le nom et la description
- Validez la création

### 3. Ajouter des Livres
- Allez dans "Livres" depuis le menu
- Cliquez sur "Nouveau Livre"
- Sélectionnez la série et le numéro de tome
- Remplissez le titre et la description
- Validez la création

### 4. Créer une Feuille d'Aventure
- Allez dans "Feuilles d'Aventures" depuis le menu
- Cliquez sur "Nouvelle Fiche"
- Sélectionnez le livre et le numéro de tentative
- Remplissez les informations du personnage
- Utilisez "Calculer automatiquement" pour les stats
- Validez la création

### 5. Utiliser les Outils de Jeu
- **Lancer des dés** : Boutons 1d6 et 2d6 sur la page d'accueil
- **Calculer des stats** : Bouton "Calculer Stats" pour un nouveau personnage
- **Gérer l'inventaire** : Modifiez vos feuilles d'aventures en cours

## 🔧 Configuration

### Variables d'Environnement
- `DATABASE_URL` : URL de la base de données (défaut : SQLite locale)

### Personnalisation
- Modifiez `src/ldvh_companion/static/css/custom.css` pour personnaliser l'apparence
- Ajoutez de nouvelles fonctionnalités dans `src/ldvh_companion/utils.py`
- Étendez les modèles dans `src/ldvh_companion/models.py`

## 🧪 Tests

Pour exécuter les tests :
```bash
pip install -e ".[dev]"
pytest
```

## 📝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🤝 Support

Si vous rencontrez des problèmes ou avez des suggestions :
- Ouvrez une issue sur GitHub
- Consultez la documentation des dépendances
- Vérifiez que vous utilisez Python 3.12+

## 🎉 Remerciements

- **FastAPI** pour le framework web exceptionnel
- **Tailwind CSS** pour les styles utilitaires
- **Font Awesome** pour les icônes
- **Google Fonts** pour la police médiévale

---

**Bonne aventure dans vos livres dont vous êtes le héros ! 🎲⚔️📚**
