from flask import jsonify, make_response
from pydantic import ValidationError
from bson import ObjectId
from app import user_database,user_simulation_database, simulation_database
from ..models.userSimulation import UserSimulationSchema
from ..models.user import UserSchema
from ..models.simulation import SimulationSchema

def updateMeController(data):
    try:
        user = UserSchema(**data)

        filter_query_simulation = {
            "_id": ObjectId(user.id)
        }
        # Define the update query
        update_query_simulation = {
            "$set": user.dict(exclude_unset=True)
        }
        
        # Update the document
        result1 = user_database.update_one(filter_query_simulation, update_query_simulation)

        if result1.matched_count == 0:
            if result1.modified_count > 0:
                print("Document updated successfully.")
            else:
                print("Document matched but no changes were made (maybe the data was already the same).")
            return str(e), False, "Something went bad"

        return "", True, "Data updated successfully"


    except ValidationError as e:
        return str(e), False, "Something went bad"

def getMeController(data):
    try:
        users = list(user_database.find(
            {
                "role": "Student",
                "_id": ObjectId(data['userId'])
            }
        ))

        if not users:
            return "", False, "No student found under this name"

        users[0]["_id"] = str(users[0]["_id"])
        return users[0], True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def simulationByClassCodeController(data):
    try:
        simulations = list(simulation_database.find(
            {"classCode": data['classCode']}, 
            {"classCode": 1, "simulationName": 1}
        ))

        if not simulations:
            return "", False, "No simulation found"
        
        simulations[0]["_id"] = str(simulations[0]["_id"])
        return simulations[0], True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def simulationSelectionController(data):
    try:

        # Validate incoming data using Pydantic schema
        simulation = list(simulation_database.find( {"classCode" : data["classCode"] }))
        if simulation:
            found = list(user_simulation_database.find({"simulationId":simulation[0]["_id"], "userId": data["userId"]}))
            userSimulatio = UserSimulationSchema(**{"simulationId":str(simulation[0]["_id"]), "userId": data["userId"]})
            if found:
                return "", False, "You are already registered"

            result = user_simulation_database.insert_one(userSimulatio.dict())

            if result:
                return "", True, "Data inserted successfully"

        return "", False, "No simulation found"

    except ValidationError as e:
        return str(e), False, "Something went bad"


def getSimulationSelectedController(data):
    try:
        userSimulations = list(user_simulation_database.find({"userId": data['userId']},{"_id": 0}))

        if not userSimulations:
            return [], True, "Successfully fetched"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]

        simulations = []
        for userSimulation in userSimulations:
            simulationObject = list(simulation_database.find({"_id": ObjectId(userSimulation["simulationId"])},{"id": 0}))
            simulationObject[0]["grade"] = userSimulation["grade"]
            simulationObject[0]["_id"] = str(simulationObject[0]["_id"])
            simulations.append(simulationObject[0])
            
        return simulations, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"


def simulationDetailController(data): 
    try:
        userSimulations = list(user_simulation_database.find({"simulationId": data['simulationId'],"userId": data['userId']},{"_id": 0}))
        if not userSimulations:
            return "", False, "No simulation found"

        userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]
        simulationDetails = list(simulation_database.find({"_id": ObjectId(userSimulations[0]["simulationId"])},{"_id": 0}))[0]
        userDetails = list(user_database.find({"_id": ObjectId(userSimulations[0]["userId"])},{"_id": 0}))[0]
        
        result = {
            "simulationDetails": simulationDetails,
            "userDetails": userDetails,
            "result": userSimulations
        }
        return result, True, "Successfully fetched"

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
        
        gradeCheck = list(user_simulation_database.find(filter_query))[0]
        print("\n", gradeCheck, "\n")
        # Update the document
        result = user_simulation_database.update_one(filter_query, update_query)

        result1 = list(simulation_database.find(
            { "_id": ObjectId(simulationData.simulationId)}, 
            {"participants": 1}
        ))
        
        if not (gradeCheck["grade"]):
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
        
        if result.matched_count == 0:
            if result.modified_count > 0:
                print("Document updated successfully.")
            else:
                print("Document matched but no changes were made (maybe the data was already the same).")
            return str(e), False, "Something went bad"
        
        if data['fileName']:
            return data['fileName'], True, "Successfully updated the record"

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