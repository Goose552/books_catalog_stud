from typing import Annotated
from pydantic import AfterValidator, Field


def reject_nul(v: str) -> str:
    if v is not None and "\x00" in v:
        raise ValueError("NUL character is not allowed")
    return v

SafeStr = Annotated[str, AfterValidator(reject_nul)]