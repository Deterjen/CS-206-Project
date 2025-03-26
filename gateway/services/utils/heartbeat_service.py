import asyncio
import logging
import time

import aiohttp

from config import HEARTBEAT_INTERVAL, ENABLE_HEARTBEAT, HEARTBEAT_URL

logger = logging.getLogger(__name__)


class HeartbeatService:
    """
    Ultra-lightweight self health check service that uses asyncio to periodically ping
    the application's heartbeat endpoint, preventing inactivity timeout on Render's free tier.
    """

    def __init__(self):
        """Initialize the heartbeat service with minimal state."""
        self.is_running = False
        self.task = None

        # Get configuration from environment variables
        self.interval = HEARTBEAT_INTERVAL  # Default: 10 minutes

        # Only track statistics if explicitly enabled
        self.stats_enabled = ENABLE_HEARTBEAT
        if self.stats_enabled:
            self.start_time = time.time()
            self.ping_count = 0
            logger.info("Heartbeat statistics tracking is enabled")
        else:
            logger.info("Heartbeat running in minimal mode (statistics disabled)")

    async def start(self):
        """Start the heartbeat service."""
        if self.is_running:
            return

        self.is_running = True
        self.task = asyncio.create_task(self._heartbeat_loop())
        logger.info(f"Heartbeat service started with interval of {self.interval} seconds")

    async def stop(self):
        """Stop the heartbeat service."""
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        logger.info("Heartbeat service stopped")

    def get_stats(self):
        """Get current heartbeat statistics if enabled."""
        if not self.stats_enabled:
            return {"statistics_tracking": "disabled"}

        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime // 86400:.0f}d {(uptime % 86400) // 3600:.0f}h {(uptime % 3600) // 60:.0f}m",
            "ping_count": self.ping_count
        }

    def _get_app_url(self):
        """Determine the application URL for self-pinging."""
        return f"{HEARTBEAT_URL.rstrip('/')}/health"

    async def _perform_heartbeat(self):
        """Perform a single heartbeat ping with minimal operations."""
        url = self._get_app_url()

        try:
            # Use a new session for each request to prevent session state accumulation
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        if self.stats_enabled:
                            self.ping_count += 1
                        # Avoid any additional processing here
                    else:
                        logger.warning(f"Heartbeat returned status: {response.status}")

        except Exception as e:
            logger.error(f"Heartbeat failed: {str(e)}")

    async def _heartbeat_loop(self):
        """Main heartbeat loop that runs continuously with minimal overhead."""
        log_counter = 0
        stats_interval = 36  # Log stats every ~6 hours with 10 min interval

        while self.is_running:
            try:
                await self._perform_heartbeat()

                # Only log stats periodically if enabled
                if self.stats_enabled:
                    log_counter += 1
                    if log_counter >= stats_interval:
                        uptime = time.time() - self.start_time
                        hours = uptime / 3600
                        logger.info(f"Heartbeat stats - Uptime: {hours:.1f} hours, Pings: {self.ping_count}")
                        log_counter = 0

                # Sleep until next heartbeat
                await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(60)  # Sleep briefly before retrying


# Create a singleton instance
heartbeat_service = HeartbeatService()
