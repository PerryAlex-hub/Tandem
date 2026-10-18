import httpx

from app.core.config import settings


async def execute_code(source: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.piston_base}/api/v2/execute",
            json={
                "language": "python",
                "version": "3.12.0",
                "files": [{"content": source}],
                "run_timeout": 8000,
            },
        )
        response.raise_for_status()

    data = response.json()
    return data["run"]
