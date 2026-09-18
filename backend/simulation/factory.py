"""
SmartSched AI - Virtual Factory Simulation
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
    return factory_state


# ---------------------------------------------------------
# FAIL MACHINE
# ---------------------------------------------------------

def fail_machine(machine_id, downtime=120):
    machine_id = machine_id.upper()

    if machine_id not in factory_state:
        return False

    factory_state[machine_id]["status"] = "DOWN"
    factory_state[machine_id]["downtime"] = downtime

    return True


# ---------------------------------------------------------
# RECOVER MACHINE
# ---------------------------------------------------------

def recover_machine(machine_id):
    machine_id = machine_id.upper()

    if machine_id not in factory_state:
        return False

    factory_state[machine_id]["status"] = "AVAILABLE"
    factory_state[machine_id]["downtime"] = 0

    return True


# ---------------------------------------------------------
# RESET FACTORY
# ---------------------------------------------------------

def reset_factory():
    for machine_id in factory_state:
        factory_state[machine_id]["status"] = "AVAILABLE"
        factory_state[machine_id]["downtime"] = 0

    return True


# ---------------------------------------------------------
# GET ONE MACHINE
# ---------------------------------------------------------

def get_machine(machine_id):
    machine_id = machine_id.upper()

    if machine_id not in factory_state:
        return None

    return factory_state[machine_id]