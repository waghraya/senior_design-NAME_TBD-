from org.orekit.orbits import KeplerianOrbit
from org.orekit.time import AbsoluteDate
from dataclasses import dataclass

@dataclass
class Satellite:
    name: str
    id: int
    international_designator: str
    epoch: AbsoluteDate
    orbit: KeplerianOrbit
    mass_kg: float
    drag_coefficient: float
    cross_sectional_area_m2: float
    srp_coefficient: float
    srp_area_m2: float
    step_size_s: float
    duration_days: float
    force_models: tuple[str,...]