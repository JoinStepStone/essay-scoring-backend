from pydantic import ValidationError
from datetime import datetime
from bson import ObjectId
from app import user_database,user_simulation_database, simulation_database
from ..models.user import UserSchema
from ..models.userSimulation import UserSimulationSchema
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

def getAllTheStuedents():
    try:

        users = list(user_database.find({"role": "Student"}))
        for user in users:
            user['_id'] = str(user['_id']) 
        users = [UserSchema(**user).dict() for user in users]

        for user in users:
            userSimulations = list(user_simulation_database.find({"userId": user["id"]}))
            if(len(userSimulations)):
                print(userSimulations)
            else:
                user["avgScore"] = 0
                user["examTaken"] = 0

        if users:
            return users, True, "Data fetched successfully"
        else:
            return [], True, "Data fetched successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def getAllTheSimulations():
    try:

        simulations = list(simulation_database.find({}))
        for simulation in simulations:
            simulation['_id'] = str(simulation['_id']) 

        simulations = len(simulations) and [SimulationSchema(**simulation).dict() for simulation in simulations]

        if simulations:
            return simulations, True, "Data fetched successfully"
        else:
            return [], True, "Data fetched successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def getTheSimulationDetails(data): 
    try:

        userSimulations = list(user_simulation_database.find({"simulationId": data['simulationId']},{"_id": 0}))
        print("1")
        if not userSimulations:
            return "", False, "No simulation found"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]
        print("2",userSimulations)
        
        # Step 1: Convert grades to numeric and sort the data
        userSimulations = sorted(userSimulations, key=lambda x: float(x['grade']) if x['grade'] is not None else 0.0, reverse=True)

        # Step 2: Assign ranks
        for i, item in enumerate(userSimulations, start=1):
            item['rank'] = i
            
        for userSimulation in userSimulations:
            userSimulation["userId"] = list(user_database.find({"_id": ObjectId(userSimulation["userId"])},{"_id": 0}))[0]

        print("3")
        result = {
            "simulationDetails": list(simulation_database.find({"_id": ObjectId(userSimulations[0]["simulationId"])},{"_id": 0}))[0],
            "result": userSimulations
        }
        return result, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"