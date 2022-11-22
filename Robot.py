# Actividad Integradora 1
# Mayra Fernanda Camacho Rodríguez	A01378998
# Víctor Martínez Román			A01746361
# Melissa Aurora Fadanelli Ordaz		A01749483
# Juan Pablo Castañeda Serrano		A01752030
from mesa import Agent, Model
from mesa.space import MultiGrid
import random

from mesa.time import RandomActivation

#Crear un id para cada caja, mientras que el robot tenga asignado ese id de la caja tiene que llevarla hacia los 
#espacios designados. Luego le cambia el estado de recogido a 2 para que ya nadie la recoja

#self.recogido. 0: No recojido. 1: En traslado. 2: Trasladado. 3:Robot. 4:Anaquel

#Que el robot primero sienta si tiene caja o no. Si tiene caja, se mueve con la caja. Si no tiene caja, busca caja

class BoxAgent(Agent):
    def __init__(self, unique_id, model,pos):

        super().__init__(unique_id, model)
        self.AgentState = 0
        self.next_state = None
        self.pos = pos
        self.id = random.randrange(0, 250, 1)
        
    def seguir(self, new_position):
        self.model.grid.move_agent(self, new_position)
        
        
class Anaquel(Agent):
    def __init__(self, unique_id, model,pos):

        super().__init__(unique_id, model)
        self.AgentState = 4
        self.pos = pos

        
class RobotAgent(Agent):
        def __init__(self, unique_id, model, pos):

            super().__init__(unique_id, model)
            self.next_state = None
            self.pos = pos
            self.AgentState = 3
            self.idcaja = 0
            
        def sense(self):
            if self.idcaja == 0:
                self.WalkWithNoBox()
            if self.idcaja != 0:
                self.WalkWithBox()
            
        def WalkWithNoBox(self):
            myBox = self
            NoRecogidos = []
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True)         
            neighbors = self.model.grid.iter_neighbors(self.pos,moore = True, include_center=True) 
            for neighbor in neighbors:
                if neighbor.AgentState == 0 and neighbor.pos == self.pos: #Si no esta recogido y esta encima
                    myBox = neighbor
                if neighbor.AgentState == 0: #Si no esta recogido y esta a lado
                    NoRecogidos.append(neighbor.pos)
            if len(NoRecogidos) == 0 and myBox == self:
                randompos = self.random.choice(possible_steps)
                self.move(randompos)
            elif len(NoRecogidos) != 0 and myBox == self:
                randompos = self.random.choice(NoRecogidos)
                self.move(randompos)
            else:
                self.acomodar(myBox)
                
        def WalkWithBox(self):
        # Primero tiene que detectar su caja, hacemos una lista de los lugares donde puede dejarlo o moverlo, segun sea necesario
            MyBox = self
            DropZone = []
            BelowDrop = []
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True)
            neighbors = self.model.grid.iter_neighbors(self.pos,moore = True, include_center=True)
            for neighbor in neighbors: 
                if neighbor.AgentState == 1 and neighbor.pos == self.pos:
                    MyBox = neighbor
                if neighbor.AgentState == 4:
                    DropZone.append(neighbor)
                if neighbor.AgentState == 4 and neighbor.pos == self.pos:   
                    BelowDrop.append(neighbor)

            if len(DropZone) == 0:
                randompos = self.random.choice(possible_steps)
                self.moveBox(MyBox,randompos)
                
            elif len(BelowDrop) == 0:
                randompos = self.random.choice(DropZone)
                self.moveBox(MyBox, neighbor.pos)
                
            else:    
                self.dejar(MyBox)    
    
        def move(self, new_position):
            self.model.grid.move_agent(self, new_position)  
            
        def moveBox(self, agente, new_position):
            self.model.grid.move_agent(self, new_position)
            agente.seguir(new_position)

        def acomodar(self, agent):
            agent.AgentState = 1
            self.idcaja = agent.id
                
        def dejar(self,agent):
            agent.AgentState = 2
            self.idcaja = 0

        def step(self):
            self.sense()


class RobotModel(Model):
    def __init__(self, width, height, box):
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True # Para la visualizacion usando navegador
        count = 0
        countF = 0
        X = []
        Y = []
        
        for (content, x, y) in self.grid.coord_iter():
            X.append(x)
            Y.append(y)

        for i in range(width):
            b = Anaquel(i, self, (i, 0))
            self.grid.place_agent(b, (i, 0))     
            self.schedule.add(b)

        s_row = width * 2
        for i in range(width, s_row):
            b1 = Anaquel(i, self, (i - width, height - 1))
            self.grid.place_agent(b1, (i - width, height - 1))
            self.schedule.add(b1)
   
        for i in range(5):
            r = RobotAgent(i + 100, self, (i + 2, i + 2))
            self.grid.place_agent(r, (i + 2, i + 2))
            self.schedule.add(r)

        for i in range(box):
            x = random.choice(X)
            y = random.choice(Y)
            c = BoxAgent(i + 200, self, (x, y))
            self.grid.place_agent(c, (x, y))
            self.schedule.add(c)

    def step(self):
        self.schedule.step()        
