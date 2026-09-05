import json
from typing import Any, List

def parse_json_waypoints(waypoints_json: str) -> List[dict]:
    """Parse JSON string into waypoint dict list safely."""
    if not waypoints_json:
        return []
    try:
        return json.loads(waypoints_json)
    except Exception:
        return []
