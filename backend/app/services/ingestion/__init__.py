"""Ingestion services package."""
from app.services.ingestion.base import PeopleDataProvider
from app.services.ingestion.factory import get_provider

__all__ = ["PeopleDataProvider", "get_provider"]

