#!/usr/bin/env python3
"""
Run AWS pricing ingestion only - for testing
"""
import asyncio
import logging
from app.database import get_async_session
from app.services.ingestion.aws_ingester import ingest_aws_pricing

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Run AWS pricing ingestion."""
    logger.info("🚀 Starting AWS pricing ingestion...")
    
    async for db in get_async_session():
        try:
            await ingest_aws_pricing(db)
            logger.info("✅ AWS pricing ingestion completed!")
            break
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(main())
