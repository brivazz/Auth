from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from services.film import FilmService, get_film_service
from core.messages import FILM_NOT_FOUND, TOTAL_FILM_NOT_FOUND
from utils.extensions import is_authenticated
from .response_models import FilmSearch, Film
from .utils import PaginateQueryParams

router = APIRouter()


@router.get("/search", response_model=list[FilmSearch])
async def film_search(
    pqp: PaginateQueryParams = Depends(PaginateQueryParams),
    film_title: str = Query("star", description="Название Кинопроизведения."),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmSearch]:
    """
    возвращает список фильмов с похожим названием (с учетом пагинации):
    - **uuid**: id фильма
    - **title**: название фильма
    - **imdb_rating**: рейтинг фильма
    """

    films = await film_service.get_by_title(film_title, pqp.page_size, pqp.page_number)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=TOTAL_FILM_NOT_FOUND
        )
    return [FilmSearch(**film.dict()) for film in films]


@router.get("/{film_id}", response_model=Film)
@is_authenticated
async def film_details(
    request: Request,
    film_id: str = Query(
        "025c58cd-1b7e-43be-9ffb-8571a613579b", description="UUID фильма"
    ),
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    """
    Возвращает информацию о фильме по его id:

    - **uuid**: id фильма
    - **title**: название фильма
    - **imdb_rating**: рейтинг фильма
    - **description**: описание фильма
    - **actors**: актеры
    - **writers**: сценаристы
    - **directors**:  режиссеры
    - **genre**: жанры
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FILM_NOT_FOUND % ("film id", film_id),
        )
    return Film(**film.dict())


@router.get("/", response_model=list[FilmSearch])
async def films_sort(
    pqp: PaginateQueryParams = Depends(PaginateQueryParams),
    sort: str = Query(
        "-imdb_rating",
        regex="^-imdb_rating$|^imdb_rating$",
        description="Сортировка в формате поле-порядок (-по убыванию, "
        "без знака - по возрастанию).",
    ),
    genre_id: UUID | None = Query(None, description="id Жанра"),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmSearch]:
    """
    Возвращает отсортированный список фильмов (с учетом пагинации и жанра):
    - **uuid**: id фильма
    - **title**: название фильма
    - **imdb_rating**: рейтинг фильма
    """

    films = await film_service.get_by_sort(
        sort, pqp.page_size, pqp.page_number, genre_id
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=TOTAL_FILM_NOT_FOUND
        )
    return [FilmSearch(**film.dict()) for film in films]
