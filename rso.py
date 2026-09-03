from org.orekit.propagation.analytical.tle import TLE
from dataclasses import dataclass

@dataclass(frozen=True)
class RSO:
    name: str
    tle: TLE