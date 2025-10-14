from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base


class Contact(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()

    __table_args__ = (
        Index(
            "ix_search",
            text(
                "to_tsvector('english', "
                "coalesce(first_name, '') || ' ' || "
                "coalesce(last_name, '') || ' ' || "
                "coalesce(email, '') || ' ' || "
                "coalesce(description, '')"
                ")"
            ),
            postgresql_using="gin",
        ),
    )
