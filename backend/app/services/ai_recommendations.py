import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional
from anthropic import Anthropic
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Anthropic client
try:
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
except Exception as e:
    logger.warning(f"Failed to initialize Anthropic client: {e}")
    client = None


async def generate_recommendations(
    calculations: List[Dict],
    focus_areas: Optional[List[str]] = None,
) -> Dict:
    """
    Generate AI-powered cost optimization recommendations using Claude.
    
    Args:
        calculations: List of calculation dicts with full data
        focus_areas: Optional list of focus areas to guide analysis
    
    Returns:
        Dict with recommendations, savings estimates, and summary
    """
    if not client:
        raise Exception("Claude API client not initialized. Please set ANTHROPIC_API_KEY in environment.")
    
    if not calculations:
        raise ValueError("At least one calculation is required for analysis")
    
    if len(calculations) > 10:
        raise ValueError("Maximum 10 calculations can be analyzed at once")
    
    # Build context for Claude
    total_monthly_spend = 0.0
    providers_used = set()
    
    for calc in calculations:
        if calc.get("aws_total_monthly"):
            total_monthly_spend += calc["aws_total_monthly"]
            providers_used.add("AWS")
        if calc.get("azure_total_monthly"):
            total_monthly_spend += calc["azure_total_monthly"]
            providers_used.add("Azure")
        if calc.get("gcp_total_monthly"):
            total_monthly_spend += calc["gcp_total_monthly"]
            providers_used.add("GCP")
    
    context = {
        "calculations": calculations,
        "total_monthly_spend": round(total_monthly_spend, 2),
        "providers_used": list(providers_used),
        "focus_areas": focus_areas or ["cost_reduction", "reserved_instances", "right_sizing"],
    }
    
    system_prompt = """You are an expert cloud cost optimization consultant for Jade Global Software Pvt Ltd. 
Analyze the provided multi-cloud pricing data and return ONLY a valid JSON object with specific, actionable 
cost optimization recommendations. Base savings estimates on the actual numbers provided. Never make up numbers. 
Be specific about which provider and instance types to change."""
    
    user_prompt = f"""Analyze these cloud infrastructure calculations and provide cost optimization recommendations:

{json.dumps(context, indent=2)}

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "recommendations": [
    {{
      "title": "Short action title",
      "category": "Reserved Instances|Right Sizing|Region Optimization|Storage|Kubernetes|Network",
      "priority": "high|medium|low",
      "estimated_monthly_savings": 0.00,
      "estimated_annual_savings": 0.00,
      "description": "Detailed explanation with specific numbers",
      "action_steps": ["Step 1", "Step 2", "Step 3"],
      "affected_providers": ["AWS"]
    }}
  ],
  "total_estimated_monthly_savings": 0.00,
  "total_estimated_annual_savings": 0.00,
  "summary": "2-3 sentence executive summary"
}}"""
    
    try:
        logger.info(f"Calling Claude API to analyze {len(calculations)} calculations...")
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
        )
        
        # Extract text from response
        raw = message.content[0].text.strip()
        
        # Parse JSON
        result = json.loads(raw)
        
        # Add metadata
        result["id"] = str(uuid.uuid4())
        result["generated_at"] = datetime.utcnow().isoformat()
        result["calculations_analysed"] = len(calculations)
        
        logger.info("Claude API recommendations generated successfully.")
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        raise Exception("AI response was not valid JSON. Please try again.")
    
    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        raise Exception(f"Failed to generate recommendations: {str(e)}")
