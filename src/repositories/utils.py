from asyncpg import Record


def one_or_none(result: list) -> Record | None:
    if isinstance(result, list) and len(result) == 1:
        return result[0]
    return None
