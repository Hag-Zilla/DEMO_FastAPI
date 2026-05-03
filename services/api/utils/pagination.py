"""Pagination utilities."""

from typing import Sequence, TypeVar

from services.api.schemas.common import ListResponse

T = TypeVar("T")


def make_list_response(items: Sequence[T], total: int) -> ListResponse[T]:
    """Build a ListResponse from a page of items and the total DB count.

    Args:
        items: The page of items returned by the query.
        total: Total number of matching items (without limit/offset).

    Returns:
        ListResponse with data, count (page size), and total.
    """
    return ListResponse(data=items, count=len(items), total=total)
