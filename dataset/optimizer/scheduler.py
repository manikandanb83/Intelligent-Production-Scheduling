from ortools.sat.python import cp_model


# ============================================================
# SMARTSCHED AI
# Adaptive Production Scheduling Under Uncertainty
# ============================================================

MACHINES = ["M1", "M2", "M3", "M4"]


# ============================================================
# PRODUCTION ORDERS
# ============================================================

ORDERS = [
    {"id": "O101", "time": 60, "priority": 5, "deadline": 240},
    {"id": "O102", "time": 90, "priority": 4, "deadline": 300},
    {"id": "O103", "time": 75, "priority": 5, "deadline": 240},
    {"id": "O104", "time": 45, "priority": 3, "deadline": 360},
    {"id": "O105", "time": 80, "priority": 2, "deadline": 420},
    {"id": "O106", "time": 50, "priority": 4, "deadline": 360},
]


# ============================================================
# MACHINE COMPATIBILITY
# ============================================================

COMPATIBILITY = {
    "O101": ["M1", "M2"],
    "O102": ["M2", "M3"],
    "O103": ["M1", "M3"],
    "O104": ["M3", "M4"],
    "O105": ["M1", "M4"],
    "O106": ["M2", "M4"],
}


# ============================================================
# GET MACHINE DATA
# ============================================================

def get_machine_data(factory_state, machine_id):

    machines = factory_state.get("machines", [])

    for machine in machines:

        if machine.get("id") == machine_id:
            return machine

    return {
        "id": machine_id,
        "status": "AVAILABLE",
        "downtime": 0
    }


# ============================================================
# OPTIMIZER
# ============================================================

def optimize_schedule(factory_state):

    model = cp_model.CpModel()

    MAX_TIME = 1000

    start_times = {}
    end_times = {}
    assignments = {}
    late_orders = {}

    # ========================================================
    # CREATE VARIABLES
    # ========================================================

    for order in ORDERS:

        order_id = order["id"]
        processing_time = order["time"]
        deadline = order["deadline"]

        start_times[order_id] = model.NewIntVar(
            0,
            MAX_TIME,
            f"start_{order_id}"
        )

        end_times[order_id] = model.NewIntVar(
            0,
            MAX_TIME,
            f"end_{order_id}"
        )

        model.Add(
            end_times[order_id]
            ==
            start_times[order_id] + processing_time
        )

        assignments[order_id] = {}

        # ====================================================
        # MACHINE ASSIGNMENTS
        # ====================================================

        for machine in COMPATIBILITY[order_id]:

            assign = model.NewBoolVar(
                f"{order_id}_{machine}"
            )

            assignments[order_id][machine] = assign

            machine_data = get_machine_data(
                factory_state,
                machine
            )

            status = str(
                machine_data.get(
                    "status",
                    "AVAILABLE"
                )
            ).upper()

            downtime = int(
                machine_data.get(
                    "downtime",
                    0
                )
            )

            # ------------------------------------------------
            # MACHINE DOWN
            # ------------------------------------------------

            if status == "DOWN":

                model.Add(
                    start_times[order_id] >= downtime
                ).OnlyEnforceIf(assign)

        # ====================================================
        # EXACTLY ONE MACHINE
        # ====================================================

        model.Add(
            sum(assignments[order_id].values()) == 1
        )

        # ====================================================
        # LATE ORDER
        # ====================================================

        late_orders[order_id] = model.NewBoolVar(
            f"late_{order_id}"
        )

        model.Add(
            end_times[order_id] > deadline
        ).OnlyEnforceIf(
            late_orders[order_id]
        )

        model.Add(
            end_times[order_id] <= deadline
        ).OnlyEnforceIf(
            late_orders[order_id].Not()
        )

    # ============================================================
    # NO OVERLAP ON MACHINES
    # ============================================================

    for machine in MACHINES:

        intervals = []

        for order in ORDERS:

            order_id = order["id"]
            processing_time = order["time"]

            if machine in COMPATIBILITY[order_id]:

                interval = model.NewOptionalIntervalVar(
                    start_times[order_id],
                    processing_time,
                    end_times[order_id],
                    assignments[order_id][machine],
                    f"{order_id}_{machine}_interval"
                )

                intervals.append(interval)

        if intervals:

            model.AddNoOverlap(intervals)

    # ============================================================
    # MAKESPAN
    # ============================================================

    makespan = model.NewIntVar(
        0,
        MAX_TIME,
        "makespan"
    )

    for order in ORDERS:

        model.Add(
            makespan >= end_times[order["id"]]
        )

    # ============================================================
    # OBJECTIVE
    # ============================================================

    total_late_orders = sum(
        late_orders[order["id"]]
        for order in ORDERS
    )

    # First minimize late orders,
    # then minimize total production time.

    model.Minimize(
        total_late_orders * 10000
        + makespan
    )

    # ============================================================
    # SOLVE
    # ============================================================

    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 10

    status = solver.Solve(model)

    # ============================================================
    # CHECK RESULT
    # ============================================================

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        return {
            "status": "NO_FEASIBLE_SCHEDULE",
            "schedule": [],
            "kpis": {}
        }

    # ============================================================
    # BUILD SCHEDULE
    # ============================================================

    schedule = []

    machine_work_time = {
        machine: 0
        for machine in MACHINES
    }

    late_count = 0

    for order in ORDERS:

        order_id = order["id"]

        selected_machine = None

        for machine in COMPATIBILITY[order_id]:

            if solver.Value(
                assignments[order_id][machine]
            ) == 1:

                selected_machine = machine

                machine_work_time[machine] += (
                    order["time"]
                )

                break

        late = bool(
            solver.Value(
                late_orders[order_id]
            )
        )

        if late:

            late_count += 1

        schedule.append({

            "order_id": order_id,

            "machine": selected_machine,

            "start": solver.Value(
                start_times[order_id]
            ),

            "end": solver.Value(
                end_times[order_id]
            ),

            "processing_time": order["time"],

            "deadline": order["deadline"],

            "priority": order["priority"],

            "late": late
        })

    # ============================================================
    # SORT BY START TIME
    # ============================================================

    schedule.sort(
        key=lambda x: x["start"]
    )

    # ============================================================
    # KPI CALCULATION
    # ============================================================

    total_time = solver.Value(makespan)

    machine_utilization = {}

    total_work = 0

    total_capacity = 0

    for machine in MACHINES:

        work = machine_work_time[machine]

        total_work += work

        if total_time > 0:

            utilization = (
                work / total_time
            ) * 100

        else:

            utilization = 0

        machine_utilization[machine] = round(
            utilization,
            2
        )

        total_capacity += total_time

    if total_capacity > 0:

        overall_utilization = (
            total_work / total_capacity
        ) * 100

    else:

        overall_utilization = 0

    # ============================================================
    # RETURN RESULT
    # ============================================================

    return {

        "status": "OPTIMAL"
        if status == cp_model.OPTIMAL
        else "FEASIBLE",

        "schedule": schedule,

        "kpis": {

            "makespan": total_time,

            "late_orders": late_count,

            "on_time_orders":
                len(ORDERS) - late_count,

            "overall_utilization":
                round(
                    overall_utilization,
                    2
                ),

            "machine_utilization":
                machine_utilization
        }
    }