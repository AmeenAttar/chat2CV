#!/usr/bin/env python3
"""
Comprehensive Error Handling and Logging Service
Provides structured logging, error tracking, and performance monitoring
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling and logging service"""
    
    def __init__(self):
        self.error_counts = {}
        self.performance_metrics = {}
        
    def log_error(self, error: Exception, context: Dict[str, Any] = None, user_id: str = None):
        """Log error with context"""
        error_type = type(error).__name__
        
        # Track error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Create error log entry
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'user_id': user_id,
            'error_count': self.error_counts[error_type]
        }
        
        logger.error(f"Error occurred: {json.dumps(error_data, indent=2)}")
        
        # Alert for critical errors
        if self.error_counts[error_type] > 10:
            logger.critical(f"High error rate for {error_type}: {self.error_counts[error_type]} errors")
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """Log performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': float('inf'),
                'max_duration': 0
            }
        
        metrics = self.performance_metrics[operation]
        metrics['total_calls'] += 1
        metrics['total_duration'] += duration
        
        if success:
            metrics['successful_calls'] += 1
        else:
            metrics['failed_calls'] += 1
        
        # Update statistics
        metrics['avg_duration'] = metrics['total_duration'] / metrics['total_calls']
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)
        
        logger.info(f"Performance: {operation} took {duration:.3f}s (success: {success})")
    
    def performance_monitor(self, operation: str):
        """Decorator for performance monitoring"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.log_performance(operation, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_performance(operation, duration, success=False)
                    self.log_error(e, {'operation': operation, 'args': str(args), 'kwargs': str(kwargs)})
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.log_performance(operation, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_performance(operation, duration, success=False)
                    self.log_error(e, {'operation': operation, 'args': str(args), 'kwargs': str(kwargs)})
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            'status': 'healthy',
            'error_counts': self.error_counts,
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        total_errors = sum(self.error_counts.values())
        return {
            'total_errors': total_errors,
            'error_types': self.error_counts,
            'critical_errors': [error_type for error_type, count in self.error_counts.items() if count > 10]
        }

# Global error handler instance
error_handler = ErrorHandler()

# Import asyncio for async function detection
import asyncio 