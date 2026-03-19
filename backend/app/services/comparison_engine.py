from typing import Dict, List


def compare_providers(provider_breakdowns: List[Dict]) -> Dict:
    """
    Compare providers and return comparison insights.
    Used by standard, reserved, and other calculation types.
    """
    if not provider_breakdowns:
        return {
            "cheapest_provider": None,
            "most_expensive_provider": None,
            "max_savings_pct": 0.0,
            "max_savings_amount": 0.0,
        }
    
    sorted_by_cost = sorted(provider_breakdowns, key=lambda x: x.get("total_cost_monthly", 0))
    cheapest = sorted_by_cost[0]
    most_expensive = sorted_by_cost[-1]
    
    cheapest_cost = cheapest.get("total_cost_monthly", 0)
    expensive_cost = most_expensive.get("total_cost_monthly", 0)
    
    if expensive_cost > 0:
        savings_pct = ((expensive_cost - cheapest_cost) / expensive_cost) * 100
        savings_amount = expensive_cost - cheapest_cost
    else:
        savings_pct = 0.0
        savings_amount = 0.0
    
    return {
        "cheapest_provider": cheapest.get("provider_name"),
        "most_expensive_provider": most_expensive.get("provider_name"),
        "max_savings_pct": round(savings_pct, 2),
        "max_savings_amount": round(savings_amount, 2),
    }
