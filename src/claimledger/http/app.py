"""In-process POST /claims/query. Starlette is imported only inside build_app."""

from __future__ import annotations

import json


def build_app():
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    async def post_claims_query(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse({}, status_code=400)
        if not isinstance(body, dict) or not isinstance(body.get("question"), str):
            return JSONResponse({}, status_code=400)
        from claimledger.http.claims import claims_query
        from claimledger.ingest.ground import recorded_book

        return JSONResponse(claims_query(body, recorded_book()))

    return Starlette(
        routes=[Route("/claims/query", post_claims_query, methods=["POST"])]
    )
