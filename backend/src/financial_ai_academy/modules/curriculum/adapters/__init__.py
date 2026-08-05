"""Curriculum adapters."""

from .content_gateway import PublicContentGateway
from .postgres_repository import PostgresCurriculumRepository

__all__ = ["PostgresCurriculumRepository", "PublicContentGateway"]
