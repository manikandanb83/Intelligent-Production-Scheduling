"""
SmartSched AI - Virtual Factory Simulation

This module simulates the current condition of factory machines.
It allows the backend to:
    - Read machine status
    - Simulate machine failures
    - Recover machines
    - Track downtime
"""

# ---------------------------------------------------------
# INITIAL FACTORY STATE
# ---------------------------------------------------------

factory_state = {
    "M1": {
        "status": "AVAILABLE",
        "downtime": 0
    },
    "M2": {
        "status": "AVAILABLE",
        "downtime": 0
    },
    "M3": {
        "status": "AVAILABLE",
        "downtime": 0
    },
    "M4": {
        "status": "AVAILABLE",
        "downtime": 0
    }
}


# ---------------------------------------------------------
# GET CURRENT FACTORY STATE
# ---------------------------------------------------------

def get_factory_state():
    """
    Return the current state of all machines.
    """
    return factory_state


# ---------------------------------------------------------
# FAIL A MACHINE
# ---------------------------------------------------------

def fail_machine(machine_id, downtime=120):
    """
    Simulate a machine failure.

    Example:
        fail_machine("M2", 120)

    M2 will become DOWN for 120 minutes.
    """

    machine_id = machine_id.upper()

    # Check whether machine exists
    if machine_id not in factory_state:
        return False

    # Change machine state
    factory_state[machine_id]["status"] = "DOWN"
    factory_state[machine_id]["downtime"] = downtime

    return True


# ---------------------------------------------------------
# RECOVER A MACHINE
# ---------------------------------------------------------

def recover_machine(machine_id):
    """
    Recover a failed machine.

    Example:
        recover_machine("M2")
    """

    machine_id = machine_id.upper()

    # Check whether machine exists
    if machine_id not in factory_state:
        return False

    # Restore machine
    factory_state[machine_id]["status"] = "AVAILABLE"
    factory_state[machine_id]["downtime"] = 0

    return True


# ---------------------------------------------------------
# RESET ENTIRE FACTORY
# ---------------------------------------------------------

def reset_factory():
    """
    Reset all machines to AVAILABLE state.

    Useful for hackathon demonstrations when you want
    to return to the original factory condition.
    """

    for machine_id in factory_state:
        factory_state[machine_id]["status"] = "AVAILABLE"
        factory_state[machine_id]["downtime"] = 0

    return True


# ---------------------------------------------------------
# GET ONE MACHINE
# ---------------------------------------------------------

def get_machine(machine_id):
    """
    Return information about one machine.
    """

    machine_id = machine_id.upper()

    if machine_id not in factory_state:
        return None

    return factory_state[machine_id]