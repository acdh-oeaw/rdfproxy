from pydantic import BaseModel, model_validator


class Point(BaseModel):
    x: int
    y: int


class PointNotOrigin(Point):
    @model_validator(mode="after")
    def _check_not_origin(self):
        if self.x == 0 and self.y == 0:
            raise ValueError("Point at origin (0, 0) is not allowed.")
        return self
