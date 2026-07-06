"""
Performance profiling against your real, running backend — not synthetic
data. Run this against the actual server (Docker or local uvicorn) once
your real 87k-movie artifacts are built and it's up and serving traffic.

Usage:
    python -m scripts.profile_performance                      # defaults: localhost:8000, 50 requests, 10 concurrent
    python -m scripts.profile_performance --base-url http://localhost:8000 --requests 200 --concurrency 20
    python -m scripts.profile_performance --skip-boot           # only benchmark /recommendations, skip the /health cold-boot report

What this measures:
  1. Cold boot time  — reads `startup_seconds` from /health, which is the
     time core/lifespan.py spent deserializing movies_processed.parquet and
     the pickled recommender at process startup. This is the in-process
     artifact-loading time; it does NOT include Python interpreter startup,
     module imports, or (for Docker) container boot — if you want the full
     "docker-compose up to first healthy response" number, time that
     separately (see the PowerShell snippet this script prints).
  2. /recommendations/{id} latency — sequential requests for a percentile
     distribution (min/mean/median/p95/p99/max), then a concurrent burst to
     see how latency and throughput hold up under simultaneous load.

Real movie IDs are pulled live from /api/v1/movies rather than hardcoded,
so this works against your actual dataset regardless of which IDs exist.
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def fetch_sample_movie_ids(base_url: str, sample_size: int) -> list[int]:
    """Pull real movie IDs from the live API rather than assuming any exist."""
    resp = requests.get(f"{base_url}/api/v1/movies", params={"page_size": 100}, timeout=10)
    resp.raise_for_status()
    items = resp.json()["items"]
    if not items:
        raise RuntimeError(
            "No movies returned by /api/v1/movies — is the server pointed at real "
            "build artifacts? (check /api/v1/health)"
        )
    ids = [item["movie_id"] for item in items]
    return random.choices(ids, k=sample_size) if sample_size > len(ids) else random.sample(ids, sample_size)


def report_cold_boot(base_url: str) -> None:
    resp = requests.get(f"{base_url}/api/v1/health", timeout=10)
    resp.raise_for_status()
    body = resp.json()

    print("=== Cold Boot (from /health) ===")
    print(f"  status:           {body['status']}")
    print(f"  movie_count:      {body['movie_count']:,}")
    startup = body.get("startup_seconds")
    if startup is not None:
        print(f"  artifact load:    {startup:.2f}s  (parquet + pickle deserialization only)")
    else:
        print("  artifact load:    unavailable (older backend without startup_seconds — apply the latest patch)")
    print(
        "  NOTE: this excludes Python/uvicorn process startup and, for Docker,\n"
        "  container boot. For the full picture, time from container start to\n"
        "  first healthy response yourself, e.g. in PowerShell:\n"
        "    $start = Get-Date; docker-compose up -d backend; "
        "do { Start-Sleep -Milliseconds 200 } "
        "until ((try { (irm http://localhost:8000/api/v1/health).status } catch {}) -eq 'ok'); "
        "(Get-Date) - $start"
    )
    print()


def percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    idx = min(int(len(sorted_values) * pct), len(sorted_values) - 1)
    return sorted_values[idx]


def time_one_request(base_url: str, movie_id: int) -> float:
    start = time.perf_counter()
    resp = requests.get(f"{base_url}/api/v1/recommendations/{movie_id}", params={"k": 10}, timeout=30)
    elapsed = time.perf_counter() - start
    resp.raise_for_status()
    return elapsed


def report_sequential_latency(base_url: str, movie_ids: list[int]) -> None:
    print(f"=== Sequential /recommendations/{{id}} latency ({len(movie_ids)} requests, one at a time) ===")
    latencies: list[float] = []
    errors = 0
    for movie_id in movie_ids:
        try:
            latencies.append(time_one_request(base_url, movie_id))
        except requests.RequestException as exc:
            errors += 1
            print(f"  request for movie_id={movie_id} failed: {exc}")

    if not latencies:
        print("  No successful requests — nothing to report.")
        return

    latencies_sorted = sorted(latencies)
    print(f"  successful: {len(latencies)}   failed: {errors}")
    print(f"  min:        {min(latencies) * 1000:.1f} ms")
    print(f"  mean:       {statistics.mean(latencies) * 1000:.1f} ms")
    print(f"  median:     {statistics.median(latencies) * 1000:.1f} ms")
    print(f"  p95:        {percentile(latencies_sorted, 0.95) * 1000:.1f} ms")
    print(f"  p99:        {percentile(latencies_sorted, 0.99) * 1000:.1f} ms")
    print(f"  max:        {max(latencies) * 1000:.1f} ms")
    print()


def report_concurrent_burst(base_url: str, movie_ids: list[int], concurrency: int) -> None:
    print(f"=== Concurrent burst ({len(movie_ids)} requests, {concurrency} at a time) ===")
    latencies: list[float] = []
    errors = 0
    burst_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(time_one_request, base_url, mid): mid for mid in movie_ids}
        for future in as_completed(futures):
            try:
                latencies.append(future.result())
            except requests.RequestException as exc:
                errors += 1
                print(f"  request for movie_id={futures[future]} failed: {exc}")

    wall_clock = time.perf_counter() - burst_start

    if not latencies:
        print("  No successful requests — nothing to report.")
        return

    latencies_sorted = sorted(latencies)
    throughput = len(latencies) / wall_clock if wall_clock > 0 else 0.0
    print(f"  successful: {len(latencies)}   failed: {errors}")
    print(f"  wall clock: {wall_clock:.2f}s total")
    print(f"  throughput: {throughput:.1f} requests/sec")
    print(f"  mean:       {statistics.mean(latencies) * 1000:.1f} ms")
    print(f"  p95:        {percentile(latencies_sorted, 0.95) * 1000:.1f} ms")
    print(f"  p99:        {percentile(latencies_sorted, 0.99) * 1000:.1f} ms")
    print(f"  max:        {max(latencies) * 1000:.1f} ms")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests for each benchmark")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent workers for the burst test")
    parser.add_argument("--skip-boot", action="store_true", help="Skip the /health cold-boot report")
    args = parser.parse_args()

    if not args.skip_boot:
        report_cold_boot(args.base_url)

    movie_ids = fetch_sample_movie_ids(args.base_url, args.requests)
    report_sequential_latency(args.base_url, movie_ids)

    movie_ids_burst = fetch_sample_movie_ids(args.base_url, args.requests)
    report_concurrent_burst(args.base_url, movie_ids_burst, args.concurrency)


if __name__ == "__main__":
    main()
