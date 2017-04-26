#Author-Philipp Nox
#Description-


import adsk.core, adsk.fusion, traceback

defaultBoxName = 'Box'
defaultWall = 0.3
defaultH = 10
defaultW = 10
defaultD = 10
defaultKerf = 0.03
defaultShiftTotal = 1
defaultSheetAlpha = 0.3
defaultMill = 0.0

#wall = self.wall
#h = self.h
#w = self.w
#d = self.d
#kerf = self.kerf
#shiftTotal = self.shiftTotal
#shiftTop    = shiftTotal
#shiftBack   = shiftTotal
#shiftBottom = shiftTotal
#shiftFront  = shiftTotal
#sheetAlpha = self.sheetAlpha

#wall = 0.3
#h = 10
#w = 10
#d = 10
#kerf = 0.3
#shiftTotal = 1.5
#sheetAlpha = 0.3

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

newComp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

class BoltCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            bolt = Bolt()
            for input in inputs:
                if input.id == 'boltName':
                    bolt.boltName = input.value
                elif input.id == 'wall':
                    bolt.wall = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'height':
                    bolt.h = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'w':
                    bolt.w = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'd':
                    bolt.d = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'kerf':
                    bolt.kerf = unitsMgr.evaluateExpression(input.expression, "cm") 
                elif input.id == 'shiftTotal':
                    bolt.shiftTotal = unitsMgr.evaluateExpression(input.expression, "cm")
                    bolt.shiftTop = unitsMgr.evaluateExpression(input.expression, "cm")
                    bolt.shiftBack = unitsMgr.evaluateExpression(input.expression, "cm")                    
                    bolt.shiftFront = unitsMgr.evaluateExpression(input.expression, "cm")
                    bolt.shiftBottom = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'sheetAlpha':
                    bolt.sheetAlpha = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'mill':
                    bolt.sheetAlpha = unitsMgr.evaluateExpression(input.expression, "cm")

            bolt.buildBolt();
            args.isValidResult = True

        except:
            if ui:
                #ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                print('Failed:\n{}'.format(traceback.format_exc()))

class BoltCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BoltCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = BoltCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = BoltCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = BoltCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs
            inputs.addStringValueInput('boltName', 'Blot Name', defaultBoxName)

            initWall = adsk.core.ValueInput.createByReal(defaultWall)
            inputs.addValueInput('wall', 'Wall','cm',initWall)

            initH = adsk.core.ValueInput.createByReal(defaultH)
            inputs.addValueInput('height', 'Height', 'cm', initH)

            initW = adsk.core.ValueInput.createByReal(defaultW)
            inputs.addValueInput('w', 'Width', 'cm', initW)

            initD = adsk.core.ValueInput.createByReal(defaultD)
            inputs.addValueInput('d', 'Depth', 'cm', initD)

            #to do the thread length

            initKerf = adsk.core.ValueInput.createByReal(defaultKerf)
            inputs.addValueInput('kerf', 'Kerf Laser Cut', 'cm', initKerf)
            
            initMill = adsk.core.ValueInput.createByReal(defaultMill)
            inputs.addValueInput('mill', 'Mill diameter', 'cm', initMill)

            initShiftTotal = adsk.core.ValueInput.createByReal(defaultShiftTotal)
            inputs.addValueInput('shiftTotal', 'Shift', 'cm', initShiftTotal)

            initSheetAlpha = adsk.core.ValueInput.createByReal(defaultSheetAlpha)
            inputs.addValueInput('sheetAlpha', 'Tooth Proportions', '', initSheetAlpha)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Bolt:
    def __init__(self):
        self._boxName = defaultBoxName
        self._wall = defaultWall
        self._h = defaultH
        self._w = defaultW
        self._d = adsk.core.ValueInput.createByReal(defaultD)
        self._kerf = defaultKerf
        self._shiftTotal = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._sheetAlpha = adsk.core.ValueInput.createByReal(defaultSheetAlpha)
        self._shiftTop   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftBack   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftFront   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftBottom   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._mill       = defaultMill


    #properties
    @property
    def boltName(self):
        return self._boxName
    @boltName.setter
    def boltName(self, value):
        self._boxName = value

    @property
    def wall(self):
        return self._wall
    @wall.setter
    def wall(self, value):
        self._wall = value

    @property
    def h(self):
        return self._h
    @h.setter
    def h(self, value):
        self._h = value 

    @property
    def w(self):
        return self._w
    @w.setter
    def w(self, value):
        self._w = value 

    @property
    def d(self):
        return self._d
    @d.setter
    def d(self, value):
        self._d = value   

    @property
    def kerf(self):
        return self._kerf
    @kerf.setter
    def kerf(self, value):
        self._kerf = value  

    @property
    def shiftTotal(self):
        return self._shiftTotal
    @shiftTotal.setter
    def shiftTotal(self, value):
        self._shiftTotal = value
        
    @property
    def shiftTop(self):
        return self._shiftTop
    @shiftTop.setter
    def shiftTop(self, value):
        self._shiftTop = value
        
    @property
    def shiftBack(self):
        return self._shiftBack
    @shiftBack.setter
    def shiftBack(self, value):
        self._shiftBack = value
        
    @property
    def shiftBottom(self):
        return self._shiftBottom
    @shiftBottom.setter
    def shiftBottom(self, value):
        self._shiftBottom = value
        
    @property
    def shiftFront(self):
        return self._shiftFront
    @shiftFront.setter
    def shiftFront(self, value):
        self._shiftFront = value

    @property
    def sheetAlpha(self):
        return self._sheetAlpha
    @sheetAlpha.setter
    def sheetAlpha(self, value):
        self._sheetAlpha = value
        
    @property
    def mill(self):
        return self._mill
    @mill.setter
    def mill(self, value):
        self._mill = value

    def buildBolt(self):
        root = createNewComponent() 
        features = root.features
        extrudes = root.features.extrudeFeatures
        
        
        wall = self.wall
        h = self.h   #height
        w = self.w
        d = self.d
        kerf = self.kerf
        shiftTotal = self.shiftTotal
        shiftTop    = self.shiftTotal
        shiftBack   = self.shiftTotal
        shiftBottom = self.shiftTotal
        shiftFront  = self.shiftTotal
        
        sheetAlpha = self.sheetAlpha
        
        
        #wall = self.wall
        #h = self.h
        #w = self.w
        #d = self.d
        #kerf = self.kerf
        #shiftTotal = self.shiftTotal
        #shiftTop    = shiftTotal
        #shiftBack   = shiftTotal
        #shiftBottom = shiftTotal
        #shiftFront  = shiftTotal
        #sheetAlpha = self.sheetAlpha
        
        sheetZ = (w-2*wall)*sheetAlpha/2                              #2
        sheetXBase = (d-2*wall-shiftFront-shiftBack)*sheetAlpha/2     #1
        sheetXFront = (h-2*wall-shiftTop-shiftBottom)*sheetAlpha/2    #1
        
        conerFront  = d/2-wall-shiftFront #-(wall-kerf)
        conerBack   = d/2-wall-shiftBack        
        

        
        self.base(shiftBottom,root,conerFront,conerBack,sheetZ,sheetXBase)
        self.base(h-wall-shiftTop,root,conerFront,conerBack,sheetZ,sheetXBase)
    
        
        self.left((w-wall)/2,       root,sheetXBase,sheetXFront)
        self.left(-(w-wall)/2-wall, root,sheetXBase,sheetXFront)
    
        
        self.back(conerBack,        root,sheetXFront,sheetZ)
        self.back(-conerFront-wall, root,sheetXFront,sheetZ)
     
        
        print(root.bRepBodies.count)
        
        
        
        #Cut
        CombineCutFeats = features.combineFeatures          
        
        #Cut Rigth
        
        
        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(root.bRepBodies.item(0))
        ToolBodies.add(root.bRepBodies.item(1))
        ToolBodies.add(root.bRepBodies.item(4))
        ToolBodies.add(root.bRepBodies.item(5))
        
        CombineCutInput = root.features.combineFeatures.createInput(root.bRepBodies.item(2), ToolBodies )
        CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        CombineCutInput.isKeepToolBodies = True
        CombineCutFeats.add(CombineCutInput)
        
        #Cut Left
        CombineCutInput = root.features.combineFeatures.createInput(root.bRepBodies.item(3), ToolBodies )
        CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        CombineCutInput.isKeepToolBodies = True
        CombineCutFeats.add(CombineCutInput)
        
        #Cut Front
        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(root.bRepBodies.item(0))
        ToolBodies.add(root.bRepBodies.item(1))
        
        CombineCutInput = root.features.combineFeatures.createInput(root.bRepBodies.item(4), ToolBodies )
        CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        CombineCutInput.isKeepToolBodies = True
        CombineCutFeats.add(CombineCutInput)
        
        #Cut back
        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(root.bRepBodies.item(0))
        ToolBodies.add(root.bRepBodies.item(1))
        
        CombineCutInput = root.features.combineFeatures.createInput(root.bRepBodies.item(5), ToolBodies )
        CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        CombineCutInput.isKeepToolBodies = True
        CombineCutFeats.add(CombineCutInput)
        
        print(root.bRepBodies.count)
        
        print(root.sketches.count)    
   
    def rectForBox(self, sketch, offset, cX,cY,w,h):
        
        #make rectangle 
        sketch.sketchCurves.sketchLines.addCenterPointRectangle(adsk.core.Point3D.create(cX,cY,offset),adsk.core.Point3D.create(cX+w,cY+h,offset))  
        
        #make mill's holes
        mill = self.mill
        yMill = True 
        
        if(mill>0.0):
            r=mill/2.0
            if(yMill):
                if(w>h):
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w-r, cY+h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w-r, cY-h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w+r, cY-h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w+r, cY+h, offset), r)
                else:
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w, cY+h-r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w, cY-h+r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w, cY-h+r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w, cY+h-r, offset), r)
            else:
                if(w>h):
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w, cY+h-r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w, cY-h+r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w, cY-h+r, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w, cY+h-r, offset), r)
                else:
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w-r, cY+h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w-r, cY-h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w+r, cY-h, offset), r)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX-w+r, cY+h, offset), r)
    
    def left(self,offset,root,sheetXBase,sheetXFront):
        sketches = root.sketches
        planeYZ = root.yZConstructionPlane
        sketch = sketches.add(planeYZ)
        
        lines = sketch.sketchCurves.sketchLines
        
        lines.addTwoPointRectangle(adsk.core.Point3D.create(self.d/2,self.h,offset),adsk.core.Point3D.create(-self.d/2,0,offset))
        
        
        #axe = self.shiftBottom+self.wall/2   THIS is important
        self.rectForBox(sketch,offset, cX= 0,   cY= self.shiftBottom+self.wall/2,  w= sheetXBase, h= (self.wall-self.kerf)/2);
        
        
        #axe = self.h-self.shiftTop-self.wall/2   THIS is important                                                                 
        self.rectForBox(sketch,offset, cX= 0,   cY= self.h-self.shiftTop-self.wall/2,  w= sheetXBase, h= (self.wall-self.kerf)/2);
              
                                                  
        #axe = self.d/2-self.shiftBack-self.wall/2   THIS is important
        self.rectForBox(sketch,offset, cX= self.d/2-self.shiftBack-self.wall/2,   cY= self.h/2,  w= (self.wall-self.kerf)/2, h= sheetXFront);                                               
            
                                                                
        #axe = self.d/2-self.shiftBack-self.wall/2   THIS is important
        self.rectForBox(sketch,offset, cX= -self.d/2+self.shiftFront+self.wall/2,   cY= self.h/2,  w= (self.wall-self.kerf)/2, h= sheetXFront);                                                         
                                                                
        
        extrudes = root.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
            
        extrudeInput = extrudes.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        return extrudes.add(extrudeInput)
        
    def back(self,offset,root,sheetXFront,sheetZ):
        
        sketches = root.sketches
        planeXY = root.xYConstructionPlane
        sketch = sketches.add(planeXY)
        
        lines = sketch.sketchCurves.sketchLines   
        
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h,offset),adsk.core.Point3D.create((self.w-self.wall)/2,0,offset))
        # sheetXFront for left
        lines.addCenterPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h/2,offset),adsk.core.Point3D.create(-(self.w-self.wall)/2-self.wall,self.h/2+sheetXFront,offset))
        # sheetXFront for Rigth
        lines.addCenterPointRectangle(adsk.core.Point3D.create((self.w-self.wall)/2,self.h/2,offset),adsk.core.Point3D.create((self.w-self.wall)/2+self.wall,self.h/2+sheetXFront,offset))
        
        
        #axe = self.shiftBottom+self.wall/2   THIS is important
        self.rectForBox(sketch,offset, cX= 0,   cY= self.shiftBottom+self.wall/2,  w= sheetZ, h= (self.wall-self.kerf)/2);
        
        
        #axe = self.h-self.shiftTop-self.wall/2   THIS is important                                                              
        self.rectForBox(sketch,offset, cX= 0,   cY= self.h-self.shiftTop-self.wall/2,  w= sheetZ, h= (self.wall-self.kerf)/2);
           
                                                     
        extrudes = root.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
            
        extrudeInput = extrudes.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        return extrudes.add(extrudeInput)
        
        
    def base(self,offset,root,conerFront,conerBack,sheetZ,sheetXBase):
        
        sketches = root.sketches
        planeXZ = root.xZConstructionPlane
        sketch = sketches.add(planeXZ)
        
        lines = sketch.sketchCurves.sketchLines
        
          
        #   half of base from origin to front
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset),adsk.core.Point3D.create((self.w-self.wall)/2,conerFront,offset))
        #   half of base from origin to back        
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset),adsk.core.Point3D.create((self.w-self.wall)/2,-conerBack,offset))
        # sheetZ for front
        lines.addCenterPointRectangle(adsk.core.Point3D.create(0,conerFront,offset),adsk.core.Point3D.create(sheetZ,conerFront-self.wall,offset))
        # sheetZ for back
        lines.addCenterPointRectangle(adsk.core.Point3D.create(0,-conerBack,offset),adsk.core.Point3D.create(sheetZ,-conerBack-self.wall,offset))
        # sheetXBase for left
        lines.addCenterPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset),adsk.core.Point3D.create((-(self.w-self.wall)/2)-self.wall,sheetXBase,offset))   
        # sheetXBase for Rigth
        lines.addCenterPointRectangle(adsk.core.Point3D.create((self.w-self.wall)/2,0,offset),adsk.core.Point3D.create(((self.w-self.wall)/2)+self.wall,sheetXBase,offset))   
        
        lines.addCenterPointRectangle(adsk.core.Point3D.create(0,0,offset),adsk.core.Point3D.create(2,2,offset))  
            
        
        extrudes = root.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
            
        extrudeInput = extrudes.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        return extrudes.add(extrudeInput)        
    

        
def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('Bolt')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Bolt',
                    'Create Bolt',
                    'Create a bolt.',
                    './resources') # relative resource file path is specified

        onCommandCreated = BoltCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
