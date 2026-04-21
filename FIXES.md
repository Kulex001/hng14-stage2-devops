# FIXES.md — Bug Report for hng14-stage2-devops

## Bug 1
- **File:** `api/main.py`
- **Line:** 6
- **Problem:** Redis connection hardcoded to `localhost` — fails inside Docker because services communicate via service names, not localhost
- **Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")`

## Bug 2
- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Redis connection hardcoded to `localhost` — same Docker networking issue as Bug 1
- **Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")`

## Bug 3
- **File:** `frontend/app.js`
- **Line:** 6
- **Problem:** `API_URL` hardcoded to `http://localhost:8000` — frontend cannot reach the API service inside Docker using localhost
- **Fix:** Changed to `process.env.API_URL || "http://api:8000"`

## Bug 4
- **File:** `api/main.py`
- **Problem:** No `/health` endpoint exists — Docker HEALTHCHECK and service dependency checks require a health endpoint to confirm the service is ready
- **Fix:** Added `GET /health` endpoint that pings Redis and returns `{"status": "healthy"}` with HTTP 200, or 503 if Redis is unreachable

## Bug 5
- **File:** `frontend/app.js`
- **Problem:** No `/health` endpoint exists — Docker HEALTHCHECK cannot verify the frontend service is ready
- **Fix:** Added `GET /health` endpoint returning `{"status": "healthy"}` with HTTP 200

## Bug 6
- **File:** `api/main.py`
- **Line:** 13
- **Problem:** Missing job returns HTTP 200 with `{"error": "not found"}` — incorrect HTTP semantics, a missing resource must return 404
- **Fix:** Changed to `raise HTTPException(status_code=404, detail="Job not found")`

## Bug 7
- **File:** `api/.env`
- **Problem:** Real secret (`REDIS_PASSWORD=supersecretpassword123`) committed directly to the git repository — exposes credentials in version control history
- **Fix:** Added `api/.env` and `.env` to `.gitignore`, removed file from git tracking with `git rm --cached api/.env`, created `.env.example` with placeholder values

## Bug 8
- **File:** `api/main.py` and `worker/worker.py`
- **Problem:** `REDIS_PASSWORD` is defined in `api/.env` but never passed to the Redis client constructor — Redis password auth is silently ignored
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD", None)` to the Redis connection in both files

## Bug 9
- **File:** `worker/worker.py`
- **Problem:** No error handling around the job processing loop — any Redis connection failure or unexpected exception crashes the entire worker process permanently with no recovery
- **Fix:** Wrapped the loop body in `try/except redis.exceptions.ConnectionError` with a 5-second retry delay, and a general `except Exception` fallback

## Bug 10
- **File:** `worker/worker.py`
- **Line:** 4
- **Problem:** `signal` module imported but no signal handlers implemented — worker cannot shut down gracefully when Docker sends SIGTERM, causing forceful kills and potential job corruption
- **Fix:** Added `signal.signal(signal.SIGTERM, handle_shutdown)` and `signal.signal(signal.SIGINT, handle_shutdown)` handlers that exit cleanly

## Bug 11
- **File:** `api/main.py` line 11 and `worker/worker.py` line 14
- **Problem:** Queue name mismatch — `api/main.py` pushes jobs to the queue named `"job"` (singular) and `worker/worker.py` also reads from `"job"`, but `decode_responses` is not set so job IDs are returned as bytes instead of strings, causing `.decode()` to be called inconsistently
- **Fix:** Added `decode_responses=True` to both Redis connections, standardized queue name to `"jobs"`, and removed manual `.decode()` calls

## Bug 12
- **File:** `api/requirements.txt` and `worker/requirements.txt`
- **Problem:** No version pins on any dependency — builds are non-reproducible and can silently break when a new package version introduces breaking changes
- **Fix:** Pinned all dependencies to specific tested versions: `fastapi==0.111.0`, `uvicorn==0.29.0`, `redis==5.0.4`

## Bug 13
- **File:** `worker/worker.py`
- **Line:** 3
- **Problem:** `os` module imported but never used
- **Fix:** Used `os.getenv()` for Redis configuration, making the import necessary and correct

## Bug 14
- **File:** `api/main.py`
- **Line:** 4
- **Problem:** `os` module imported but never used in original code
- **Fix:** Used `os.getenv()` for Redis host, port, and password configuration

## Summary of All Changes

| File | Changes Made |
|---|---|
| `api/main.py` | Fixed Redis host, added password auth, added /health endpoint, fixed 404 response, used env vars |
| `worker/worker.py` | Fixed Redis host, added password auth, added error handling, implemented signal handlers, fixed queue name |
| `frontend/app.js` | Fixed API_URL to use env var, added /health endpoint |
| `api/requirements.txt` | Pinned all dependency versions |
| `worker/requirements.txt` | Pinned redis version |
| `api/.env` | Removed from git tracking |
| `.gitignore` | Added .env entries |
| `.env.example` | Created with placeholder values |
