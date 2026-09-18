# ==========================================
# SMARTSCHED AI
# VIRTUAL FACTORY
# ==========================================


# ==========================================
# MACHINE DATA
# ==========================================

machines = {

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


# ==========================================
# GET FACTORY STATE
# ==========================================

def get_factory_state():

    return machines


# ==========================================
# FAIL MACHINE
# ==========================================

def fail_machine(machine_id, downtime=120):

    machine_id = machine_id.upper()

    if machine_id not in machines:

        return False

    machines[machine_id]["status"] = "DOWN"

    machines[machine_id]["downtime"] = downtime

    return True


# ==========================================
# RECOVER MACHINE
# ==========================================

def recover_machine(machine_id):

    machine_id = machine_id.upper()

    if machine_id not in machines:

        return False

    machines[machine_id]["status"] = "AVAILABLE"

    machines[machine_id]["downtime"] = 0

    return True


# ==========================================
# DISPLAY FACTORY
# ==========================================

def show_machines():

    print()
    print("SMARTSCHED VIRTUAL FACTORY")
    print("---------------------------")

    for machine, data in machines.items():

        print(
            machine,
            ":",
            data["status"],
            "| Downtime:",
            data["downtime"],
            "minutes"
        )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("INITIAL FACTORY")

    show_machines()

    print()
    print("SIMULATING MACHINE FAILURE")
    print("---------------------------")

    fail_machine("M2", 120)

    print()
    print("ALERT!")
    print("M2 has FAILED.")
    print("Downtime: 120 minutes")

    print()
    print("AFTER MACHINE FAILURE")

    show_machines()