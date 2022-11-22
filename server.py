# Actividad Integradora 1
# Mayra Fernanda Camacho Rodríguez	A01378998
# Víctor Martínez Román			A01746361
# Melissa Aurora Fadanelli Ordaz		A01749483
# Juan Pablo Castañeda Serrano		A01752030
from flask import Flask, request, jsonify
from Robot import *

robotModel = None
currentStep = 0

app = Flask("Cleaning robots")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, robotModel, width, height

    if request.method == 'POST':
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        box = int(request.form.get('box'))
        currentStep = 0

        robotModel = RobotModel(width, height, box)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getRobots', methods=['GET'])
def getRobots():
    global robotModel

    if request.method == 'GET':
        robotPositions = []
        for (a, x, z) in robotModel.grid.coord_iter():
            if len(a) > 0:
                for i in a:
                    dic = {}
                    if isinstance(i, RobotAgent):
                        dic["id"] = str(i.unique_id)
                        dic["x"] = x
                        dic["z"] = z
                        robotPositions.append(dic)

        return jsonify({'positions':robotPositions})

@app.route('/getBoxes', methods=['GET'])
def getBoxes():
    global robotModel

    if request.method == 'GET':
        boxPositions = []
        for (a, x, z) in robotModel.grid.coord_iter():
            if len(a) > 0:
                for i in a:
                    dic = {}
                    if isinstance(i, BoxAgent):
                        dic["id"] = str(i.unique_id)
                        dic["x"] = x
                        dic["z"] = z
                        boxPositions.append(dic)
        
        return jsonify({'positions':boxPositions})

@app.route('/getShelves', methods=['GET'])
def getShelves():
    global robotModel

    if request.method == 'GET':
        shelvesPositions = []
        for (a, x, z) in robotModel.grid.coord_iter():
            if len(a) > 0:
                for i in a:
                    dic = {}
                    if isinstance(i, Anaquel):
                        dic["id"] = str(i.unique_id)
                        dic["x"] = x
                        dic["z"] = z
                        shelvesPositions.append(dic)

    return jsonify({'positions':shelvesPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, robotModel
    if request.method == 'GET':
        robotModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="0.0.0.0", port=8585, debug=True)
