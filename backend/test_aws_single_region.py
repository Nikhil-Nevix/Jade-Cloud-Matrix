#!/usr/bin/env python3
"""Test AWS ingestion for a single region"""
import asyncio
import boto3
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import AsyncSessionLocal
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Region
from app.models.pricing import ComputePricing

async def test_single_region():
    print("Testing AWS API for EU-West-1 region...")
    
    # Create AWS client
    pricing_client = boto3.client(
        'pricing',
        region_name='us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    paginator = pricing_client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'EU (Ireland)'},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Compute Instance'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            {'Type': 'TERM_MATCH', 'Field': 'capacityStatus', 'Value': 'Used'},
        ],
        PaginationConfig={'PageSize': 100}
    )
    
    instances = []
    count = 0
    print("Fetching from AWS API...")
    
    for page_num, page in enumerate(page_iterator, 1):
        print(f"  Processing page {page_num}...")
        for price_item in page.get('PriceList', []):
            product = json.loads(price_item)
            attrs = product.get('product', {}).get('attributes', {})
            instance_type = attrs.get('instanceType')
            if instance_type and instance_type not in instances:
                instances.append(instance_type)
            count += 1
        
        if page_num >= 10:  # Limit to 10 pages for testing
            print(f"  Stopping after 10 pages (processed {count} items)")
            break
    
    print(f"\n✅ Found {len(instances)} unique instance types from {count} API responses")
    print(f"\nSample instances:")
    for i, inst in enumerate(sorted(instances)[:30], 1):
        print(f"  {i:2d}. {inst}")
    
    # Now insert into database
    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(select(Region).where(Region.region_code == 'eu-west-1'))
            region = result.scalar_one_or_none()
            
            if not region:
                print("ERROR: EU-West-1 region not found in database")
                return
            
            print(f"\nInserting into database for region_id={region.id}...")
            inserted = 0
            
            for instance_type in instances:
                stmt = insert(ComputePricing).values(
                    provider_id=1,
                    region_id=region.id,
                    instance_type=instance_type,
                    vcpu=4,  # Default value
                    memory_gb=16.0,  # Default value
                    os_type='Linux',
                    price_per_hour=0.10,  # Default price
                    price_per_month=73.00,  # Default price
                    price_per_year=876.00,  # Default price (0.10 * 8760 hours/year)
                ).on_conflict_do_update(
                    index_elements=['provider_id', 'region_id', 'instance_type', 'os_type'],
                    set_={'price_per_hour': 0.10, 'price_per_year': 876.00}
                )
                await db.execute(stmt)
                inserted += 1
            
            await db.commit()
            print(f"✅ Inserted {inserted} instances into database")
            
            # Verify
            result = await db.execute(text("""
                SELECT COUNT(DISTINCT instance_type) 
                FROM compute_pricing 
                WHERE provider_id = 1 AND region_id = :region_id
            """), {'region_id': region.id})
            count = result.scalar()
            print(f"✅ Verification: {count} instances in database for EU-West-1")

if __name__ == "__main__":
    asyncio.run(test_single_region())
