#!/usr/bin/env python3
"""
Script to manually run Azure and GCP pricing ingestion only.
"""
import asyncio
import sys
import logging
from app.database import get_async_session
from app.services.ingestion.azure_ingester import ingest_azure_pricing
from app.services.ingestion.gcp_ingester import ingest_gcp_pricing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run Azure and GCP pricing ingestion."""
    logger.info("🚀 Starting Azure and GCP pricing ingestion...")
    
    # Get database session
    async for db in get_async_session():
        try:
            logger.info("📊 Starting Azure pricing ingestion...")
            await ingest_azure_pricing(db)
            logger.info("✅ Azure pricing ingestion completed!")
            
            logger.info("\n📊 Starting GCP pricing ingestion...")
            await ingest_gcp_pricing(db)
            logger.info("✅ GCP pricing ingestion completed!")
            
            logger.info("\n🎉 All pricing ingestion completed successfully!")
            break
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
