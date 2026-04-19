from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: UserOut

