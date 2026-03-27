import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Google Gemini client
try:
    if settings.GOOGLE_API_KEY:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        client = genai.GenerativeModel('gemini-2.5-flash')
    else:
        client = None
except Exception as e:
    logger.warning(f"Failed to initialize Google Gemini client: {e}")
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
        raise Exception("Google Gemini AI is not configured. Please contact your administrator to set up the GOOGLE_API_KEY.")

    # Check for placeholder key
    if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.startswith("your-google-api-key"):
        raise Exception("Google Gemini AI is not configured properly. Please contact your administrator to set up a valid GOOGLE_API_KEY.")

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
        logger.info(f"Calling Google Gemini API to analyze {len(calculations)} calculations...")

        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = client.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 4000,
            }
        )

        logger.info(f"Response type: {type(response)}")

        # Extract text from Gemini response
        if hasattr(response, 'text'):
            raw = response.text.strip()
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                raw = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip()
            else:
                raise Exception("No text content found in Gemini response")
        else:
            raise Exception(f"Unexpected response format from Gemini: {response}")

        # Remove markdown code fences if present
        if raw.startswith('```json'):
            raw = raw[7:]  # Remove ```json
        if raw.startswith('```'):
            raw = raw[3:]   # Remove ```
        if raw.endswith('```'):
            raw = raw[:-3]  # Remove trailing ```
        raw = raw.strip()

        logger.info(f"Raw response: {raw[:200]}...")

        # Parse JSON
        result = json.loads(raw)
        
        # Add metadata
        result["id"] = str(uuid.uuid4())
        result["generated_at"] = datetime.utcnow().isoformat()
        result["calculations_analysed"] = len(calculations)
        
        logger.info("Google Gemini API recommendations generated successfully.")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        raise Exception("AI response was not valid JSON. Please try again.")

    except Exception as e:
        logger.error(f"Google Gemini API call failed: {e}")
        raise Exception(f"Failed to generate recommendations: {str(e)}")
