from collections import defaultdict
from time import time
from fastapi import HTTPException, status
from starlette.requests import Request

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)

    async def __call__(self, request: Request):
        client_ip = request.client.host
        current_time = time()
        window_start = current_time - self.period
        # Remove timestamps outside the current window
        self.clients[client_ip] = [timestamp for timestamp in self.clients[client_ip] if timestamp > window_start]

        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later."
            )
        self.clients[client_ip].append(current_time)