from typing import Literal, List, get_args, get_origin
from pydantic import BaseModel


class TeslaBase(BaseModel):
    zipcode: str
    model: str
    type: Literal["new", "used"]
    engines: List[str]
    exterior_colors: List[str]
    interior_colors: List[str]
    years: List[Literal[
        "2018", "2019", "2020", "2021", "2022", "2023", "2024"
    ]]

    def __str__(self):
        return f"{self.zipcode}.{self.model}.{self.type}.{'-'.join(self.engines)}.{'-'.join(self.exterior_colors)}.{'-'.join(self.interior_colors)}.{'-'.join(self.years)}"

    def to_url(self):
        url = f"{self.type}/{self.model}"
        params = []

        if self.zipcode:
            params.append(f"zip={self.zipcode}")
        if self.engines:
            params.append(
                "TRIM=" + "".join(",".join(self.engines)))
        if self.exterior_colors:
            params.append(
                "PAINT=" + "".join(",".join(self.exterior_colors)))
        if self.interior_colors:
            params.append(
                "INTERIOR=" + "".join(",".join(self.interior_colors)))
        if self.years:
            params.append(
                "Year=" + "".join(",".join(self.years)))

        if len(params) > 0:
            url += "?" + "".join("&".join(params))

        return url

    @classmethod
    def options(cls, field_name: str) -> List[str]:
        annotation = cls.model_fields.get(field_name).annotation

        if not annotation:
            raise ValueError(f"No such field: {field_name}")

        origin = get_origin(annotation)
        args = get_args(annotation)

        # Case: Literal[...]
        if origin is Literal:
            return list(args)

        # Case: List[Literal[...]]
        if origin in (list, List) and get_origin(args[0]) is Literal:
            return list(get_args(args[0]))

        raise TypeError(
            f"Field '{field_name}' is not a Literal or List[Literal]")


class TeslaModelS(TeslaBase):
    model: str = "ms"
    engines: List[Literal[
        "MSPLAID", "MSPERF", "MSAWD"
    ]]
    exterior_colors: List[Literal[
        "WHITE", "BLACK", "BLUE", "GREY", "RED"
    ]]
    interior_colors: List[Literal[
        "BLACK", "WHITE", "CREAM"
    ]]


class TeslaModel3(TeslaBase):
    model: str = "m3"
    engines: List[Literal[
        "PAWD", "LRAWD", "LRRWD", "M3RWD"
    ]]
    exterior_colors: List[Literal[
        "WHITE", "BLACK", "BLUE", "GREY", "SILVER", "RED"
    ]]
    interior_colors: List[Literal[
        "PREMIUM_BLACK", "PREMIUM_WHITE"
    ]]
