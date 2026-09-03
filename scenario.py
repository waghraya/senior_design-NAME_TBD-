from dataclasses import dataclass
from org.orekit.time import AbsoluteDate

@dataclass
class Scenario:
    name: str
    epoch: AbsoluteDate
    duration_days: float
    time_step_s: float