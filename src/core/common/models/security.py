from typing import Optional

from src.core.mixins import UsernameModel


class UsernamePasswordSchema(UsernameModel):
    password: Optional[str]
