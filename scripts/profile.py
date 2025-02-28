#!/usr/bin/env python
"""
Script to profile and analyze application performance.
"""
import cProfile
import os
import pstats
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import django
import psutil
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.db import connection, reset_queries
from django.test.client import Client
from termcolor import colored
from werkzeug.middleware.profiler import ProfilerMiddleware

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')
django.setup()


def print_status(message: str, status: str = 'info') -> None:
    """Print colored status messages."""
    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan'
    }
    print(colored(message, colors.get(status, 'white')))


class QueryProfiler:
    """Context manager to profile database queries."""

    def __enter__(self):
        self.start_time = time.time()
        self.query_count = len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.final_query_count = len(connection.queries)
        self.queries = connection.queries[self.query_count:]
        self.time_taken = self.end_time - self.start_time

    def print_report(self):
        """Print query profiling report."""
        print_status("\nQuery Profile:", 'info')
        print(f"Total Queries: {len(self.queries)}")
        print(f"Total Time: {self.time_taken:.3f}s")
        print(f"Average Time per Query: {self.time_taken/len(self.queries):.3f}s")
        
        if self.queries:
            print("\nSlow Queries (>0.1s):")
            for query in self.queries:
                if float(query['time']) > 0.1:
                    print(f"\nTime: {query['time']}s")
                    print(f"SQL: {query['sql']}")


def profile_view(view_func: Callable, *args: Any, **kwargs: Any) -> None:
    """Profile a specific view function."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        view_func(*args, **kwargs)
    finally:
        profiler.disable()
        
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    # Create profiles directory if it doesn't exist
    profiles_dir = BASE_DIR / 'profiles'
    profiles_dir.mkdir(exist_ok=True)
    
    # Save profile results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stats_file = profiles_dir / f'view_profile_{timestamp}.stats'
    stats.dump_stats(str(stats_file))
    
    # Print summary
    print_status(f"\nProfile saved to: {stats_file}", 'info')
    stats.print_stats(20)  # Print top 20 entries


def analyze_memory_usage() -> Dict[str, Any]:
    """Analyze current memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss / 1024 / 1024,  # RSS in MB
        'vms': memory_info.vms / 1024 / 1024,  # VMS in MB
        'percent': process.memory_percent(),
        'cpu_percent': process.cpu_percent(),
        'threads': len(process.threads())
    }


def profile_request(url: str, method: str = 'GET', data: Optional[Dict] = None) -> None:
    """Profile a specific HTTP request."""
    client = Client()
    settings.DEBUG = True
    reset_queries()
    
    with QueryProfiler() as profiler:
        if method.upper() == 'GET':
            response = client.get(url)
        else:
            response = client.post(url, data=data)
    
    print_status(f"\nRequest Profile for {method} {url}", 'info')
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {profiler.time_taken:.3f}s")
    
    profiler.print_report()
    
    # Memory usage after request
    memory_usage = analyze_memory_usage()
    print("\nMemory Usage:")
    print(f"RSS: {memory_usage['rss']:.2f} MB")
    print(f"VMS: {memory_usage['vms']:.2f} MB")
    print(f"Memory %: {memory_usage['percent']:.2f}%")
    print(f"CPU %: {memory_usage['cpu_percent']:.2f}%")
    print(f"Threads: {memory_usage['threads']}")


def analyze_query_patterns() -> None:
    """Analyze database query patterns."""
    from django.db import connection
    from collections import defaultdict
    
    query_patterns = defaultdict(list)
    
    for query in connection.queries:
        sql = query['sql']
        time = float(query['time'])
        query_patterns[sql].append(time)
    
    print_status("\nQuery Pattern Analysis:", 'info')
    for sql, times in query_patterns.items():
        count = len(times)
        avg_time = sum(times) / count
        print(f"\nQuery executed {count} times")
        print(f"Average time: {avg_time:.3f}s")
        print(f"SQL: {sql}")


def generate_load_test(url: str, requests: int = 100, concurrent: int = 10) -> None:
    """Generate load test using locust."""
    try:
        from locust import HttpUser, between, task
        
        class TestUser(HttpUser):
            wait_time = between(1, 2)
            
            @task
            def test_url(self):
                self.client.get(url)
        
        # Save locust file
        locust_file = """
from locust import HttpUser, between, task

class TestUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def test_url(self):
        self.client.get('{url}')
""".format(url=url)
        
        with open('locustfile.py', 'w') as f:
            f.write(locust_file)
        
        # Run locust
        os.system(f'locust -f locustfile.py --headless -u {concurrent} -r {concurrent} -t 30s')
        
    except ImportError:
        print_status("! Locust not installed. Install with: pip install locust", 'warning')


def main() -> None:
    """Main function to run profiling tasks."""
    import argparse

    parser = argparse.ArgumentParser(description='Performance profiling script')
    parser.add_argument('--url', help='URL to profile')
    parser.add_argument('--method', default='GET', help='HTTP method')
    parser.add_argument('--data', help='POST data (JSON string)')
    parser.add_argument('--load-test', action='store_true', help='Run load test')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests for load test')
    parser.add_argument('--concurrent', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--analyze-queries', action='store_true', help='Analyze query patterns')
    parser.add_argument('--memory', action='store_true', help='Show memory usage')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.url:
        data = json.loads(args.data) if args.data else None
        profile_request(args.url, args.method, data)

    if args.load_test and args.url:
        generate_load_test(args.url, args.requests, args.concurrent)

    if args.analyze_queries:
        analyze_query_patterns()

    if args.memory:
        memory_usage = analyze_memory_usage()
        print_status("\nCurrent Memory Usage:", 'info')
        print(f"RSS: {memory_usage['rss']:.2f} MB")
        print(f"VMS: {memory_usage['vms']:.2f} MB")
        print(f"Memory %: {memory_usage['percent']:.2f}%")
        print(f"CPU %: {memory_usage['cpu_percent']:.2f}%")
        print(f"Threads: {memory_usage['threads']}")


if __name__ == '__main__':
    main()
