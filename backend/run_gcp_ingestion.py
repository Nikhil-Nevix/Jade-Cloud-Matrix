#!/usr/bin/env python3
"""
Script to manually run GCP pricing ingestion with live API.
"""
import asyncio
import sys
import logging
from app.database import get_async_session
from app.services.ingestion.gcp_ingester import ingest_gcp_pricing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run GCP pricing ingestion."""
    logger.info("🚀 Starting GCP pricing ingestion with LIVE API...")
    
    # Get database session
    async for db in get_async_session():
        try:
            await ingest_gcp_pricing(db)
            logger.info("✅ GCP pricing ingestion completed!")
            break
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
