from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from services.person import PersonService, get_person_service
from core.messages import (
    TOTAL_PERSON_NOT_FOUND,
    PERSON_NOT_FOUND,
    PERSONS_FILMS_NOT_FOUND,
)
from utils.extensions import is_authenticated
from .response_models import PersonFilm, ResponsePerson
from .utils import PaginateQueryParams

router = APIRouter()


@router.get("/{person_id}/film/", response_model=list[PersonFilm])
async def person_films(
    person_id: UUID = Query(
        "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", description="UUID персоны"
    ),
    person_service: PersonService = Depends(get_person_service),
):
    """
    Возвращает список фильмов в создании которых приняла участие персона с переданным id:
    - **uuid**: id фильма
    - **name**: название фильма
    """
    films = await person_service.get_films_for_person(person_id)
    if films is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PERSONS_FILMS_NOT_FOUND
        )
    return films


@router.get("/{person_id}", response_model=ResponsePerson)
@is_authenticated
async def detail_person(
    request: Request,
    person_id: UUID = Query(
        "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", description="UUID персоны"
    ),
    person_service: PersonService = Depends(get_person_service),
):
    """
    Возвращает детальную информацию о персоне по его id:
    - **uuid**: id персоны
    - **full_name**: полное имя персоны
    - **films**: список фильмов в которых уччастовала персона (id фильма и роль)
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PERSON_NOT_FOUND % ("person_id", person_id),
        )
    return ResponsePerson(**person.dict())


@router.get("/search/", response_model=list[ResponsePerson])
async def search_person(
    pqp: PaginateQueryParams = Depends(PaginateQueryParams),
    person_name: str = Query(
        "George Lucas", description="Имя персоны для нечеткого поиска"
    ),
    person_service: PersonService = Depends(get_person_service),
):
    """
    Возвращает список персон с похожими именами (с учетом пагинации):
    - **uuid**: id персоны
    - **full_name**: полное имя персоны
    - **films**: список фильмов в которых участовала персона (id фильма и роль)
    """
    persons = await person_service.search_person(
        person_name, pqp.page_size, pqp.page_number
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=TOTAL_PERSON_NOT_FOUND
        )
    return [ResponsePerson(**p.dict()) for p in persons]
