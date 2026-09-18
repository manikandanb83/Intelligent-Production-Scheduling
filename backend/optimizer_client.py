import httpx

# Temporary address for Member 3's optimizer
OPTIMIZER_URL = "http://127.0.0.1:9000"


async def send_to_optimizer(factory_state):

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.post(
                f"{OPTIMIZER_URL}/optimize",
                json=factory_state
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:

        return {
            "status": "OPTIMIZER_UNAVAILABLE",
            "message": str(e)
        }