from sqlalchemy import Index, text, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base


class Contact(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    nimble_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

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

    def __str__(self):
        return f"id={self.id} full name={self.first_name + self.last_name}"

    def __repr__(self):
        return f"Contact(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, description={self.description})"
