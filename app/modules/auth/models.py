from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.shared.base_model import BaseModel


class RefreshToken(BaseModel):
    """Модель refresh токена"""

    __tablename__ = "refresh_tokens"

    token_jti = Column(String(64), unique=True, nullable=False, index=True)
    token_hash = Column(String(128), nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
