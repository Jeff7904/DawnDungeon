
from datetime import datetime, timedelta
from dawndungeon import config, mongodb
from dawndungeon.api.routers.authentication.schemas import Token, TokenData
from dawndungeon.db.mongodb.entities.session import Session
from fastapi import Depends, HTTPException, status, APIRouter, Security, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from typing import Optional, Any, Annotated
from dawndungeon.api.story import StoryManager
from dawndungeon.api.dependencies import get_session
from dawndungeon.db.mongodb.entities.world import World
from dawndungeon.db.mongodb.entities.user import UserInDB
from dawndungeon.api.routers.authentication.router import get_current_user

router: APIRouter = APIRouter()

async def session_create(
    current_user: Annotated[UserInDB, Security(get_current_user)],
    world: World,
    session: dict = Depends(get_session)
) -> JSONResponse:
    manager_dict: Optional[dict] = session.get("manager")

    if manager_dict is None:
        manager: StoryManager = StoryManager(world, current_user)
    else:
        manager: StoryManager = StoryManager(
            World(**manager_dict["world"]),
            UserInDB(**manager_dict["user"]),
            session=Session(**manager_dict["session"]),
            history=manager_dict["memory"]
        )

    if len(manager.memory.buffer) != 0:
        raise HTTPException(
            status_code=400,
            detail="Session already exists. Please use /session/execute to continue."
        )

    response: JSONResponse = JSONResponse(manager.execute())
    session["manager"] = manager.serialize()
    return response

@router.post("/session/create")
async def session_create_from(
    current_user: Annotated[UserInDB, Security(get_current_user)],
    world_id: Annotated[str, Form()],
    session: dict = Depends(get_session)
):
    world: Optional[World] = mongodb.get_world(id_=world_id)
    if world is None:
        raise HTTPException(
            status_code=404,
            detail="World not found."
        )
    return await session_create(current_user, world, session)

@router.post("/session/create-random")
async def session_create_random(
    current_user: Annotated[UserInDB, Security(get_current_user)],
    session: dict = Depends(get_session)
):
    world: Optional[World] = mongodb.get_world(random=True)
    if world is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There are no worlds in the database."
        )
    return await session_create(current_user, world, session)

@router.post("/session/create-for-developer")
async def session_create_for_developer(
    current_user: Annotated[UserInDB, Security(get_current_user)],
    session: dict = Depends(get_session)
):
    return JSONResponse(
        {"content": "You wake up in a dimly lit dungeon, your head throbbing with pain. As your eyes adjust to the darkness, you see a flickering torch on the wall and a rusty sword lying on the ground. You slowly get up, feeling the weight of your armor on your weary body. You have no memory of how you ended up here, but one thing is clear - you must find a way out of this dungeon and discover the truth behind your amnesia.","metadata": {"character": {"name": "Elysia","description": "A fearless warrior with a mysterious past","age": 25,"coins": 0,"current_health": 100,"current_mana": 50,"defense": 10,"health_regeneration": 5,"inventory": [{"name": "Rusty Sword","description": "A worn-out sword, but still deadly","damage": 15,"durability": 50,"price": 10},{"name": "Healing Potion","description": "A magical potion that restores health","price": 20}],"level": 1,"location": "Dungeon","max_health": 100,"max_mana": 100,"quests": [],"strength": 15},"world": {"name": "DawnDungeon","description": "A RPG world with dragons and dungeons","world_quest": None,"artifacts": ["Dragon Scale","Amulet of Power"],"current_date": "June 23, 2023","current_time": "12:00 PM","dimensions": ["Dungeon","Forest","Mountain"],"geography": "A land filled with treacherous dungeons, towering mountains, and ancient forests","history": "A history of battles between dragons and warriors seeking glory and treasure","magic": "Magic flows through the veins of this world, granting power to those who can harness it","technology": "Medieval technology with a touch of magic","threat_level": "Medium"}}}
    )

@router.post("/session/execute")
async def session_execute(
    action: Annotated[str, Form()],
    session: dict = Depends(get_session)
):
    manager_dict: Optional[dict] = session.get("manager")
    if manager_dict is None:
        raise HTTPException(
            status_code=404,
            detail="Please create a session first with /session/create."
        )
    manager: StoryManager = StoryManager.deserialize(manager_dict)
    response: JSONResponse = JSONResponse(manager.execute(action=action))
    session["manager"] = manager.serialize()
    return response

@router.post("/session/save")
async def session_save(
    session: dict = Depends(get_session)
):
    manager: Optional[StoryManager] = session.get("manager")
    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="Please create a session first with /session/create."
        )

    manager.save()
    return JSONResponse({"status": "success"})
