import logging
import time
import uuid

from collections import defaultdict
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from config.logging_config import request_id_var

from .views import api_response, rate_limit_exceeded


logger = logging.getLogger("app")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app, default_limit: int = 60, limit_period: int = 60, cleanup_period: int = 150, route_limits: dict = {}
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.limit_period = limit_period  # Time window for rate limiting
        self.cleanup_period = cleanup_period  # Time window for cleanup
        self.route_limits = route_limits
        self.requests: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        self.cleanup_requests(client_ip, request.url.path, current_time)

        # check for route specific limit
        route = request.url.path
        limit = self.route_limits.get(route, self.default_limit)

        if len(self.requests[client_ip][route]) >= limit:
            logger.info("%s has exceeded rate limit", client_ip)
            if request.headers.get("Accept") == "application/json":
                return await api_response(
                    success=False,
                    message="Rate limit exceeded",
                    status_code=429,
                    errors={"errors": "Too many requests"},
                )
            else:
                return await rate_limit_exceeded(request, HTTPException(status_code=429, detail="Rate limit exceeded"))

        self.requests[client_ip][route].append(current_time)
        logging.info(self.requests)

        response = await call_next(request)
        return response

    def cleanup_requests(self, client_ip, route, current_time):
        # Remove timestamps that are outside the cleanup period
        self.requests[client_ip][route] = [
            timestamp for timestamp in self.requests[client_ip][route] if current_time - timestamp < self.cleanup_period
        ]


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        request_id_var.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
