"""Run the FastAPI server with uvicorn."""

from __future__ import annotations

import uvicorn

from policritique.settings import get_settings


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "policritique.api.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )


if __name__ == "__main__":
    run()
