from flask import jsonify, make_response
from pydantic import ValidationError
from bson import ObjectId
from app import user_database,user_simulation_database, simulation_database
from ..models.userSimulation import UserSimulationSchema
from ..models.user import UserSchema
from ..models.simulation import SimulationSchema

def simulationByClassCodeController(data):
    try:
        simulations = list(simulation_database.find(
            {"classCode": data['classCode']}, 
            {"classCode": 1, "simulationName": 1, "_id" : 0}
        ))

        if not simulations:
            return "", False, "No simulation found"
        
        return simulations, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def simulationSelectionController(data):
    try:
        # Validate incoming data using Pydantic schema
        simulationData = UserSimulationSchema(**data)

        result = user_simulation_database.insert_one(simulationData.dict())

        if result:
            return "", True, "Data inserted successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"


def getSimulationSelectedController(data):
    try:
        userSimulations = list(user_simulation_database.find({"userId": data['userId']},{"_id": 0}))
        if not userSimulations:
            return "", False, "No simulation found"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]

        simulations = []
        for userSimulation in userSimulations:
            simulationObject = list(simulation_database.find({"_id": ObjectId(userSimulation["simulationId"])},{"_id": 0}))
            simulations.append(simulationObject[0])
            
        return simulations, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"


def simulationDetailController(data):
    try:
        userSimulations = list(user_simulation_database.find({"simulationId": data['simulationId']},{"_id": 0}))
        if not userSimulations:
            return "", False, "No simulation found"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]
        
        for userSimulation in userSimulations:
            userSimulation["simulationId"] = list(simulation_database.find({"_id": ObjectId(userSimulation["simulationId"])},{"_id": 0}))[0]

        return userSimulations, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"


def updateUserSimulationController(data):
    try:
        # Validate using Pydantic schema
        simulationData = UserSimulationSchema(**data)
        # Define the filter to locate the document to update
        filter_query = {
            "userId": simulationData.userId,
            "simulationId": simulationData.simulationId
        }
        
        # Define the update query
        update_query = {
            "$set": simulationData.dict(exclude_unset=True)
        }
        
        # Update the document
        result = user_simulation_database.update_one(filter_query, update_query)

        result1 = list(simulation_database.find(
            { "_id": ObjectId(simulationData.simulationId)}, 
            {"participants": 1}
        ))
        
        participants = result1[0]["participants"] + 1
        
        filter_query_simulation = {
            "_id": ObjectId(simulationData.simulationId)
        }
        # Define the update query
        update_query_simulation = {
            "$set": {"participants": participants}
        }
        
        # Update the document
        result1 = simulation_database.update_one(filter_query_simulation, update_query_simulation)
        
        if result1.matched_count == 0 or result.matched_count == 0:
            if result1.modified_count > 0 or result.modified_count > 0:
                print("Document updated successfully.")
            else:
                print("Document matched but no changes were made (maybe the data was already the same).")
            return str(e), False, "Something went bad"
        
        return "", True, "Successfully updated the record"
    except ValidationError as e:
        return str(e), False, "Something went bad"

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