from pydantic import ValidationError
from bson import ObjectId
from app import user_database,user_simulation_database, simulation_database
from ..models.userSimulation import UserSimulationSchema
from ..models.user import UserSchema
from ..models.simulation import SimulationSchema


def userSimulationController(data):
    try:
        userSimulations = list(user_simulation_database.find({"_id": ObjectId(data['_id'])}))
        if not userSimulations:
            return "", False, "No simulation found"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]

        users = list(user_database.find({"_id": ObjectId(userSimulations[0]["userId"])}))
        users = [UserSchema(**users).dict() for users in users]

        simulations = list(simulation_database.find({"_id": ObjectId(userSimulations[0]["simulationId"])}))
        simulations = [SimulationSchema(**simulation).dict() for simulation in simulations]

        userSimulations[0]["userId"] = users
        userSimulations[0]["simulationId"] = simulations
        return userSimulations, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def startUserSimulationController(data):
    try:
        # Validate incoming data using Pydantic schema
        simulationData = UserSimulationSchema(**data)

        result = user_simulation_database.insert_one(simulationData.dict())

        if result:
            return "", True, "Data inserted successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"