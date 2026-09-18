from pydantic import BaseModel
from typing import List


class Machine(BaseModel):
    id: str
    name: str
    available: bool
    status: str


class Order(BaseModel):
    id: str
    product: str
    quantity: int
    priority: int
    processing_time: int
    deadline: int


class Worker(BaseModel):
    id: str
    name: str
    available: bool


class Material(BaseModel):
    id: str
    name: str
    available_quantity: int


class FactoryState(BaseModel):
    machines: List[Machine]
    orders: List[Order]
    workers: List[Worker]
    materials: List[Material]