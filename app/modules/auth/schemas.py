import re
from pydantic import BaseModel, field_validator

# Permissive email regex — rejects clearly invalid formats while allowing
# internal/reserved domains like .local, .internal, .test, etc.
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+$")


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if len(v) > 254:
            raise ValueError("Email too long")
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password too short")
        if len(v) > 128:
            raise ValueError("Password too long")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: UserOut

