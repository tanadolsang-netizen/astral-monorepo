"""Accuracy endpoints — computational validation report."""

from __future__ import annotations

from fastapi import APIRouter

from src.services.accuracy_service import accuracy_report, cross_validate

router = APIRouter()


@router.get("/report")
def get_accuracy_report() -> dict:
    return accuracy_report()


@router.get("/cross-check")
def quick_cross_check() -> dict:
    return cross_validate(max_samples=4)
