from typing import List, Tuple
from fastapi import Query


class Ordering:
    def __init__(self, prior_fields=None, default_field="-create_datetime"):
        self.prior_fields = prior_fields
        self.default_field = default_field

    def __call__(
        self,
        fields: str = Query(
            None,
            description="use - for descending sorting otherwise only field name seprated by ,",
            example="-username,age,create_datetime",
            alias="ordering",
        ),
    ):
        self.fields = fields
        return self

    @property
    def _ordering_fields(self) -> List[str]:
        ordering_fields = [self.default_field]
        if self.prior_fields:
            ordering_fields = self.prior_fields.split(",")
        if self.fields and self.prior_fields:
            ordering_fields.extend(self.fields.split(","))
        elif self.fields and not self.prior_fields:
            ordering_fields = self.fields.split(",")
        return ordering_fields

    def _get_ordering_filter(self, field: str) -> Tuple[str, int]:
        if field.startswith("-"):
            return (field[1:], -1)
        else:
            return (field, 1)

    async def get_ordering_criteria(self) -> List[Tuple[str, int]]:
        criteria = [self._get_ordering_filter(field) for field in self._ordering_fields]
        return criteria
