from pydantic import ValidationError
from datetime import datetime
from bson import ObjectId
from app import user_database,user_simulation_database, simulation_database, name_storage_database
from ..models.user import UserSchema
from ..models.userSimulation import UserSimulationSchema
from ..models.simulation import SimulationSchema
from ..models.nameStorage import NameStorageSchema
from app import gridFileStorage

def deleteSimulationById(data):
    try:
        delete_sim = False
        delete_us_sim = False
        # Delete the student by ID
        simulation = list(simulation_database.find({"_id": ObjectId(data["simulationId"])}))
        file_id = simulation[0]["fileId"]
        gridFileStorage.delete(ObjectId(file_id))
        delete_simulation = simulation_database.delete_one({"_id": ObjectId(data["simulationId"])})

        if delete_simulation.deleted_count > 0:
            delete_sim = True

        user_simulation = list(user_simulation_database.find({"simulationId": data["simulationId"]}))

        if(user_simulation):
            delete_user_simulation = user_simulation_database.delete_one({"simulationId": data["simulationId"]})

            if delete_user_simulation.deleted_count > 0:
                return "", True, "Successfully deleted simulaion and its students"
            if delete_sim:
                return "", True, "Successfully deleted simulaion but not its students"
            else:
                return "", False, "Something went bad"

        
        if delete_sim:
            return "", True, "Successfully deleted simulaion"
        else:
            return "", False, "Something went bad"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def deleteStudentById(data):
    try:
        delete_us = False
        delete_us_sim = False
    
        delete_user = user_database.delete_one({"_id": ObjectId(data["userId"])})
        if delete_user.deleted_count > 0:
            delete_us = True

        user_simulation = list(user_simulation_database.find({"userId": data["userId"]}))
        if(user_simulation):
            simulation_id = user_simulation[0]["simulationId"]
            file_id = user_simulation[0]["fileId"]

            gridFileStorage.delete(ObjectId(file_id))
            delete_user_simulation = user_simulation_database.delete_one({"userId": data["userId"]})
            if delete_user_simulation.deleted_count > 0:
                delete_us_sim = True

            simulation = list(simulation_database.find({"_id": ObjectId(simulation_id)}))[0]
            filter_query_simulation = {
                "_id": ObjectId(simulation_id)
            }
            update_query_simulation = {
                "$set": {"participants" : simulation["participants"] - 1}
            }
            result1 = simulation_database.update_one(filter_query_simulation, update_query_simulation)

            if delete_us_sim:
                return {}, True, "Student record deleted successfully and its internal simulations"
            else:
                return "", True, "Successfully deleted student"
        if delete_us:
            return "", True, "Successfully deleted student"
        else:
            return "", False, "Something went bad"


    except ValidationError as e:
        return str(e), False, "Something went bad"

def getSimulationById(data):
    try:
        simulation = list(simulation_database.find({"_id": ObjectId(data["simulationId"])}))[0]
        if simulation:
            simulation['_id'] = str(simulation['_id']) 

            return simulation, True, "Data fetched successfully"

        return [], False, "No student is registred under this name"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def getAdminById():
    try:
        users = list(user_database.find({"role": "Admin"}))
        if users:
            for user in users:
                user['_id'] = str(user['_id']) 

            return users, True, "Data fetched successfully"

        return [], False, "No student is registred under this name"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def updateAdminById(data):
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

def updateStudentById(data):
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


def getStudentById(data):
    try:
        users = list(user_database.find({"role": "Student", "_id": ObjectId(data["studentId"])}, {"password": 0}))
        if users:
            for user in users:
                user['_id'] = str(user['_id']) 

            return users, True, "Data fetched successfully"

        return [], False, "No student is registred under this name"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def updateSimulationController(data):
    try:

        simulation = SimulationSchema(**data)

        filter_query_simulation = {
            "_id": ObjectId(simulation.id)
        }
        # Define the update query
        update_query_simulation = {
            "$set": simulation.dict(exclude_unset=True)
        }
        
        # Update the document
        result1 = simulation_database.update_one(filter_query_simulation, update_query_simulation)

        if result1.matched_count == 0:
            if result1.modified_count > 0:
                print("Document updated successfully.")
            else:
                print("Document matched but no changes were made (maybe the data was already the same).")
            return str(e), False, "Something went bad"
        # # Validate incoming data using Pydantic schema
        # simulationData = SimulationSchema(**data)
        # result = simulation_database.insert_one(simulationData.dict())

        # if result:
        return "", True, "Data inserted successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def createSimulationController(data):
    try:

        # Validate incoming data using Pydantic schema
        simulationData = SimulationSchema(**data)
        dictSim = simulationData.dict() 
        nameStr = list(name_storage_database.find({}))
        if not nameStr:
            nameStorageData = NameStorageSchema(**{
                "category": [dictSim["category"]],
                "simulationName":[dictSim["simulationName"]],
                "organizationName":[dictSim["organizationName"]],
            })
            name_storage_database.insert_one(nameStorageData.dict())
        else:
            # Check if the value is not already in the list before appending
            if dictSim["category"] not in nameStr[0]["category"]:
                nameStr[0]["category"].append(dictSim["category"])

            if dictSim["simulationName"] not in nameStr[0]["simulationName"]:
                nameStr[0]["simulationName"].append(dictSim["simulationName"])

            if dictSim["organizationName"] not in nameStr[0]["organizationName"]:
                nameStr[0]["organizationName"].append(dictSim["organizationName"])

            nameStr[0]["_id"] = str(nameStr[0]["_id"])
            nameStorageData = NameStorageSchema(**nameStr[0])
        
            name_storage_database.update_one({"_id": ObjectId(nameStr[0]["_id"])}, { "$set": nameStorageData.dict() })
        
        result = simulation_database.insert_one(dictSim)

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
            scores= []
            examsTaken = 0
            maxScore = 0
            userSimulations = list(user_simulation_database.find({"userId": user["id"]}))
            if(len(userSimulations)):
                for userSimulation in userSimulations:
                    if(userSimulation["grade"]):
                        examsTaken += 1
                        scores.append(float(userSimulation["grade"]))
                        user["examTaken"] = examsTaken
                        user["avgScore"] =  round(sum(scores) / examsTaken, 2)
                        if(float(userSimulation["grade"]) > maxScore):
                            maxScore = float(userSimulation["grade"])
                user["maxScore"] = maxScore
            else:
                user["avgScore"] = 0
                user["examTaken"] = 0
                user["maxScore"] = 0

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

def getSuggestionListsController():
    try:

        suggList = list(name_storage_database.find({},{"id":0}))

        if suggList:
            suggList[0]["_id"] = str(suggList[0]["_id"])
            return suggList[0], True, "Data fetched successfully"
        else:
            return [], True, "Data fetched successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def getTheSimulationDetails(data): 
    try:
   
        simulation =list(simulation_database.find({"_id": ObjectId(data['simulationId'])},{"_id": 0}))
        if not simulation:
            return "", False, "No simulation found"
            
        userSimulations = list(user_simulation_database.find({"simulationId": data['simulationId']},{"_id": 0}))
        if userSimulations:
            userSimulations = [UserSimulationSchema(**userSimulation).dict() for userSimulation in userSimulations]
        
            # Step 1: Convert grades to numeric and sort the data
            userSimulations = sorted(userSimulations, key=lambda x: float(x['grade']) if x['grade'] is not None else 0.0, reverse=True)

            # Step 2: Assign ranks
            for i, item in enumerate(userSimulations, start=1):
                item['rank'] = i
                
            for userSimulation in userSimulations:
                userSimulation["userId"] = list(user_database.find({"_id": ObjectId(userSimulation["userId"])},{"_id": 0}))[0]

        result = {
            "simulationDetails": simulation[0],
            "result": userSimulations
        }
        return result, True, "Successfully fetched"

    except ValidationError as e:
        return str(e), False, "Something went bad"