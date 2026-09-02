import orekit_jpype as orekit
orekit.initVM()

from orekit_jpype.pyhelpers import setup_orekit_data, absolutedate_to_datetime
setup_orekit_data()

from org.orekit.frames import FramesFactory
from org.orekit.utils import IERSConventions, Constants
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.orbits import KeplerianOrbit, OrbitType, PositionAngleType
from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.numerical import NumericalPropagator
from org.orekit.propagation.integration import AdditionalDerivativesProvider
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.bodies import OneAxisEllipsoid

from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.hipparchus.geometry.euclidean.threed import Vector3D

## Setup frames and time
# J2000 frame
inertial_frame = FramesFactory.getEME2000()
earth_frame = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
utc = TimeScalesFactory.getUTC()

# TODO: Move to setup file: epoch
epoch = AbsoluteDate(2026, 1, 1, 0, 0, 0.0, utc)

## Build Initial Orbit
# TODO: Move to setup file: initial orbit
a = 7000000.0
e = 0.001
i = 1.7
pa = 0.0
raan = 0.0
lv = 0.0
mu = Constants.WGS84_EARTH_MU

initial_orbit = KeplerianOrbit(
    a, e, i, pa, raan, lv,
    PositionAngleType.TRUE,
    inertial_frame, epoch, mu
)

# TODO: Move to setup file: s/c properties

mass = 1000.0
initial_state = SpacecraftState(initial_orbit, mass)

## Integrator setup parameters
min_step = 0.001
max_step = 300.0
pos_tolerance = 1.0

tolerances = NumericalPropagator.tolerances(pos_tolerance, initial_orbit, initial_orbit.getType())
integrator = DormandPrince853Integrator(
    min_step, max_step,
    tolerances[0],  # absolute tolerances
    tolerances[1]   # relative tolerances
)

## Propagator Setup
propagator = NumericalPropagator(integrator)
propagator.setOrbitType(OrbitType.CARTESIAN)
propagator.setInitialState(initial_state)

# Add an Earth gravity field force model (degree/order 8x8, for example)
earth = OneAxisEllipsoid(
    Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
    Constants.WGS84_EARTH_FLATTENING,
    earth_frame
)
gravity_provider = GravityFieldFactory.getNormalizedProvider(8, 8)
gravity_force = HolmesFeatherstoneAttractionModel(earth_frame, gravity_provider)
propagator.addForceModel(gravity_force)

## Propagate
target_date = epoch.shiftedBy(3600.0)  # 1 hour later
final_state = propagator.propagate(target_date)

pv = final_state.getPVCoordinates()
print("Date:", absolutedate_to_datetime(final_state.getDate()))
print("Position (m):", pv.getPosition())
print("Velocity (m/s):", pv.getVelocity())