"""
Health Service - Handles application health checks and system status
"""
import time
from typing import Dict, Any


class HealthService:
    def __init__(self, start_time: float):
        self.start_time = start_time
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the current health status of the application.
        
        Returns:
            Dict containing status, uptime, and version information
        """
        uptime = round(time.time() - self.start_time, 2)
        
        return {
            "status": "ok",
            "uptime_seconds": uptime,
            "version": "1.0.0"
        }
    
    def get_detailed_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status including system information.
        This can be extended later with database checks, external service checks, etc.
        
        Returns:
            Dict containing detailed health information
        """
        basic_health = self.get_health_status()
        
        # Can be extended with additional checks:
        # - Database connectivity
        # - External API availability
        # - Memory/CPU usage
        # - Disk space
        
        detailed_status = {
            **basic_health,
            "components": {
                "api": "healthy",
                "services": "healthy"
            }
        }
        
        return detailed_status
