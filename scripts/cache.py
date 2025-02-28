#!/usr/bin/env python
"""
Script to manage caching and cache invalidation.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import django
import redis
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import BaseCache
from django.core.management import call_command
from termcolor import colored

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


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client from Django's cache configuration."""
    try:
        if hasattr(cache, 'client'):
            return cache.client.get_client()
        return None
    except Exception:
        return None


def clear_cache(pattern: Optional[str] = None) -> None:
    """Clear cache entries matching pattern."""
    try:
        print_status("\nClearing cache...", 'info')
        
        redis_client = get_redis_client()
        if redis_client:
            # Redis-specific clearing
            if pattern:
                keys = redis_client.keys(f'*{pattern}*')
                if keys:
                    redis_client.delete(*keys)
                    print_status(f"✓ Cleared {len(keys)} keys matching pattern: {pattern}", 'success')
                else:
                    print_status(f"No keys found matching pattern: {pattern}", 'info')
            else:
                redis_client.flushdb()
                print_status("✓ Cache cleared successfully", 'success')
        else:
            # Generic Django cache clearing
            cache.clear()
            print_status("✓ Cache cleared successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error clearing cache: {e}", 'error')


def analyze_cache() -> None:
    """Analyze cache usage and statistics."""
    print_status("\nAnalyzing cache...", 'info')
    
    redis_client = get_redis_client()
    if not redis_client:
        print_status("! Redis client not available", 'warning')
        return
    
    try:
        # Get cache info
        info = redis_client.info()
        
        # Memory usage
        used_memory = info['used_memory_human']
        peak_memory = info['used_memory_peak_human']
        
        # Keys statistics
        total_keys = redis_client.dbsize()
        
        # Sample keys for pattern analysis
        sample_keys = redis_client.keys('*')[:100]  # Limit to 100 keys
        patterns: Dict[str, int] = {}
        
        for key in sample_keys:
            key_str = key.decode('utf-8')
            pattern = key_str.split(':')[0]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Print analysis
        print("\nCache Statistics:")
        print(f"Memory Usage: {used_memory}")
        print(f"Peak Memory: {peak_memory}")
        print(f"Total Keys: {total_keys}")
        
        print("\nKey Patterns:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"{pattern}: {count} keys")
        
        # Check for potential issues
        if info['used_memory_peak'] > info['total_system_memory'] * 0.8:
            print_status("! High memory usage detected", 'warning')
        
        if total_keys > 1000000:
            print_status("! Large number of keys detected", 'warning')
    
    except Exception as e:
        print_status(f"✗ Error analyzing cache: {e}", 'error')


def monitor_cache(duration: int = 60) -> None:
    """Monitor cache operations in real-time."""
    print_status(f"\nMonitoring cache for {duration} seconds...", 'info')
    
    redis_client = get_redis_client()
    if not redis_client:
        print_status("! Redis client not available", 'warning')
        return
    
    try:
        start_time = time.time()
        prev_ops = redis_client.info()['total_commands_processed']
        
        while time.time() - start_time < duration:
            time.sleep(1)
            info = redis_client.info()
            curr_ops = info['total_commands_processed']
            ops_per_second = curr_ops - prev_ops
            
            print(f"Operations/sec: {ops_per_second}, "
                  f"Memory used: {info['used_memory_human']}, "
                  f"Connected clients: {info['connected_clients']}")
            
            prev_ops = curr_ops
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print_status(f"✗ Error monitoring cache: {e}", 'error')


def invalidate_patterns(patterns: List[str]) -> None:
    """Invalidate cache entries matching patterns."""
    try:
        print_status("\nInvalidating cache patterns...", 'info')
        
        redis_client = get_redis_client()
        if not redis_client:
            print_status("! Redis client not available", 'warning')
            return
        
        total_keys = 0
        for pattern in patterns:
            keys = redis_client.keys(f'*{pattern}*')
            if keys:
                redis_client.delete(*keys)
                total_keys += len(keys)
                print(f"Cleared {len(keys)} keys matching: {pattern}")
        
        print_status(f"✓ Invalidated {total_keys} total keys", 'success')
    
    except Exception as e:
        print_status(f"✗ Error invalidating patterns: {e}", 'error')


def export_cache(output_file: str) -> None:
    """Export cache entries to JSON file."""
    try:
        print_status("\nExporting cache entries...", 'info')
        
        redis_client = get_redis_client()
        if not redis_client:
            print_status("! Redis client not available", 'warning')
            return
        
        cache_data = {}
        for key in redis_client.keys('*'):
            key_str = key.decode('utf-8')
            try:
                value = redis_client.get(key)
                if value:
                    cache_data[key_str] = value.decode('utf-8')
            except Exception:
                continue
        
        with open(output_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print_status(f"✓ Cache exported to {output_file}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error exporting cache: {e}", 'error')


def warm_cache() -> None:
    """Pre-warm cache with common queries."""
    try:
        print_status("\nWarming up cache...", 'info')
        
        # Import models
        from blog.models import Post
        from tests.models import Test
        from users.models import User
        
        # Cache common queries
        cache.set('active_tests', Test.objects.filter(active=True).count(), 3600)
        cache.set('recent_posts', Post.objects.filter(status='published')[:10].values(), 3600)
        cache.set('user_count', User.objects.count(), 3600)
        
        # Warm up template cache
        call_command('createcachetable', verbosity=0)
        
        print_status("✓ Cache warmed up successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error warming cache: {e}", 'error')


def cleanup_cache() -> None:
    """Clean up expired cache entries."""
    try:
        print_status("\nCleaning up expired cache entries...", 'info')
        
        redis_client = get_redis_client()
        if not redis_client:
            print_status("! Redis client not available", 'warning')
            return
        
        # Scan for keys with TTL
        cursor = 0
        expired_keys = []
        
        while True:
            cursor, keys = redis_client.scan(cursor)
            for key in keys:
                ttl = redis_client.ttl(key)
                if ttl < 0:  # Expired or no TTL
                    expired_keys.append(key)
            
            if cursor == 0:
                break
        
        # Delete expired keys
        if expired_keys:
            redis_client.delete(*expired_keys)
            print_status(f"✓ Cleaned up {len(expired_keys)} expired keys", 'success')
        else:
            print_status("No expired keys found", 'info')
    
    except Exception as e:
        print_status(f"✗ Error cleaning up cache: {e}", 'error')


def main() -> None:
    """Main function to manage cache."""
    import argparse

    parser = argparse.ArgumentParser(description='Cache management script')
    parser.add_argument('--clear', action='store_true', help='Clear all cache')
    parser.add_argument('--pattern', help='Clear cache matching pattern')
    parser.add_argument('--analyze', action='store_true', help='Analyze cache usage')
    parser.add_argument('--monitor', type=int, metavar='SECONDS', help='Monitor cache operations')
    parser.add_argument('--invalidate', nargs='+', metavar='PATTERN', help='Invalidate cache patterns')
    parser.add_argument('--export', help='Export cache to JSON file')
    parser.add_argument('--warm', action='store_true', help='Warm up cache')
    parser.add_argument('--cleanup', action='store_true', help='Clean up expired entries')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.clear:
        clear_cache(args.pattern)

    if args.analyze:
        analyze_cache()

    if args.monitor:
        monitor_cache(args.monitor)

    if args.invalidate:
        invalidate_patterns(args.invalidate)

    if args.export:
        export_cache(args.export)

    if args.warm:
        warm_cache()

    if args.cleanup:
        cleanup_cache()


if __name__ == '__main__':
    main()
