from typing import Optional
from uuid import UUID
from sqlalchemy import or_


def apply_user_scope(query, user_id_column, user_id: Optional[UUID]):
    """
    Scope telemetry to a logged-in user without dropping extension/demo rows
    that were ingested with a null user_id (no JWT on the client).
    """
    if user_id is None:
        return query
    return query.filter(or_(user_id_column == user_id, user_id_column.is_(None)))
