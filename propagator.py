import json
import numpy as np

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

from satellite import Satellite
## Setup frames and time
# J2000 frame
inertial_frame = FramesFactory.getEME2000()
earth_frame = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
utc = TimeScalesFactory.getUTC()

## Parse input file
# TODO: move parsing somewhere else and store into dataclass
with open('Inputs/satellite.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

semi_major_axis_km = data['orbit']['elements']['semi_major_axis_km']
eccentricity = data['orbit']['elements']['eccentricity']
inclination_deg = data['orbit']['elements']['inclination_deg']
raan_degrees = data['orbit']['elements']['raan_deg']
arg_of_perigee_deg = data['orbit']['elements']['arg_of_perigee_deg']
true_anomaly_deg = data['orbit']['elements']['true_anomaly_deg']
epoch = AbsoluteDate(data['epoch'],utc)
initial_orbit = KeplerianOrbit(
    semi_major_axis_km * 1000.0,    # semi-major axis in m
    eccentricity,                   # eccentricity
    np.deg2rad(inclination_deg),    # inclination
    np.deg2rad(arg_of_perigee_deg), # argument of perigee
    np.deg2rad(raan_degrees),       # raan
    np.deg2rad(true_anomaly_deg),   # true anomaly
    PositionAngleType.TRUE,         # tells which anomaly type ^
    FramesFactory.getGCRF(),        # frame
    epoch,                          # epoch
    Constants.WGS84_EARTH_MU        # mu
)
sat = Satellite(
    name=data['satellite']['name'],
    id=int(data['satellite']['id']),
    international_designator=data['satellite']['international_designator'],
    epoch=epoch,
    orbit=initial_orbit,
    mass_kg=data['physical_properties']['mass_kg'],
    drag_coefficient=data['physical_properties']['drag_coefficient'],
    cross_sectional_area_m2=data['physical_properties']['cross_sectional_area_m2'],
    srp_coefficient=data['physical_properties']['srp_coefficient'],
    srp_area_m2=data['physical_properties']['srp_area_m2'],
    step_size_s=data['propagator']['step_size_s'],
    duration_days=data['propagator']['duration_days'],
    force_models=data['propagator']['force_models']
)

## Integrator setup parameters
min_step = 0.001
max_step = 300.0
pos_tolerance = 1.0

tolerances = NumericalPropagator.tolerances(pos_tolerance, sat.orbit, sat.orbit.getType())
integrator = DormandPrince853Integrator(
    min_step, max_step,
    tolerances[0],  # absolute tolerances
    tolerances[1]   # relative tolerances
)

## Propagator Setup
initial_state = SpacecraftState(sat.orbit, sat.mass_kg)
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
target_date = sat.epoch.shiftedBy(86400.0 * sat.duration_days)  # 1 hour later
final_state = propagator.propagate(target_date)

pv = final_state.getPVCoordinates()
print("Date:", absolutedate_to_datetime(final_state.getDate()))
print("Position (m):", pv.getPosition())
print("Velocity (m/s):", pv.getVelocity())