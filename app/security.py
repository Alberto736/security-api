from fastapi import Depends, HTTPException, Request

from app.settings import Settings, get_settings


def require_api_key(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """
    Protege endpoints cuando se configura una API key en `API_KEY`.
    - header por defecto: `X-API-Key`
    - configurable vía `API_KEY_HEADER`
    """

    # Tratar `API_KEY=""` como no configurada para no romper desarrollo/local.
    if not settings.api_key:
        if settings.api_key_required:
            raise HTTPException(
                status_code=500,
                detail="API_KEY_REQUIRED=true pero falta API_KEY en configuración",
            )
        return

    provided = request.headers.get(settings.api_key_header)
    if not provided or provided != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

