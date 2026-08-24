# Architecture

DBXGuard separates evidence acquisition from enforcement. Connectors and parsers produce normalized changes and graph evidence. The graph engine calculates downstream impact. Finding generators create typed findings. The risk engine aggregates severity and confidence. The policy engine returns an explicit deployment decision.
