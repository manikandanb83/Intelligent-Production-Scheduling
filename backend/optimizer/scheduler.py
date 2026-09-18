"""
SmartSched AI
Adaptive Production Scheduling Under Uncertainty

Optimization engine using Google OR-Tools CP-SAT.

The scheduler:
    1. Reads the current factory condition.
    2. Checks machine availability.
    3. Assigns orders only to compatible machines.
    4. Schedules production without machine overlap.
    5. Handles machine downtime.
    6. Considers deadlines and priorities.
    7. Minimizes late orders first.
    8. Minimizes overall makespan second.
    9. Returns schedule and KPI information.
"""

from ortools.sat.python import cp_model


# =========================================================
# MACHINE DATA
# =========================================================

MACHINES = [
    "M1",
    "M2",
    "M3",
    "M4"
]


# =========================================================
# PRODUCTION ORDERS
# =========================================================

ORDERS = [
    {
        "id": "O101",
        "time": 60,
        "priority": 5,
        "deadline": 240
    },
    {
        "id": "O102",
        "time": 90,
        "priority": 4,
        "deadline": 300
    },
    {
        "id": "O103",
        "time": 75,
        "priority": 5,
        "deadline": 240
    },
    {
        "id": "O104",
        "time": 45,
        "priority": 3,
        "deadline": 360
    },
    {
        "id": "O105",
        "time": 80,
        "priority": 2,
        "deadline": 420
    },
    {
        "id": "O106",
        "time": 50,
        "priority": 4,
        "deadline": 360
    }
]


# =========================================================
# MACHINE COMPATIBILITY
# =========================================================

COMPATIBILITY = {
    "O101": ["M1", "M2"],
    "O102": ["M2", "M3"],
    "O103": ["M1", "M3"],
    "O104": ["M3", "M4"],
    "O105": ["M1", "M4"],
    "O106": ["M2", "M4"]
}


# =========================================================
# HELPER: GET MACHINE DATA
# =========================================================

def get_machine_data(factory_state, machine_id):
    """
    Supports both factory-state formats.

    Format 1:

        {
            "M1": {
                "status": "AVAILABLE",
                "downtime": 0
            }
        }

    Format 2:

        {
            "machines": [
                {
                    "id": "M1",
                    "status": "AVAILABLE",
                    "downtime": 0
                }
            ]
        }
    """

    if not isinstance(factory_state, dict):
        return None

    # -----------------------------------------------------
    # Format 1: machine dictionary
    # -----------------------------------------------------

    if machine_id in factory_state:

        data = factory_state[machine_id]

        if isinstance(data, dict):
            return {
                "id": machine_id,
                **data
            }

    # -----------------------------------------------------
    # Format 2: machines list
    # -----------------------------------------------------

    if "machines" in factory_state:

        machines = factory_state["machines"]

        if isinstance(machines, list):

            for machine in machines:

                if (
                    isinstance(machine, dict)
                    and machine.get("id") == machine_id
                ):
                    return machine

    return None


# =========================================================
# HELPER: CHECK MACHINE AVAILABILITY
# =========================================================

def machine_is_available(factory_state, machine_id):

    machine = get_machine_data(
        factory_state,
        machine_id
    )

    # If machine information does not exist,
    # assume unavailable for safety.
    if machine is None:
        return False

    status = str(
        machine.get(
            "status",
            "AVAILABLE"
        )
    ).upper()

    return status not in [
        "DOWN",
        "FAILED",
        "OFFLINE",
        "UNAVAILABLE"
    ]


# =========================================================
# HELPER: MACHINE DOWNTIME
# =========================================================

def get_machine_downtime(factory_state, machine_id):

    machine = get_machine_data(
        factory_state,
        machine_id
    )

    if machine is None:
        return 0

    try:
        downtime = int(
            machine.get(
                "downtime",
                0
            )
        )

    except (TypeError, ValueError):
        downtime = 0

    return max(
        0,
        downtime
    )


# =========================================================
# MAIN OPTIMIZATION FUNCTION
# =========================================================

def optimize_schedule(factory_state):

    # -----------------------------------------------------
    # CREATE CP-SAT MODEL
    # -----------------------------------------------------

    model = cp_model.CpModel()

    # -----------------------------------------------------
    # BASIC TIME HORIZON
    # -----------------------------------------------------

    total_processing_time = sum(
        order["time"]
        for order in ORDERS
    )

    max_downtime = max(
        [
            get_machine_downtime(
                factory_state,
                machine
            )
            for machine in MACHINES
        ]
        + [0]
    )

    # Large enough scheduling horizon
    MAX_TIME = total_processing_time + max_downtime + 500