"""Read-only tool factory: no approval, execution, network, shell or filesystem tools."""
from .catalog import rank

TOOL_NAMES = ('search_appointments', 'evaluate_appointments')


def build_tools(candidates, budget, daypart, trace):
    from strands import tool

    @tool
    def search_appointments() -> list[dict]:
        """Read the synthetic annual car-service inventory. No real appointments are queried."""
        trace.append('search_appointments')
        return [dict(c) for c in candidates]

    @tool
    def evaluate_appointments() -> list[dict]:
        """Rank inventory using confirmed budget and daypart; higher eligible score wins."""
        trace.append('evaluate_appointments')
        return rank(candidates, budget, daypart)

    return [search_appointments, evaluate_appointments]
