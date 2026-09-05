import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import User, BusRoute, Vehicle, GPSTelemetry, RoutePoint, UserAssignment

logger = logging.getLogger("seed_service")

# Predefined Development / Demo Route Points
ROUTE_A_WAYPOINTS = [
    {
        "lat": 12.971858,
        "lng": 77.594672,
        "is_stop": True,
        "name": "Stop 1: Downtown Hub",
        "sequence": 1
    },
    {
        "lat": 12.971871,
        "lng": 77.59464,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971901,
        "lng": 77.594553,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971911,
        "lng": 77.594527,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972022,
        "lng": 77.594247,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972063,
        "lng": 77.59416,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972069,
        "lng": 77.594147,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972113,
        "lng": 77.594044,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972174,
        "lng": 77.59397,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972206,
        "lng": 77.594011,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.972259,
        "lng": 77.59407,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97246,
        "lng": 77.594226,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973084,
        "lng": 77.59475,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97344,
        "lng": 77.595041,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973607,
        "lng": 77.595223,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97373,
        "lng": 77.595372,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973902,
        "lng": 77.595583,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974067,
        "lng": 77.595777,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974253,
        "lng": 77.596001,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97463,
        "lng": 77.596459,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974735,
        "lng": 77.596585,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974942,
        "lng": 77.59684,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97502,
        "lng": 77.596943,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975144,
        "lng": 77.597125,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975434,
        "lng": 77.597541,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975717,
        "lng": 77.597936,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975833,
        "lng": 77.598092,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97594,
        "lng": 77.59824,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976297,
        "lng": 77.598726,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976523,
        "lng": 77.598994,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976561,
        "lng": 77.599033,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976583,
        "lng": 77.599061,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976644,
        "lng": 77.599133,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976672,
        "lng": 77.599195,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9767,
        "lng": 77.599334,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976704,
        "lng": 77.599499,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9767,
        "lng": 77.599602,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976687,
        "lng": 77.600029,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976679,
        "lng": 77.600293,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976661,
        "lng": 77.600859,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976632,
        "lng": 77.601607,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976632,
        "lng": 77.601678,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976639,
        "lng": 77.601792,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976637,
        "lng": 77.601864,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976518,
        "lng": 77.601799,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976521,
        "lng": 77.601674,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97654,
        "lng": 77.601037,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976561,
        "lng": 77.600829,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976568,
        "lng": 77.600538,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976592,
        "lng": 77.600034,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976593,
        "lng": 77.600008,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976615,
        "lng": 77.599517,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976616,
        "lng": 77.599495,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976616,
        "lng": 77.599352,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976447,
        "lng": 77.59936,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976334,
        "lng": 77.599414,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976276,
        "lng": 77.599444,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976075,
        "lng": 77.59956,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975817,
        "lng": 77.599722,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975673,
        "lng": 77.599813,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975578,
        "lng": 77.599878,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975452,
        "lng": 77.599871,
        "is_stop": True,
        "name": "Stop 2: City Center",
        "sequence": 2
    },
    {
        "lat": 12.975376,
        "lng": 77.599857,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974949,
        "lng": 77.599725,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974533,
        "lng": 77.599597,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974538,
        "lng": 77.599554,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974549,
        "lng": 77.599487,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974611,
        "lng": 77.599144,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974628,
        "lng": 77.599046,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974635,
        "lng": 77.598976,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974635,
        "lng": 77.598976,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974749,
        "lng": 77.59831,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974727,
        "lng": 77.598293,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97449,
        "lng": 77.598353,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974075,
        "lng": 77.598455,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974041,
        "lng": 77.599404,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974042,
        "lng": 77.599415,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974038,
        "lng": 77.599465,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973616,
        "lng": 77.599382,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973376,
        "lng": 77.59935,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973308,
        "lng": 77.599378,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973259,
        "lng": 77.599423,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973202,
        "lng": 77.599503,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973161,
        "lng": 77.599709,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973147,
        "lng": 77.599955,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973114,
        "lng": 77.600506,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973109,
        "lng": 77.600598,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973102,
        "lng": 77.600701,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97309,
        "lng": 77.601026,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973094,
        "lng": 77.601066,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973133,
        "lng": 77.601128,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973165,
        "lng": 77.60118,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973185,
        "lng": 77.601203,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973227,
        "lng": 77.601256,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973243,
        "lng": 77.601282,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973267,
        "lng": 77.601325,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.973378,
        "lng": 77.601355,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974031,
        "lng": 77.601436,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974092,
        "lng": 77.601443,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974181,
        "lng": 77.601454,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974234,
        "lng": 77.601461,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974343,
        "lng": 77.601473,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974414,
        "lng": 77.601481,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97443,
        "lng": 77.601483,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974461,
        "lng": 77.601487,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974847,
        "lng": 77.601543,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.974973,
        "lng": 77.601561,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975041,
        "lng": 77.60157,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975111,
        "lng": 77.601579,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975214,
        "lng": 77.60159,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975289,
        "lng": 77.601598,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975385,
        "lng": 77.601608,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975478,
        "lng": 77.60162,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975589,
        "lng": 77.601636,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975799,
        "lng": 77.601668,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.975913,
        "lng": 77.601686,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976388,
        "lng": 77.601766,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976418,
        "lng": 77.601771,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976518,
        "lng": 77.601799,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976639,
        "lng": 77.601792,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976736,
        "lng": 77.601785,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.976843,
        "lng": 77.601809,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.977133,
        "lng": 77.601877,
        "is_stop": True,
        "name": "Stop 3: Commercial Zone",
        "sequence": 3
    },
    {
        "lat": 12.977717,
        "lng": 77.602014,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.977937,
        "lng": 77.602069,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979057,
        "lng": 77.602349,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979084,
        "lng": 77.602355,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979112,
        "lng": 77.602362,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979205,
        "lng": 77.602388,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979315,
        "lng": 77.602425,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979386,
        "lng": 77.602489,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979397,
        "lng": 77.602492,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979803,
        "lng": 77.602614,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980182,
        "lng": 77.60273,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980707,
        "lng": 77.602895,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980743,
        "lng": 77.602906,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980731,
        "lng": 77.602941,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980588,
        "lng": 77.603347,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980407,
        "lng": 77.603862,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980265,
        "lng": 77.604264,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980208,
        "lng": 77.604427,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980011,
        "lng": 77.605004,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979945,
        "lng": 77.605196,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979863,
        "lng": 77.605432,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979847,
        "lng": 77.605481,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979819,
        "lng": 77.605555,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979652,
        "lng": 77.606044,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97933,
        "lng": 77.606978,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979322,
        "lng": 77.607003,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979279,
        "lng": 77.607124,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.979374,
        "lng": 77.607157,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980027,
        "lng": 77.607384,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980241,
        "lng": 77.607461,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980859,
        "lng": 77.607676,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981521,
        "lng": 77.607956,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981541,
        "lng": 77.607964,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.98159,
        "lng": 77.608121,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981604,
        "lng": 77.608281,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981497,
        "lng": 77.6086,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981141,
        "lng": 77.609524,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980982,
        "lng": 77.609961,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980972,
        "lng": 77.609987,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.980965,
        "lng": 77.610045,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981036,
        "lng": 77.610099,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.98116,
        "lng": 77.610142,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981407,
        "lng": 77.610227,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981507,
        "lng": 77.610262,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981537,
        "lng": 77.610272,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.981577,
        "lng": 77.610285,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.982206,
        "lng": 77.610513,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.982335,
        "lng": 77.610548,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.98264,
        "lng": 77.61059,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.982899,
        "lng": 77.610627,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.983053,
        "lng": 77.61065,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.983095,
        "lng": 77.610664,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.983289,
        "lng": 77.610762,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.983657,
        "lng": 77.610999,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.983879,
        "lng": 77.611255,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984078,
        "lng": 77.611498,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984289,
        "lng": 77.611713,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984351,
        "lng": 77.611756,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984497,
        "lng": 77.611797,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984567,
        "lng": 77.61202,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.98462,
        "lng": 77.612157,
        "is_stop": True,
        "name": "Stop 4: Tech Hub East",
        "sequence": 4
    },
    {
        "lat": 12.984881,
        "lng": 77.612915,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.984894,
        "lng": 77.613017,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.98511,
        "lng": 77.613066,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.985229,
        "lng": 77.613111,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.985379,
        "lng": 77.613168,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.985921,
        "lng": 77.611963,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.985956,
        "lng": 77.611886,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.986203,
        "lng": 77.61199,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.986331,
        "lng": 77.612053,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.986985,
        "lng": 77.612442,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.987192,
        "lng": 77.612559,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.987284,
        "lng": 77.612592,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.987554,
        "lng": 77.61269,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.987829,
        "lng": 77.612776,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.987981,
        "lng": 77.612822,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.988512,
        "lng": 77.612987,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.989215,
        "lng": 77.613213,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.990447,
        "lng": 77.613836,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.990505,
        "lng": 77.613865,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.990565,
        "lng": 77.613907,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.99063,
        "lng": 77.61392,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.990666,
        "lng": 77.613936,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991154,
        "lng": 77.614191,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991249,
        "lng": 77.61424,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991635,
        "lng": 77.61445,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991709,
        "lng": 77.614475,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991829,
        "lng": 77.614515,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.99258,
        "lng": 77.614856,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.992619,
        "lng": 77.614876,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.99301,
        "lng": 77.615045,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.993178,
        "lng": 77.615122,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.993379,
        "lng": 77.615216,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.993524,
        "lng": 77.615283,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994025,
        "lng": 77.615521,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994277,
        "lng": 77.615656,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994335,
        "lng": 77.61569,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994407,
        "lng": 77.615739,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994535,
        "lng": 77.615855,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994785,
        "lng": 77.615984,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994878,
        "lng": 77.616033,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995122,
        "lng": 77.616163,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995129,
        "lng": 77.616167,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995455,
        "lng": 77.61635,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995458,
        "lng": 77.616352,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995572,
        "lng": 77.616453,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995634,
        "lng": 77.616509,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995738,
        "lng": 77.616661,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995753,
        "lng": 77.616684,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995773,
        "lng": 77.616712,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995732,
        "lng": 77.616774,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995617,
        "lng": 77.616981,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995348,
        "lng": 77.617397,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.995088,
        "lng": 77.617599,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994835,
        "lng": 77.617742,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994565,
        "lng": 77.617901,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994475,
        "lng": 77.617953,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994386,
        "lng": 77.618003,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.994132,
        "lng": 77.618149,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.992865,
        "lng": 77.61879,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.992573,
        "lng": 77.618944,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.991785,
        "lng": 77.619329,
        "is_stop": True,
        "name": "Stop 5: North Terminal",
        "sequence": 5
    }
]

ROUTE_B_WAYPOINTS = [
    {
        "lat": 12.930001,
        "lng": 77.580093,
        "is_stop": True,
        "name": "Stop 1: South Terminal",
        "sequence": 1
    },
    {
        "lat": 12.930157,
        "lng": 77.580091,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.930706,
        "lng": 77.580084,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.930722,
        "lng": 77.580083,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.930773,
        "lng": 77.580083,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.930868,
        "lng": 77.580081,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.930904,
        "lng": 77.580081,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.931324,
        "lng": 77.580075,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.931656,
        "lng": 77.580071,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.932743,
        "lng": 77.580057,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.932808,
        "lng": 77.580056,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.933048,
        "lng": 77.580053,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.933607,
        "lng": 77.580051,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.93368,
        "lng": 77.58005,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.934943,
        "lng": 77.580046,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.935448,
        "lng": 77.580044,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936095,
        "lng": 77.580042,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936247,
        "lng": 77.580041,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936385,
        "lng": 77.580041,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936449,
        "lng": 77.580041,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936695,
        "lng": 77.58004,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936761,
        "lng": 77.580016,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936798,
        "lng": 77.580014,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936794,
        "lng": 77.58009,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936793,
        "lng": 77.58012,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936785,
        "lng": 77.580372,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936762,
        "lng": 77.581158,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936747,
        "lng": 77.581829,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936734,
        "lng": 77.5827,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936711,
        "lng": 77.583711,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936698,
        "lng": 77.583966,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936694,
        "lng": 77.584323,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936692,
        "lng": 77.584486,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936689,
        "lng": 77.584745,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936687,
        "lng": 77.58488,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936686,
        "lng": 77.584959,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936706,
        "lng": 77.584974,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936722,
        "lng": 77.584993,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936733,
        "lng": 77.585016,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936739,
        "lng": 77.58504,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.93674,
        "lng": 77.585065,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936836,
        "lng": 77.585065,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.936925,
        "lng": 77.585064,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.937326,
        "lng": 77.58507,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.937693,
        "lng": 77.585075,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.938944,
        "lng": 77.585096,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.939011,
        "lng": 77.585096,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.939335,
        "lng": 77.585096,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.939657,
        "lng": 77.585102,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.939998,
        "lng": 77.585108,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941296,
        "lng": 77.58513,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941486,
        "lng": 77.585134,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941585,
        "lng": 77.585135,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941641,
        "lng": 77.585136,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941653,
        "lng": 77.585137,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941715,
        "lng": 77.585138,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.941759,
        "lng": 77.585138,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.942457,
        "lng": 77.585151,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.942754,
        "lng": 77.585156,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943248,
        "lng": 77.585164,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943558,
        "lng": 77.58517,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943577,
        "lng": 77.58512,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943611,
        "lng": 77.585078,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943656,
        "lng": 77.58505,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943707,
        "lng": 77.585037,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943762,
        "lng": 77.585042,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943812,
        "lng": 77.585066,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943852,
        "lng": 77.585105,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.943876,
        "lng": 77.585156,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.944027,
        "lng": 77.585171,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.944356,
        "lng": 77.585227,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9445,
        "lng": 77.585263,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.944671,
        "lng": 77.585326,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.944814,
        "lng": 77.585393,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94498,
        "lng": 77.585477,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945161,
        "lng": 77.585585,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945284,
        "lng": 77.585667,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945352,
        "lng": 77.585727,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945408,
        "lng": 77.585785,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945529,
        "lng": 77.585945,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945616,
        "lng": 77.586077,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945684,
        "lng": 77.586196,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.945722,
        "lng": 77.586271,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946006,
        "lng": 77.587139,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946152,
        "lng": 77.587594,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946202,
        "lng": 77.587784,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946237,
        "lng": 77.587917,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946246,
        "lng": 77.587952,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946257,
        "lng": 77.588083,
        "is_stop": True,
        "name": "Stop 2: University Gate",
        "sequence": 2
    },
    {
        "lat": 12.946258,
        "lng": 77.588092,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946324,
        "lng": 77.589629,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946337,
        "lng": 77.589685,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94635,
        "lng": 77.589727,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946362,
        "lng": 77.589759,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946407,
        "lng": 77.589835,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946466,
        "lng": 77.589914,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.946769,
        "lng": 77.590218,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.947373,
        "lng": 77.590822,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.947463,
        "lng": 77.590935,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.947621,
        "lng": 77.591261,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.947632,
        "lng": 77.591282,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.948009,
        "lng": 77.592098,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.948209,
        "lng": 77.592464,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.948521,
        "lng": 77.592891,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.948622,
        "lng": 77.593039,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.948818,
        "lng": 77.593175,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949017,
        "lng": 77.593283,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94908,
        "lng": 77.593317,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94934,
        "lng": 77.593219,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949601,
        "lng": 77.59308,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949987,
        "lng": 77.592856,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950016,
        "lng": 77.59284,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950055,
        "lng": 77.592805,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95036,
        "lng": 77.5925,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950438,
        "lng": 77.592419,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950682,
        "lng": 77.59215,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950915,
        "lng": 77.591896,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950988,
        "lng": 77.591807,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951102,
        "lng": 77.591607,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951336,
        "lng": 77.59103,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951399,
        "lng": 77.59085,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951411,
        "lng": 77.590817,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951464,
        "lng": 77.590666,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951447,
        "lng": 77.590656,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95142,
        "lng": 77.59063,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951385,
        "lng": 77.590557,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951382,
        "lng": 77.590499,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951226,
        "lng": 77.590441,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951211,
        "lng": 77.590436,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951177,
        "lng": 77.590422,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.950011,
        "lng": 77.589971,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949844,
        "lng": 77.589906,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949815,
        "lng": 77.58993,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949779,
        "lng": 77.589946,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949728,
        "lng": 77.58995,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949684,
        "lng": 77.589936,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949661,
        "lng": 77.589922,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94963,
        "lng": 77.589888,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949613,
        "lng": 77.589849,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949608,
        "lng": 77.589803,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949618,
        "lng": 77.589758,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949642,
        "lng": 77.589718,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94966,
        "lng": 77.589701,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949701,
        "lng": 77.589678,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949756,
        "lng": 77.589672,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949805,
        "lng": 77.589686,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.94984,
        "lng": 77.589712,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949864,
        "lng": 77.589746,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.949878,
        "lng": 77.589789,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951209,
        "lng": 77.590316,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951249,
        "lng": 77.590332,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951269,
        "lng": 77.590339,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951431,
        "lng": 77.5904,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951478,
        "lng": 77.590368,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951562,
        "lng": 77.590354,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951625,
        "lng": 77.590374,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951656,
        "lng": 77.590397,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951686,
        "lng": 77.590436,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951707,
        "lng": 77.590492,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951709,
        "lng": 77.590526,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.951838,
        "lng": 77.590575,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95305,
        "lng": 77.591033,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.953776,
        "lng": 77.591307,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.953856,
        "lng": 77.591335,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.953928,
        "lng": 77.591364,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.954044,
        "lng": 77.591407,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.954433,
        "lng": 77.591551,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.954921,
        "lng": 77.591732,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955483,
        "lng": 77.591964,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955502,
        "lng": 77.591969,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955644,
        "lng": 77.592024,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955767,
        "lng": 77.592071,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955804,
        "lng": 77.592085,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95602,
        "lng": 77.592162,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956034,
        "lng": 77.592167,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956118,
        "lng": 77.592198,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956193,
        "lng": 77.592226,
        "is_stop": True,
        "name": "Stop 3: Hospital Square",
        "sequence": 3
    },
    {
        "lat": 12.957262,
        "lng": 77.592638,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958024,
        "lng": 77.592932,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958107,
        "lng": 77.592964,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958315,
        "lng": 77.593044,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958437,
        "lng": 77.593091,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958491,
        "lng": 77.593112,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959472,
        "lng": 77.593499,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959548,
        "lng": 77.593502,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959988,
        "lng": 77.593651,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960197,
        "lng": 77.593721,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960323,
        "lng": 77.593769,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9616,
        "lng": 77.594256,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962123,
        "lng": 77.59446,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962157,
        "lng": 77.594468,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962339,
        "lng": 77.594509,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962356,
        "lng": 77.594572,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962185,
        "lng": 77.594638,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96174,
        "lng": 77.594471,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.961343,
        "lng": 77.594318,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960815,
        "lng": 77.594115,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960807,
        "lng": 77.594178,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960729,
        "lng": 77.594785,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960398,
        "lng": 77.594785,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960036,
        "lng": 77.594734,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9597,
        "lng": 77.594686,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959127,
        "lng": 77.594568,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95865,
        "lng": 77.59447,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958493,
        "lng": 77.594438,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958106,
        "lng": 77.594352,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958273,
        "lng": 77.593765,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95841,
        "lng": 77.593272,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958432,
        "lng": 77.593195,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95804,
        "lng": 77.593048,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.957971,
        "lng": 77.593022,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95765,
        "lng": 77.592894,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.957603,
        "lng": 77.592877,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95731,
        "lng": 77.592768,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.957235,
        "lng": 77.592742,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956747,
        "lng": 77.592558,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956108,
        "lng": 77.592318,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956037,
        "lng": 77.592291,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955954,
        "lng": 77.592259,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955817,
        "lng": 77.592204,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955772,
        "lng": 77.592186,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955733,
        "lng": 77.59217,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955614,
        "lng": 77.592113,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955644,
        "lng": 77.592024,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955767,
        "lng": 77.592071,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.955804,
        "lng": 77.592085,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.95602,
        "lng": 77.592162,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956034,
        "lng": 77.592167,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956118,
        "lng": 77.592198,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.956193,
        "lng": 77.592226,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.957262,
        "lng": 77.592638,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958024,
        "lng": 77.592932,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958107,
        "lng": 77.592964,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958315,
        "lng": 77.593044,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958437,
        "lng": 77.593091,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.958491,
        "lng": 77.593112,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959472,
        "lng": 77.593499,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959548,
        "lng": 77.593502,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.959988,
        "lng": 77.593651,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960197,
        "lng": 77.593721,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.960323,
        "lng": 77.593769,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.9616,
        "lng": 77.594256,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962123,
        "lng": 77.59446,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962157,
        "lng": 77.594468,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962339,
        "lng": 77.594509,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962356,
        "lng": 77.594572,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962377,
        "lng": 77.594615,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962464,
        "lng": 77.594809,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962488,
        "lng": 77.594859,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962537,
        "lng": 77.594974,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962561,
        "lng": 77.595026,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962787,
        "lng": 77.595306,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.962858,
        "lng": 77.595389,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963007,
        "lng": 77.595578,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963085,
        "lng": 77.595664,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963276,
        "lng": 77.595876,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963395,
        "lng": 77.595951,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963561,
        "lng": 77.596092,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.963862,
        "lng": 77.596311,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964218,
        "lng": 77.596527,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964675,
        "lng": 77.596728,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964691,
        "lng": 77.596735,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964763,
        "lng": 77.596767,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964835,
        "lng": 77.596799,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964852,
        "lng": 77.596646,
        "is_stop": True,
        "name": "Stop 4: Metro Interchange",
        "sequence": 4
    },
    {
        "lat": 12.964862,
        "lng": 77.596571,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96487,
        "lng": 77.596501,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964926,
        "lng": 77.596243,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964963,
        "lng": 77.596138,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965029,
        "lng": 77.596008,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96508,
        "lng": 77.595952,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965197,
        "lng": 77.595835,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965333,
        "lng": 77.595722,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965523,
        "lng": 77.595596,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965826,
        "lng": 77.595398,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965938,
        "lng": 77.595332,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966397,
        "lng": 77.595062,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966514,
        "lng": 77.595,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966778,
        "lng": 77.594836,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966827,
        "lng": 77.5948,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966851,
        "lng": 77.594806,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966877,
        "lng": 77.59483,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96689,
        "lng": 77.59485,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96691,
        "lng": 77.594886,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966913,
        "lng": 77.594933,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966895,
        "lng": 77.594986,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966874,
        "lng": 77.595028,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966834,
        "lng": 77.595039,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.96668,
        "lng": 77.595081,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966566,
        "lng": 77.595112,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966469,
        "lng": 77.595139,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966387,
        "lng": 77.595169,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966336,
        "lng": 77.595185,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966291,
        "lng": 77.595204,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966236,
        "lng": 77.595226,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966155,
        "lng": 77.595266,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966131,
        "lng": 77.595279,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965908,
        "lng": 77.595426,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965524,
        "lng": 77.595689,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965349,
        "lng": 77.595814,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965229,
        "lng": 77.595911,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965154,
        "lng": 77.595997,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965116,
        "lng": 77.596061,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965048,
        "lng": 77.596183,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.964999,
        "lng": 77.596313,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965035,
        "lng": 77.596527,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965055,
        "lng": 77.596572,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965087,
        "lng": 77.596641,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965125,
        "lng": 77.596726,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965145,
        "lng": 77.596755,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965191,
        "lng": 77.596737,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965772,
        "lng": 77.596604,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.965852,
        "lng": 77.596596,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966444,
        "lng": 77.596534,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966673,
        "lng": 77.59651,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.966937,
        "lng": 77.596481,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.967456,
        "lng": 77.596436,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.967514,
        "lng": 77.596431,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.968066,
        "lng": 77.596419,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.968303,
        "lng": 77.596488,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.968553,
        "lng": 77.596613,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.968786,
        "lng": 77.596801,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.968991,
        "lng": 77.596977,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969229,
        "lng": 77.5972,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969343,
        "lng": 77.59728,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969625,
        "lng": 77.597496,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969796,
        "lng": 77.597521,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970396,
        "lng": 77.597608,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971027,
        "lng": 77.597687,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97106,
        "lng": 77.597691,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971146,
        "lng": 77.597714,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971204,
        "lng": 77.597755,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97124,
        "lng": 77.597745,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971232,
        "lng": 77.597793,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97122,
        "lng": 77.597828,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971174,
        "lng": 77.597928,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971167,
        "lng": 77.597941,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971127,
        "lng": 77.59798,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.971082,
        "lng": 77.598138,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970949,
        "lng": 77.598603,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97075,
        "lng": 77.599298,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970503,
        "lng": 77.600161,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970481,
        "lng": 77.600239,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970474,
        "lng": 77.600263,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.97036,
        "lng": 77.60066,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970337,
        "lng": 77.600745,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.970191,
        "lng": 77.600708,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969897,
        "lng": 77.600634,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969877,
        "lng": 77.600629,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969735,
        "lng": 77.600598,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969563,
        "lng": 77.600559,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969574,
        "lng": 77.600504,
        "is_stop": False,
        "name": "Path Point"
    },
    {
        "lat": 12.969685,
        "lng": 77.599935,
        "is_stop": True,
        "name": "Stop 5: Central Plaza",
        "sequence": 5
    }
]

def init_db_seed(db: Session, force: bool = False):
    """
    Idempotent development seed script.
    Populates demo users, routes, route points, vehicles, assignments, and initial GPS telemetry.
    Strictly disabled in production unless force=True.
    """
    if settings.APP_ENV == "production" and not force:
        logger.info("[SEED] Skipping automatic development data seed in production environment (APP_ENV='production').")
        return

    logger.info("[SEED] Seeding development / demo data...")

    # 1. Seed Routes & RoutePoints
    route_a = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-101").first()
    if not route_a:
        route_a = BusRoute(
            route_code="ROUTE-101",
            route_name="Route A - Downtown Express [DEV DEMO]",
            description="[DEV DATA] High frequency express route connecting Downtown Hub to North Terminal",
            start_location="Downtown Hub",
            end_location="North Terminal",
            waypoints_json=json.dumps(ROUTE_A_WAYPOINTS)
        )
        db.add(route_a)
        db.flush()

        for i, wp in enumerate(ROUTE_A_WAYPOINTS):
            rp = RoutePoint(
                route_id=route_a.id,
                sequence=wp.get("sequence", i + 1),
                latitude=wp["lat"],
                longitude=wp["lng"],
                name=wp["name"]
            )
            db.add(rp)
        db.flush()

    route_b = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()
    if not route_b:
        route_b = BusRoute(
            route_code="ROUTE-202",
            route_name="Route B - Uptown Shuttle [DEV DEMO]",
            description="[DEV DATA] Scenic shuttle route connecting South Terminal to Central Plaza",
            start_location="South Terminal",
            end_location="Central Plaza",
            waypoints_json=json.dumps(ROUTE_B_WAYPOINTS)
        )
        db.add(route_b)
        db.flush()

        for i, wp in enumerate(ROUTE_B_WAYPOINTS):
            rp = RoutePoint(
                route_id=route_b.id,
                sequence=wp.get("sequence", i + 1),
                latitude=wp["lat"],
                longitude=wp["lng"],
                name=wp["name"]
            )
            db.add(rp)
        db.flush()

    # 2. Seed Vehicles
    vehicle_1 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    if not vehicle_1:
        vehicle_1 = Vehicle(
            vehicle_code="BUS-001",
            license_plate="BUS-1001-PLATE",
            model_name="Standard Transit Bus [DEV DEMO]",
            status="ONLINE",
            assigned_route_id=route_a.id,
            last_latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            last_speed=0.0,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_1)
        db.flush()

    vehicle_2 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    if not vehicle_2:
        vehicle_2 = Vehicle(
            vehicle_code="BUS-002",
            license_plate="BUS-2002-PLATE",
            model_name="City Express Bus [DEV DEMO]",
            status="ONLINE",
            assigned_route_id=route_b.id,
            last_latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            last_speed=0.0,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_2)
        db.flush()

    # 3. Seed Users & Enforce Assignments
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="System Administrator [DEV DEMO]",
            password_hash=get_password_hash("admin123"),
            role="admin",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(admin)
        db.flush()

    user_a = db.query(User).filter(User.email == "usera@example.com").first()
    if not user_a:
        user_a = User(
            email="usera@example.com",
            full_name="User A [DEV DEMO]",
            password_hash=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(user_a)
        db.flush()

    assign_a = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_a.id,
        UserAssignment.is_active == True
    ).first()
    if not assign_a:
        assign_a = UserAssignment(
            user_id=user_a.id,
            route_id=route_a.id,
            vehicle_id=vehicle_1.id,
            is_active=True
        )
        db.add(assign_a)

    user_b = db.query(User).filter(User.email == "userb@example.com").first()
    if not user_b:
        user_b = User(
            email="userb@example.com",
            full_name="User B [DEV DEMO]",
            password_hash=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_b.id,
            assigned_vehicle_id=vehicle_2.id
        )
        db.add(user_b)
        db.flush()

    assign_b = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_b.id,
        UserAssignment.is_active == True
    ).first()
    if not assign_b:
        assign_b = UserAssignment(
            user_id=user_b.id,
            route_id=route_b.id,
            vehicle_id=vehicle_2.id,
            is_active=True
        )
        db.add(assign_b)

    # 4. Seed Initial Telemetry Records
    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_1.id).count() == 0:
        telemetry_1 = GPSTelemetry(
            vehicle_id=vehicle_1.id,
            latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            speed=0.0,
            heading=0.0,
            recorded_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc),
            source="REST"
        )
        db.add(telemetry_1)

    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_2.id).count() == 0:
        telemetry_2 = GPSTelemetry(
            vehicle_id=vehicle_2.id,
            latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            speed=0.0,
            heading=0.0,
            recorded_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc),
            source="REST"
        )
        db.add(telemetry_2)

    db.commit()
    logger.info("[SEED] Development data seeded successfully (Idempotent execution verified).")

