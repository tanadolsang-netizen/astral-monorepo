"""Grand Narrative API — endpoints for advanced astrology readings."""

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.services.varshaphal_narrative import generate_annual_reading, generate_monthly_focus
from src.services.ziwei_narrative import generate_ziwei_reading, generate_palace_focus
from src.services.fixed_star_narrative import generate_fixed_star_reading, generate_sabian_reading
from src.services.asteroid_narrative import generate_asteroid_reading, generate_chiron_reading
from src.services.nakshatra_narrative import generate_nakshatra_reading, generate_moon_nakshatra_reading
from src.services.dasha_narrative import generate_dasha_reading, generate_antardasha_reading
from src.services.yoga_narrative import generate_yoga_reading, generate_raja_yoga_reading
from src.services.arabic_parts_narrative import generate_arabic_parts_reading, generate_part_of_fortune_reading

logger = logging.getLogger("astral.grand-narrative")
router = APIRouter(prefix="/v1/narrative/grand", tags=["grand-narrative"])


class ChartData(BaseModel):
    data: dict


@router.post("/varshaphal")
async def varshaphal_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Varshaphal (annual) narrative."""
    try:
        return generate_annual_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Varshaphal narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/varshaphal/monthly")
async def varshaphal_monthly(data: ChartData, month: int = Query(1, ge=1, le=12), lang: str = Query("th")):
    """Generate monthly focus from Varshaphal data."""
    try:
        return generate_monthly_focus(data.data, month, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Varshaphal monthly narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/ziwei")
async def ziwei_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Ziwei Dou Shu narrative."""
    try:
        return generate_ziwei_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Ziwei narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/ziwei/palace")
async def ziwei_palace(data: ChartData, palace: str, lang: str = Query("th")):
    """Generate focus on a specific Ziwei palace."""
    try:
        return generate_palace_focus(data.data, palace, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Ziwei palace narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/fixed-stars")
async def fixed_star_narrative(data: ChartData, lang: str = Query("th")):
    """Generate fixed star narrative."""
    try:
        return generate_fixed_star_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Fixed star narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/sabian")
async def sabian_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Sabian symbol narrative."""
    try:
        return generate_sabian_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Sabian narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/asteroids")
async def asteroid_narrative(data: ChartData, lang: str = Query("th")):
    """Generate asteroid narrative."""
    try:
        return generate_asteroid_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Asteroid narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/asteroids/chiron")
async def chiron_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Chiron-specific narrative."""
    try:
        return generate_chiron_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Chiron narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/nakshatra")
async def nakshatra_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Nakshatra narrative."""
    try:
        return generate_nakshatra_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Nakshatra narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/nakshatra/moon")
async def moon_nakshatra_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Moon Nakshatra-specific narrative."""
    try:
        return generate_moon_nakshatra_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Moon Nakshatra narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/dasha")
async def dasha_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Dasha narrative."""
    try:
        return generate_dasha_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Dasha narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/dasha/antardasha")
async def antardasha_narrative(
    data: ChartData,
    mahadasha: str,
    antardasha: str,
    lang: str = Query("th"),
):
    """Generate Antardasha-specific narrative."""
    try:
        return generate_antardasha_reading(data.data, mahadasha, antardasha, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Antardasha narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/yoga")
async def yoga_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Vedic Yoga narrative."""
    try:
        return generate_yoga_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Yoga narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/yoga/raja")
async def raja_yoga_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Raja Yoga-specific narrative."""
    try:
        return generate_raja_yoga_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Raja Yoga narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/arabic-parts")
async def arabic_parts_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Arabic Parts narrative."""
    try:
        return generate_arabic_parts_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Arabic Parts narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/arabic-parts/fortune")
async def part_of_fortune_narrative(data: ChartData, lang: str = Query("th")):
    """Generate Part of Fortune-specific narrative."""
    try:
        return generate_part_of_fortune_reading(data.data, lang)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid chart data: {e}") from e
    except Exception as e:
        logger.error("Part of Fortune narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e
