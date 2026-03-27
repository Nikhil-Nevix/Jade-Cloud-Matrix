#!/usr/bin/env python3
"""
Standalone AWS pricing ingestion script - bypasses any cached sessions
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/NikhilRokade/JadeCloudMatrix/backend')

async def main():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.config import settings
    from app.services.ingestion.aws_ingester import ingest_aws_pricing
    import logging
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    # Create new engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    logger.info("🚀 Starting FRESH AWS pricing ingestion...")
    
    async with SessionLocal() as session:
        try:
            await ingest_aws_pricing(session)
            await session.commit()
            logger.info("✅ AWS pricing ingestion completed successfully!")
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
