from fastapi import FastAPI
from optimizer.scheduler import optimize_schedule
from simulation.factory import (
    get_factory_state,
    fail_machine,
    recover_machine
)

app = FastAPI(
    title="SmartSched AI",
    description="Smart Production Scheduling API",
    version="1.0"
)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "SmartSched AI Backend is running"
    }


# ==========================================
# FACTORY STATUS
# ==========================================

@app.get("/factory")
def get_factory():
    return get_factory_state()


# ==========================================
# CURRENT OPTIMIZED SCHEDULE
# ==========================================

@app.get("/schedule")
def get_schedule():

    factory_state = get_factory_state()

    result = optimize_schedule(factory_state)

    return result


# ==========================================
# MACHINE FAILURE
# ==========================================

@app.post("/machine-failure/{machine_id}")
def machine_failure(machine_id: str):

    machine_id = machine_id.upper()

    # Simulate 120-minute machine failure
    success = fail_machine(machine_id, 120)

    if not success:
        return {
            "error": "Machine not found",
            "machine_id": machine_id
        }

    # Get updated factory state
    factory_state = get_factory_state()

    # Re-optimize automatically
    result = optimize_schedule(factory_state)

    return {
        "event": "MACHINE_FAILURE",
        "message": machine_id + " has failed",
        "machine_id": machine_id,
        "downtime_minutes": 120,
        "factory": factory_state,
        "new_schedule": result
    }


# ==========================================
# MACHINE RECOVERY
# ==========================================

@app.post("/machine-recover/{machine_id}")
def machine_recover(machine_id: str):

    machine_id = machine_id.upper()

    success = recover_machine(machine_id)

    if not success:
        return {
            "error": "Machine not found",
            "machine_id": machine_id
        }

    # Get updated factory state
    factory_state = get_factory_state()

    # Re-optimize after recovery
    result = optimize_schedule(factory_state)

    return {
        "event": "MACHINE_RECOVERY",
        "message": machine_id + " has recovered",
        "machine_id": machine_id,
        "factory": factory_state,
        "new_schedule": result
    }


# ==========================================
# OPTIMIZE CUSTOM FACTORY STATE
# ==========================================

@app.post("/optimize")
def optimize_custom_factory(factory_state: dict):

    # --------------------------------------
    # Convert API machine-list format
    # into optimizer dictionary format
    # --------------------------------------

    if "machines" in factory_state:

        machines_list = factory_state["machines"]

        machine_state = {}

        for machine in machines_list:

            machine_id = machine["id"]

            machine_state[machine_id] = {
                "status": machine.get(
                    "status",
                    "AVAILABLE"
                ).upper(),

                "downtime": machine.get(
                    "downtime",
                    0
                )
            }

        factory_state = machine_state

    # --------------------------------------
    # Run optimization
    # --------------------------------------

    result = optimize_schedule(factory_state)

    # --------------------------------------
    # Return result
    # --------------------------------------

    return result