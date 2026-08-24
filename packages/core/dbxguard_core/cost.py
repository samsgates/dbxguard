from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostEstimate:
    current_monthly: float
    proposed_monthly: float
    difference: float
    increase_percent: float | None
    confidence: float
    method: str


def estimate_scaled_compute_cost(
    historical_monthly_cost: float,
    current_capacity: float,
    proposed_capacity: float,
    *,
    runtime_ratio: float = 1.0,
    schedule_ratio: float = 1.0,
    confidence: float = 0.8,
) -> CostEstimate:
    """Estimate cost by scaling historical spend by capacity, runtime and schedule.

    This deliberately labels itself as an estimate. A production connector can replace this
    strategy with SKU/DBU-specific calculations using system.billing usage and list prices.
    """
    if historical_monthly_cost < 0:
        raise ValueError("historical_monthly_cost must be non-negative")
    if current_capacity <= 0 or proposed_capacity < 0:
        raise ValueError("capacity values are invalid")
    if runtime_ratio < 0 or schedule_ratio < 0:
        raise ValueError("ratios must be non-negative")
    factor = (proposed_capacity / current_capacity) * runtime_ratio * schedule_ratio
    proposed = historical_monthly_cost * factor
    difference = proposed - historical_monthly_cost
    increase = None if historical_monthly_cost == 0 else (difference / historical_monthly_cost) * 100
    return CostEstimate(
        current_monthly=round(historical_monthly_cost, 2),
        proposed_monthly=round(proposed, 2),
        difference=round(difference, 2),
        increase_percent=round(increase, 2) if increase is not None else None,
        confidence=max(0.0, min(1.0, confidence)),
        method="historical_capacity_scaling",
    )
