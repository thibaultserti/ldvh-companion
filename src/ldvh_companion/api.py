"""API principale de l'application LDVH Companion."""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import create_tables, get_db, init_db
from .models import (
    AdventureSheet,
    AdventureSheetCreate,
    AdventureSheetResponse,
    AdventureSheetUpdate,
    Book,
    BookCreate,
    BookResponse,
    CombatAction,
    CombatStart,
    CombatState,
    DiceRoll,
    Series,
    SeriesCreate,
    SeriesResponse,
)
from .utils import (
    calculate_initial_stats,
    execute_combat_round,
    get_next_attempt_number,
    parse_monster_encounters,
    roll_1d6,
    roll_2d6,
    start_combat,
    validate_character_stats,
)

# Création de l'application FastAPI
app = FastAPI(
    title="LDVH Companion",
    description="Application de suivi des feuilles d'aventures de livres dont vous êtes le héros",
    version="0.1.0",
)

# Configuration des templates et fichiers statiques
templates = Jinja2Templates(directory="src/ldvh_companion/templates")
app.mount("/static", StaticFiles(directory="src/ldvh_companion/static"), name="static")


# Routes pour l'interface web
@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Page d'accueil de l'application."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/series", response_class=HTMLResponse)
async def series_page(request: Request) -> HTMLResponse:
    """Page de gestion des séries."""
    return templates.TemplateResponse("series.html", {"request": request})


@app.get("/books", response_class=HTMLResponse)
async def books_page(request: Request) -> HTMLResponse:
    """Page de gestion des livres."""
    return templates.TemplateResponse("books.html", {"request": request})


@app.get("/adventure-sheets", response_class=HTMLResponse)
async def adventure_sheets_page(request: Request) -> HTMLResponse:
    """Page de gestion des feuilles d'aventures."""
    return templates.TemplateResponse("adventure_sheets.html", {"request": request})


@app.get("/adventure-sheets/{sheet_id}/game", response_class=HTMLResponse)
async def adventure_sheet_game_page(request: Request, sheet_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    """Page de jeu d'une feuille d'aventure."""
    sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")

    book = db.query(Book).filter(Book.id == sheet.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    series = db.query(Series).filter(Series.id == book.series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Série non trouvée")

    # Parser les rencontres de monstres
    monster_encounters = []
    if sheet.monster_encounters:
        try:
            monster_encounters = parse_monster_encounters(sheet.monster_encounters or "")
        except:
            monster_encounters = []

    context = {
        "request": request,
        "id": sheet.id,
        "book_id": sheet.book_id,
        "attempt_number": sheet.attempt_number,
        "character_name": sheet.character_name,
        "initial_skill": sheet.initial_skill,
        "initial_stamina": sheet.initial_stamina,
        "initial_luck": sheet.initial_luck,
        "current_skill": sheet.current_skill,
        "current_stamina": sheet.current_stamina,
        "current_luck": sheet.current_luck,
        "gold": sheet.gold,
        "jewelry": sheet.jewelry,
        "potions": sheet.potions,
        "provisions": sheet.provisions,
        "equipment": sheet.equipment,
        "monster_encounters": monster_encounters,
        "active_combats": sheet.active_combats if sheet.active_combats else "{}",
        "combat_history": sheet.combat_history if sheet.combat_history else "[]",
        "is_active": sheet.is_active,
        "notes": sheet.notes,
        "series_name": series.name,
        "book_title": book.title,
    }

    return templates.TemplateResponse("adventure_sheet_game.html", context)


# API Endpoints


# Séries
@app.post("/api/series", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
async def create_series(series: SeriesCreate, db: Session = Depends(get_db)) -> SeriesResponse:
    """Crée une nouvelle série."""
    db_series = Series(**series.dict())
    db.add(db_series)
    db.commit()
    db.refresh(db_series)
    return db_series


@app.get("/api/series", response_model=list[SeriesResponse])
async def get_series(db: Session = Depends(get_db)) -> list[SeriesResponse]:
    """Récupère toutes les séries."""
    return db.query(Series).all()


@app.get("/api/series/{series_id}", response_model=SeriesResponse)
async def get_series_by_id(series_id: int, db: Session = Depends(get_db)) -> SeriesResponse:
    """Récupère une série par son ID."""
    series = db.query(Series).filter(Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Série non trouvée")
    return series


@app.put("/api/series/{series_id}", response_model=SeriesResponse)
async def update_series(series_id: int, series_update: SeriesCreate, db: Session = Depends(get_db)) -> SeriesResponse:
    """Met à jour une série."""
    db_series = db.query(Series).filter(Series.id == series_id).first()
    if not db_series:
        raise HTTPException(status_code=404, detail="Série non trouvée")

    # Mettre à jour les champs fournis
    db_series.name = series_update.name
    db_series.description = series_update.description

    db.commit()
    db.refresh(db_series)
    return db_series


@app.delete("/api/series/{series_id}")
async def delete_series(series_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Supprime une série."""
    db_series = db.query(Series).filter(Series.id == series_id).first()
    if not db_series:
        raise HTTPException(status_code=404, detail="Série non trouvée")

    db.delete(db_series)
    db.commit()
    return {"message": "Série supprimée avec succès"}


# Livres
@app.post("/api/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)) -> BookResponse:
    """Crée un nouveau livre."""
    # Vérifier que la série existe
    series = db.query(Series).filter(Series.id == book.series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Série non trouvée")

    # Vérifier que le numéro de tome n'existe pas déjà pour cette série
    existing_book = (
        db.query(Book).filter(Book.series_id == book.series_id, Book.book_number == book.book_number).first()
    )
    if existing_book:
        raise HTTPException(status_code=400, detail="Ce numéro de tome existe déjà pour cette série")

    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/api/books", response_model=list[BookResponse])
async def get_books(series_id: int | None = None, db: Session = Depends(get_db)) -> list[BookResponse]:
    """Récupère tous les livres, optionnellement filtrés par série."""
    query = db.query(Book)
    if series_id:
        query = query.filter(Book.series_id == series_id)
    return query.all()


@app.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book_by_id(book_id: int, db: Session = Depends(get_db)) -> BookResponse:
    """Récupère un livre par son ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book


@app.put("/api/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book_update: BookCreate, db: Session = Depends(get_db)) -> BookResponse:
    """Met à jour un livre."""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Vérifier que la série existe
    series = db.query(Series).filter(Series.id == book_update.series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Série non trouvée")

    # Vérifier que le numéro de tome n'existe pas déjà pour cette série (sauf pour ce livre)
    existing_book = (
        db.query(Book)
        .filter(
            Book.series_id == book_update.series_id, Book.book_number == book_update.book_number, Book.id != book_id
        )
        .first()
    )
    if existing_book:
        raise HTTPException(status_code=400, detail="Ce numéro de tome existe déjà pour cette série")

    # Mettre à jour les champs fournis
    db_book.title = book_update.title
    db_book.series_id = book_update.series_id
    db_book.book_number = book_update.book_number
    db_book.description = book_update.description

    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/api/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Supprime un livre."""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    db.delete(db_book)
    db.commit()
    return {"message": "Livre supprimé avec succès"}


# Feuilles d'aventures
@app.post("/api/adventure-sheets", response_model=AdventureSheetResponse, status_code=status.HTTP_201_CREATED)
async def create_adventure_sheet(sheet: AdventureSheetCreate, db: Session = Depends(get_db)) -> AdventureSheetResponse:
    """Crée une nouvelle feuille d'aventure."""
    # Vérifier que le livre existe
    book = db.query(Book).filter(Book.id == sheet.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Obtenir le prochain numéro de tentative automatiquement
    sheet.attempt_number = get_next_attempt_number(sheet.book_id, db)

    # Calculer les statistiques initiales si non fournies
    if sheet.initial_skill is None or sheet.initial_stamina is None or sheet.initial_luck is None:
        skill, stamina, luck = calculate_initial_stats()
        sheet.initial_skill = skill
        sheet.initial_stamina = stamina
        sheet.initial_luck = luck

    # Valider les statistiques initiales
    if not validate_character_stats(sheet.initial_skill, sheet.initial_stamina, sheet.initial_luck):
        raise HTTPException(status_code=400, detail="Statistiques du personnage invalides")

    # Créer la feuille avec les statistiques courantes égales aux initiales
    db_sheet = AdventureSheet(
        book_id=sheet.book_id,
        attempt_number=sheet.attempt_number,
        character_name=sheet.character_name,
        initial_skill=sheet.initial_skill,
        initial_stamina=sheet.initial_stamina,
        initial_luck=sheet.initial_luck,
        current_skill=sheet.initial_skill,
        current_stamina=sheet.initial_stamina,
        current_luck=sheet.initial_luck,
        gold=0,
        jewelry=None,
        potions=None,
        provisions=None,
        equipment=None,
        monster_encounters=None,
        active_combats=None,
        combat_history=None,
        is_active=True,
        notes=None,
    )

    db.add(db_sheet)
    db.commit()
    db.refresh(db_sheet)
    return db_sheet


@app.get("/api/adventure-sheets", response_model=list[AdventureSheetResponse])
async def get_adventure_sheets(
    book_id: int | None = None, db: Session = Depends(get_db)
) -> list[AdventureSheetResponse]:
    """Récupère toutes les feuilles d'aventures, optionnellement filtrées par livre."""
    query = db.query(AdventureSheet)
    if book_id:
        query = query.filter(AdventureSheet.book_id == book_id)
    return query.order_by(AdventureSheet.attempt_number.desc()).all()


@app.get("/api/adventure-sheets/{sheet_id}", response_model=AdventureSheetResponse)
async def get_adventure_sheet_by_id(sheet_id: int, db: Session = Depends(get_db)) -> AdventureSheetResponse:
    """Récupère une feuille d'aventure par son ID."""
    sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")
    return sheet


@app.put("/api/adventure-sheets/{sheet_id}", response_model=AdventureSheetResponse)
async def update_adventure_sheet(
    sheet_id: int, sheet_update: AdventureSheetUpdate, db: Session = Depends(get_db)
) -> AdventureSheetResponse:
    """Met à jour une feuille d'aventure."""
    db_sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not db_sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")

    # Mettre à jour les champs fournis
    update_data = sheet_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sheet, field, value)

    db.commit()
    db.refresh(db_sheet)
    return db_sheet


@app.delete("/api/adventure-sheets/{sheet_id}")
async def delete_adventure_sheet(sheet_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Supprime une feuille d'aventure."""
    db_sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not db_sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")

    db.delete(db_sheet)
    db.commit()
    return {"message": "Feuille d'aventure supprimée avec succès"}


# Utilitaires pour les dés
@app.post("/api/dice/roll")
async def roll_dice_endpoint(dice_roll: DiceRoll) -> dict:
    """Lance des dés selon la configuration spécifiée."""
    from .utils import roll_dice

    result = roll_dice(dice_roll.dice_count, dice_roll.sides)
    return {
        "dice_count": dice_roll.dice_count,
        "sides": dice_roll.sides,
        "result": result,
        "rolls": [roll_dice(1, dice_roll.sides) for _ in range(dice_roll.dice_count)],
    }


@app.post("/api/dice/1d6")
async def roll_1d6_endpoint() -> dict:
    """Lance 1d6."""
    result = roll_1d6()
    return {"dice": "1d6", "result": result}


@app.post("/api/dice/2d6")
async def roll_2d6_endpoint() -> dict:
    """Lance 2d6."""
    result = roll_2d6()
    rolls = [roll_1d6() for _ in range(2)]
    return {"dice": "2d6", "result": result, "rolls": rolls}


@app.post("/api/dice/calculate-stats")
async def calculate_stats_endpoint() -> dict:
    """Calcule les statistiques initiales d'un personnage."""
    skill, stamina, luck = calculate_initial_stats()
    return {
        "skill": skill,
        "stamina": stamina,
        "luck": luck,
        "skill_roll": skill - 6,
        "stamina_roll": stamina - 12,
        "luck_roll": luck - 6,
    }


# Endpoints pour le système de combat
@app.post("/api/combat/start", response_model=CombatState)
async def start_combat_endpoint(combat_start: CombatStart, sheet_id: int, db: Session = Depends(get_db)) -> CombatState:
    """Commence un nouveau combat avec un monstre."""
    # Récupérer la feuille d'aventure pour obtenir les stats du joueur
    sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")

    # Commencer le combat
    combat_state = start_combat(
        monster_name=combat_start.monster_name,
        monster_skill=combat_start.monster_skill,
        monster_stamina=combat_start.monster_stamina,
        player_skill=sheet.current_skill,
        player_stamina=sheet.current_stamina,
        player_luck=sheet.current_luck,
    )

    return combat_state


@app.post("/api/combat/round")
async def execute_combat_round_endpoint(
    combat_state: CombatState, action: CombatAction, sheet_id: int, db: Session = Depends(get_db)
) -> dict:
    """Exécute un round de combat."""
    # Vérifier que la feuille d'aventure existe
    sheet = db.query(AdventureSheet).filter(AdventureSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Feuille d'aventure non trouvée")

    # Exécuter le round de combat
    round_result, new_combat_state = execute_combat_round(combat_state=combat_state, attempt_luck=action.attempt_luck)

    # Mettre à jour les statistiques du joueur dans la base de données
    if round_result.combat_ended:
        sheet.current_stamina = round_result.player_stamina_after
        sheet.current_luck = round_result.player_luck_after
        db.commit()
        db.refresh(sheet)

    return {"round_result": round_result, "new_combat_state": new_combat_state}


# Initialisation de la base de données
@app.on_event("startup")
async def startup_event() -> None:
    """Événement de démarrage de l'application."""
    create_tables()
    init_db()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
