from pydantic import ValidationError
from app import user_database,user_simulation_database, simulation_database

from ..models.simulation import SimulationSchema

def createSimulationController(data):
    try:
        # Validate incoming data using Pydantic schema
        simulationData = SimulationSchema(**data)

        result = simulation_database.insert_one(simulationData.dict())

        if result:
            return "", True, "Data inserted successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"