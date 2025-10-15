from typing import Annotated

import httpx
from taskiq import TaskiqDepends, Context


def get_httpx_client(
    context: Annotated[Context, TaskiqDepends()],
) -> httpx.AsyncClient:
    return context.state.client
