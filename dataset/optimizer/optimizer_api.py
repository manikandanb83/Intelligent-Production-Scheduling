from scheduler import optimize_schedule


# ==========================================
# DEFAULT FACTORY STATE
# ==========================================

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


# ==========================================
# RUN OPTIMIZER
# ==========================================

result = optimize_schedule(factory_state)


# ==========================================
# DISPLAY RESULT
# ==========================================

print()
print("SMARTSCHED API TEST")
print("===================")

print()

print("SCHEDULE")
print("--------")

for item in result["schedule"]:

    print(
        item["order_id"],
        "|",
        item["machine"],
        "| Start:",
        item["start"],
        "| End:",
        item["end"]
    )


print()

print("KPIs")
print("----")

print(
    "Production time:",
    result["kpis"]["makespan"],
    "minutes"
)

print(
    "Late orders:",
    result["kpis"]["late_orders"]
)

print(
    "On-time orders:",
    result["kpis"]["on_time_orders"]
)

print(
    "Overall utilization:",
    result["kpis"]["overall_utilization"],
    "%"
)