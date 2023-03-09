from pydantic import BaseModel
from typing import List, Any


class Data(BaseModel):
    HomePlanet: List[str]
    CryoSleep: List[bool]
    Destination: List[str]
    Age: List[float]
    VIP: List[bool]
    RoomService: List[float]
    FoodCourt: List[float]
    ShoppingMall: List[float]
    Spa: List[float]
    VRDeck: List[float]
    deck: List[str]
    deck_num: List[int]
    deck_side: List[str]
    group_number: List[int]
    RoomService_cat: List[bool]
    FoodCourt_cat: List[bool]
    ShoppingMall_cat: List[bool]
    Spa_cat: List[bool]
    VRDeck_cat: List[bool]


class Result(BaseModel):
    id: str
    Transported: bool
