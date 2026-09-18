from fastapi import FastAPI

from optimizer.scheduler import optimize_schedule

from simulation.factory import (
    get_factory_state,
    fail_machine,
    recover_machine
)


# =========================================================
# REQUEST MODELS
# =========================================================

class MachineFailure(BaseModel):
    machine_id: str
    downtime_minutes: int


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="SmartSched AI",
    description="Adaptive Production Scheduling Backend",
    version="1.0.0"
)


# =========================================================
# CURRENT FACTORY STATE
# =========================================================

factory_state = {

    "machines": [
        {
            "id": "M1",
            "name": "CNC Machine 1",
            "available": True,
            "status": "RUNNING"
        },
        {
            "id": "M2",
            "name": "CNC Machine 2",
            "available": True,
            "status": "RUNNING"
        },
        {
            "id": "M3",
            "name": "Assembly Machine",
            "available": True,
            "status": "IDLE"
        },
        {
            "id": "M4",
            "name": "Finishing Machine",
            "available": True,
            "status": "IDLE"
        }
    ],

    "orders": [
        {
            "id": "O101",
            "product": "Gear Housing",
            "quantity": 50,
            "priority": 3,
            "processing_time": 120,
            "deadline": 480
        },
        {
            "id": "O102",
            "product": "Shaft",
            "quantity": 80,
            "priority": 2,
            "processing_time": 90,
            "deadline": 360
        },
        {
            "id": "O103",
            "product": "Bearing",
            "quantity": 100,
            "priority": 1,
            "processing_time": 60,
            "deadline": 300
        }
    ],

    "workers": [
        {
            "id": "W1",
            "name": "Operator 1",
            "available": True
        },
        {
            "id": "W2",
            "name": "Operator 2",
            "available": True
        },
        {
            "id": "W3",
            "name": "Operator 3",
            "available": True
        }
    ],

    "materials": [
        {
            "id": "MAT-A",
            "name": "Steel",
            "available_quantity": 500
        },
        {
            "id": "MAT-B",
            "name": "Aluminium",
            "available_quantity": 300
        }
    ]
}


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "system": "SmartSched AI",
        "status": "online",
        "message": "Backend is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# FACTORY STATE
# =========================================================

@app.get("/factory-state")
def get_factory_state():

    return factory_state


# =========================================================
# MACHINE FAILURE / DISRUPTION
# =========================================================

@app.post("/disruption/machine-failure")
def machine_failure(disruption: MachineFailure):

    machine_found = False

    for machine in factory_state["machines"]:

        if machine["id"] == disruption.machine_id:

            machine["available"] = False
            machine["status"] = "DOWN"

            machine_found = True

            break

    if not machine_found:

        return {
            "status": "ERROR",
            "message": f"Machine {disruption.machine_id} not found"
        }

    return {
        "event": "MACHINE_FAILURE",
        "machine_id": disruption.machine_id,
        "downtime_minutes": disruption.downtime_minutes,
        "status": "DISRUPTION_DETECTED",
        "machine_status": "DOWN",
        "action": "REOPTIMIZATION_REQUIRED"
    }
# =========================================================
# RE-OPTIMIZATION
# =========================================================

@app.post("/reoptimize")
async def reoptimize():

    down_machines = []

    for machine in factory_state["machines"]:
        if machine["available"] is False:
            down_machines.append(machine["id"])

    if not down_machines:
        return {
            "status": "NO_DISRUPTION",
            "down_machines": [],
            "message": "All machines are currently available"
        }

    # Send current factory state to the optimization engine
    optimizer_result = await send_to_optimizer(factory_state)

    return {
        "status": "REOPTIMIZATION_TRIGGERED",
        "down_machines": down_machines,
        "optimizer_result": optimizer_result
    }