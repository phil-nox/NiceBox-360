#Author-Philipp Nox
#Description-


import adsk.core, adsk.fusion, traceback
import os, tempfile, platform

defaultBoxName = 'Box'
defaultWall = 0.3
defaultH = 10
defaultW = 10
defaultD = 10
defaultKerf = 0.03
defaultShiftTotal = 1
defaultSheetAlpha = 0.3
defaultMill = 0.2
mill = 0.2

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

newComp = None

product = app.activeProduct
design = adsk.fusion.Design.cast(product)
 

def createNewComponent(rootComp):
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

class BoxCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            box = BOX()
            for input in inputs:
                if input.id == 'boxName':
                    box.boxName = input.value
                elif input.id == 'wall':
                    box.wall = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'height':
                    box.h = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'w':
                    box.w = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'd':
                    box.d = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'kerf':
                    box.kerf = unitsMgr.evaluateExpression(input.expression, "cm") 
                elif input.id == 'shiftTotal':
                    box.shiftTotal = unitsMgr.evaluateExpression(input.expression, "cm")
                    box.shiftTop = unitsMgr.evaluateExpression(input.expression, "cm")
                    box.shiftBack = unitsMgr.evaluateExpression(input.expression, "cm")                    
                    box.shiftFront = unitsMgr.evaluateExpression(input.expression, "cm")
                    box.shiftBottom = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'sheetAlpha':
                    box.sheetAlpha = unitsMgr.evaluateExpression(input.expression, "cm")

            box.buildBox();
            args.isValidResult = True

        except:
            if ui:
                #ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                print('Failed:\n{}'.format(traceback.format_exc()))

class BoxCommandDestroyHandler(adsk.core.CommandEventHandler):
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

class BoxCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = BoxCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = BoxCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = BoxCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs
            inputs.addStringValueInput('boxName', 'Box Name', defaultBoxName)
            
            #print(design.userParameters.itemByName('defaultWall'))
            #print('test') 
            
            initWall = adsk.core.ValueInput.createByReal(defaultWall)
            #initWall = adsk.core.ValueInput.createByReal(design.userParameters.itemByName('defaultWall').value)
            inputs.addValueInput('wall', 'Wall','cm',initWall)
            
            initH = adsk.core.ValueInput.createByReal(defaultH)      
            #initH = adsk.core.ValueInput.createByReal(design.userParameters.itemByName(defaultH)) 
            inputs.addValueInput('height', 'Height', 'cm', initH)

            initW = adsk.core.ValueInput.createByReal(defaultW)
            inputs.addValueInput('w', 'Width', 'cm', initW)

            initD = adsk.core.ValueInput.createByReal(defaultD)
            inputs.addValueInput('d', 'Depth', 'cm', initD)

            #to do the thread length

            initKerf = adsk.core.ValueInput.createByReal(defaultKerf)
            inputs.addValueInput('kerf', 'Kerf Laser Cut', 'cm', initKerf)

            initShiftTotal = adsk.core.ValueInput.createByReal(defaultShiftTotal)
            inputs.addValueInput('shiftTotal', 'Shift', 'cm', initShiftTotal)

            initSheetAlpha = adsk.core.ValueInput.createByReal(defaultSheetAlpha)
            inputs.addValueInput('sheetAlpha', 'Tooth Proportions', '', initSheetAlpha)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BOX:
    def __init__(self):
        self._boxName = defaultBoxName
        self._wall = defaultWall
        self._h = defaultH
        #self._h = design.rootComponent.modelParameters.itemByName('defaultH')
        self._w = defaultW
        self._d = adsk.core.ValueInput.createByReal(defaultD)
        self._kerf = defaultKerf
        self._shiftTotal = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._sheetAlpha = adsk.core.ValueInput.createByReal(defaultSheetAlpha)
        self._shiftTop   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftBack   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftFront   = adsk.core.ValueInput.createByReal(defaultShiftTotal)
        self._shiftBottom   = adsk.core.ValueInput.createByReal(defaultShiftTotal)


    #properties
    @property
    def boxName(self):
        return self._boxName
    @boxName.setter
    def boxName(self, value):
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

    def buildBox(self):
        rootComp = design.rootComponent
        root = createNewComponent(rootComp)
        root.name = defaultBoxName 
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
        
        sheetZ = (w-2*wall)*sheetAlpha/2                              #2
        sheetXBase = (d-2*wall-shiftFront-shiftBack)*sheetAlpha/2     #1
        sheetXFront = (h-2*wall-shiftTop-shiftBottom)*sheetAlpha/2    #1
        
        conerFront  = d/2-wall-shiftFront #-(wall-kerf)
        conerBack   = d/2-wall-shiftBack        
        
        self.bot_top("Bottom",shiftBottom,root,conerFront,conerBack,sheetZ,sheetXBase)
        self.bot_top("Top",h-wall-shiftTop,root,conerFront,conerBack,sheetZ,sheetXBase)
            
        self.left_right("Right",(w-wall)/2,       root,sheetXBase,sheetXFront)
        self.left_right("Left",-(w-wall)/2-wall, root,sheetXBase,sheetXFront)
        
        self.front_back("Front",conerBack,        root,sheetXFront,sheetZ)
        self.front_back("Back",-conerFront-wall, root,sheetXFront,sheetZ)
        
        componentNameMap = {}
        componentNameMap[root.name] = root

        for occ in root.allOccurrences:
            subComp = occ.component
            componentNameMap[subComp.name] = subComp
        
        allbodies = adsk.core.ObjectCollection.create()
        for comp in list(componentNameMap.values()):
            for body in comp.bRepBodies:
                allbodies.add(body)
        
#        print(root.bRepBodies.count)     
#        print(root.sketches.count)    
    def rectForBox(self, sketch, offset, cX,cY,w,h):
        #make rectangle 
        rect = sketch.sketchCurves.sketchLines.addCenterPointRectangle(adsk.core.Point3D.create(cX,cY,offset),adsk.core.Point3D.create(cX+w,cY+h,offset))  
        
        #make mill's holes
        #mill = self.mill
        yMill = True 
        toTrim = True
        
        if(mill>0.0):
            r=mill/2.0
            
            if(yMill):
                if(w>h):
                    pnt0 = adsk.core.Point3D.create(cX+w-r, cY+h, offset)
                    pnt1 = adsk.core.Point3D.create(cX+w-r, cY-h, offset)
                    pnt2 = adsk.core.Point3D.create(cX-w+r, cY-h, offset)
                    pnt3 = adsk.core.Point3D.create(cX-w+r, cY+h, offset)
                else:
                    pnt0 = adsk.core.Point3D.create(cX+w, cY+h-r, offset)
                    pnt1 = adsk.core.Point3D.create(cX+w, cY-h+r, offset)
                    pnt2 = adsk.core.Point3D.create(cX-w, cY-h+r, offset)
                    pnt3 = adsk.core.Point3D.create(cX-w, cY+h-r, offset)
            else:
                if(w>h):
                    pnt0 = adsk.core.Point3D.create(cX+w, cY+h-r, offset)
                    pnt1 = adsk.core.Point3D.create(cX+w, cY-h+r, offset)
                    pnt2 = adsk.core.Point3D.create(cX-w, cY-h+r, offset)
                    pnt3 = adsk.core.Point3D.create(cX-w, cY+h-r, offset)
                else:
                    pnt0 = adsk.core.Point3D.create(cX+w-r, cY+h, offset)
                    pnt1 = adsk.core.Point3D.create(cX+w-r, cY-h, offset)
                    pnt2 = adsk.core.Point3D.create(cX-w+r, cY-h, offset)
                    pnt3 = adsk.core.Point3D.create(cX-w+r, cY+h, offset)
                    
            cir0 = sketch.sketchCurves.sketchCircles.addByCenterRadius(pnt0, r)
            cir1 = sketch.sketchCurves.sketchCircles.addByCenterRadius(pnt1, r)
            cir2 = sketch.sketchCurves.sketchCircles.addByCenterRadius(pnt2, r)
            cir3 = sketch.sketchCurves.sketchCircles.addByCenterRadius(pnt3, r)
            
            if(toTrim):
                #sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cX+w-r, cY+h-r, offset),0.02)
                #rect.item(0).trim(adsk.core.Point3D.create(cX+w-r, cY+h-r, offset),False)
                #sketch.sketchCurves.sketchCircles.item(0).trim(adsk.core.Point3D.create(cX+w-r, cY+h-r, offset),False)
                
                if(w>h):                
                    rect.item(0).trim(pnt0)
                    rect.item(0).trim(pnt3)
                    rect.item(2).trim(pnt1)
                    rect.item(2).trim(pnt2)
                else:
                    rect.item(1).trim(pnt0)
                    rect.item(1).trim(pnt1)
                    rect.item(3).trim(pnt3)
                    rect.item(3).trim(pnt2)
            
                cir0.trim(adsk.core.Point3D.create(cX,cY,offset))
                cir1.trim(adsk.core.Point3D.create(cX,cY,offset))
                cir2.trim(adsk.core.Point3D.create(cX,cY,offset))
                cir3.trim(adsk.core.Point3D.create(cX,cY,offset))
                
    
    def left_right(self,_name,offset,root,sheetXBase,sheetXFront):
        #Component rename
        side = createNewComponent(root) 
        side.name = _name
        
        #Sketch rename
        sketches = side.sketches
        planeYZ = side.yZConstructionPlane
        sketch = sketches.add(planeYZ)
        sketch.name = _name
        
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
                      
        
        extrudes = side.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
            
        #print(profs.count)
        extrudeInput = extrudes.createInput(profs[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        
        #Extrude rename
        sideExtrude = extrudes.add(extrudeInput)
        sideExtrude.name = _name
        
        #Body rename
        sideBody = side.bRepBodies.item(side.bRepBodies.count-1)
        sideBody.name = _name  
    
        saveToDXF(sketch, _name)    
    
        return sideExtrude
        
    def front_back(self,_name,offset,root,sheetXFront,sheetZ):
        #Component rename
        toTrim = True        
        
        side = createNewComponent(root) 
        side.name = _name        
             
        #Sketch rename
        sketches = side.sketches
        planeXY = side.xYConstructionPlane
        sketch = sketches.add(planeXY)
        sketch.name = _name
        
        lines = sketch.sketchCurves.sketchLines   
        
        # Main rectangle
        mainRectangle = lines.addTwoPointRectangle(adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h,offset),adsk.core.Point3D.create((self.w-self.wall)/2,0,offset))
        # sheetXFront for left
        point1 = adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h/2,offset)
        point2 = adsk.core.Point3D.create(-(self.w-self.wall)/2-self.wall,self.h/2+sheetXFront,offset)
        point3 = adsk.core.Point3D.create(-(self.w-self.wall)/2+self.wall,self.h/2+sheetXFront,offset)
        point4 = adsk.core.Point3D.create(-(self.w-self.wall)/2+self.wall,self.h/2-sheetXFront,offset)
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(1).deleteMe()
        rectangleToCut.item(0).trim(point4, False) #Top
        rectangleToCut.item(2).trim(point3, False) #Bottom
        
        leftLine = mainRectangle.item(3).trim(point1, False) #Left
        
        # sheetXFront for Right
        point1 = adsk.core.Point3D.create((self.w-self.wall)/2,self.h/2,offset)
        point2 = adsk.core.Point3D.create((self.w-self.wall)/2+self.wall,self.h/2+sheetXFront,offset)
        point3 = adsk.core.Point3D.create((self.w-self.wall)/2-self.wall,self.h/2+sheetXFront,offset)
        point4 = adsk.core.Point3D.create((self.w-self.wall)/2-self.wall,self.h/2-sheetXFront,offset)
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(1).deleteMe()
        rectangleToCut.item(0).trim(point3, False) #Top
        rectangleToCut.item(2).trim(point4, False) #Bottom
        
        rightLine = mainRectangle.item(1).trim(point1, False) #Right
                
        #   hole for the top
        #axe = self.shiftBottom+self.wall/2   THIS is important
        self.rectForBox(sketch,offset, cX= 0,   cY= self.shiftBottom+self.wall/2,  w= sheetZ, h= (self.wall-self.kerf)/2);
        
        
        #axe = self.h-self.shiftTop-self.wall/2   THIS is important                                                              
        self.rectForBox(sketch,offset, cX= 0,   cY= self.h-self.shiftTop-self.wall/2,  w= sheetZ, h= (self.wall-self.kerf)/2);
        
        if(mill > 0.0):
            r=mill/2.0
            
            tmpCenter = adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h/2+sheetXFront+r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-(self.w-self.wall)/2-r,self.h/2+sheetXFront+r,offset))
                leftLine.item(1).trim(tmpCenter)
            
            tmpCenter = adsk.core.Point3D.create(-(self.w-self.wall)/2,self.h/2-sheetXFront-r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-(self.w-self.wall)/2-r,self.h/2-sheetXFront-r,offset))
                leftLine.item(0).trim(tmpCenter)
            
            tmpCenter = adsk.core.Point3D.create((self.w-self.wall)/2,self.h/2+sheetXFront+r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create((self.w-self.wall)/2+r,self.h/2+sheetXFront+r,offset))
                rightLine.item(0).trim(tmpCenter)
            
            tmpCenter = adsk.core.Point3D.create((self.w-self.wall)/2,self.h/2-sheetXFront-r,offset)      
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create((self.w-self.wall)/2+r,self.h/2-sheetXFront-r,offset) )
                rightLine.item(1).trim(tmpCenter)
                                                                
        extrudes = side.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
        print(profs.count)
   
        extrudeInput = extrudes.createInput(profs[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        
        #Extrude rename
        sideExtrude = extrudes.add(extrudeInput)
        sideExtrude.name = _name        
        
        #Body rename
        sideBody = side.bRepBodies.item(side.bRepBodies.count-1)
        sideBody.name = _name 
        
        saveToDXF(sketch, _name)
        
        return sideExtrude
        
    def bot_top(self,_name,offset,root,conerFront,conerBack,sheetZ,sheetXBase):
        #Component rename
        toTrim = True
        
        side = createNewComponent(root) 
        side.name = _name  
        
        #Sketch rename
        sketches = side.sketches
        planeXZ = side.xZConstructionPlane
        sketch = sketches.add(planeXZ)
        sketch.name = _name         
        
        lines = sketch.sketchCurves.sketchLines
        
        #   half of base from origin to back
        baseBackPoint0 = adsk.core.Point3D.create(0,conerBack,offset) #MidPoint
        baseBackPoint1 = adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset)
        baseBackPoint2 = adsk.core.Point3D.create((self.w-self.wall)/2,conerBack,offset)
        baseBackToCut = lines.addTwoPointRectangle(baseBackPoint1,baseBackPoint2)
        baseBackToCut.item(0).deleteMe()
        #   half of base from origin to front
        baseFrontPoint0 = adsk.core.Point3D.create(0,-conerFront,offset) #MidPoint
        baseFrontPoint1 = adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset)
        baseFrontPoint2 = adsk.core.Point3D.create((self.w-self.wall)/2,-conerFront,offset)
        baseFrontToCut = lines.addTwoPointRectangle(baseFrontPoint1,baseFrontPoint2)
        baseFrontToCut.item(0).deleteMe()
        # sheetZ for back
        point1 = adsk.core.Point3D.create(0,conerBack,offset)
        point2 = adsk.core.Point3D.create(sheetZ,conerBack-self.wall,offset)  #ToRight
        point3 = adsk.core.Point3D.create(-sheetZ,conerBack-self.wall,offset) #ToLeft
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(0).deleteMe() #ToFront
        rectangleToCut.item(1).trim(point3, False) #Correct ToLeft
        rectangleToCut.item(3).trim(point2, False) #Correct ToRight
        # sheetZ for front
        point1 = adsk.core.Point3D.create(0,-conerBack,offset) #MidPoint
        point2 = adsk.core.Point3D.create(sheetZ,-conerBack-self.wall,offset)
        point3 = adsk.core.Point3D.create(sheetZ,-conerBack+self.wall,offset) #ToRight
        point4 = adsk.core.Point3D.create(-sheetZ,-conerBack+self.wall,offset) #ToLeft
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(2).deleteMe()
        rectangleToCut.item(1).trim(point3, False) #Correct
        rectangleToCut.item(3).trim(point4, False) #Correct
        # sheetXBase for left
        point1 = adsk.core.Point3D.create(-(self.w-self.wall)/2,0,offset)
        point2 = adsk.core.Point3D.create((-(self.w-self.wall)/2)-self.wall,sheetXBase,offset)
        point3 = adsk.core.Point3D.create(0,-(self.w-self.wall)/2,offset)
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(1).deleteMe()
        rectangleToCut.item(0).trim(point1, False)
        rectangleToCut.item(2).trim(point3, False)
        # sheetXBase for Right
        point1 = adsk.core.Point3D.create((self.w-self.wall)/2,0,offset)
        point2 = adsk.core.Point3D.create(((self.w-self.wall)/2)+self.wall,sheetXBase,offset)
        point3 = adsk.core.Point3D.create(0,(self.w-self.wall)/2,offset)
        rectangleToCut = lines.addCenterPointRectangle(point1,point2)
        rectangleToCut.item(1).deleteMe() 
        rectangleToCut.item(0).trim(point1, False) #Correct
        rectangleToCut.item(2).trim(point3, False)
        
        #  Trim rest of lines
        rightBack = baseBackToCut.item(1).trim(baseBackPoint1) #Correct RIGHT 
        leftBack = baseBackToCut.item(3).trim(baseBackPoint1) #Correct LEFT
        
        rightFront = baseFrontToCut.item(1).trim(baseFrontPoint1) #Correct RIGHT
        leftFront = baseFrontToCut.item(3).trim(baseFrontPoint1) #Correct LEFT
        
        backLine = baseBackToCut.item(2).trim(baseBackPoint0) #Correct BACK
        frontLine = baseFrontToCut.item(2).trim(baseFrontPoint0) #Correct FRONT 
        
        #sketch.sketchPoints.add(baseBackPoint0) #Draw a test dot
        if(mill > 0.0):
            r=mill/2.0
            tmpCenter = adsk.core.Point3D.create(sheetZ+r,conerFront,offset)            
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(sheetZ+r,conerFront+r,offset))
                backLine.item(0).trim(tmpCenter)
                  
            tmpCenter = adsk.core.Point3D.create(-sheetZ-r,conerFront,offset) 
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-sheetZ-r,conerFront+r,offset))
                backLine.item(1).trim(tmpCenter)
            
            tmpCenter = adsk.core.Point3D.create(sheetZ+r,-conerBack,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(sheetZ+r,-conerBack-r,offset))
                frontLine.item(0).trim(tmpCenter)
                
            tmpCenter = adsk.core.Point3D.create(-sheetZ-r,-conerBack,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-sheetZ-r,-conerBack-r,offset))
                frontLine.item(1).trim(tmpCenter)
             
            tmpCenter = adsk.core.Point3D.create((self.w-self.wall)/2,sheetXBase+r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create((self.w-self.wall)/2+r,sheetXBase+r,offset))
                rightBack.item(0).trim(tmpCenter)
                
            tmpCenter = adsk.core.Point3D.create((self.w-self.wall)/2,-sheetXBase-r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create((self.w-self.wall)/2+r,-sheetXBase-r,offset))
                rightFront.item(0).trim(tmpCenter)
            
            tmpCenter = adsk.core.Point3D.create(-(self.w-self.wall)/2,sheetXBase+r,offset)
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-(self.w-self.wall)/2-r,sheetXBase+r,offset))
                leftBack.item(0).trim(tmpCenter)       
            
            tmpCenter = adsk.core.Point3D.create(-(self.w-self.wall)/2,-sheetXBase-r,offset)            
            tmp = sketch.sketchCurves.sketchCircles.addByCenterRadius(tmpCenter,r)
            if(toTrim) : 
                tmp.trim(adsk.core.Point3D.create(-(self.w-self.wall)/2-r,-sheetXBase-r,offset))
                leftFront.item(0).trim(tmpCenter)
        
        extrudes = side.features.extrudeFeatures
        #prof = sketch.profiles[0]
        
        profs = adsk.core.ObjectCollection.create()
            
        for prof in sketch.profiles:
            profs.add(prof)
            
        extrudeInput = extrudes.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distExtrude = adsk.core.ValueInput.createByReal(self.wall)   
        extrudeInput.setDistanceExtent(False, distExtrude)
        
        #Extrude rename
        sideExtrude = extrudes.add(extrudeInput)
        sideExtrude.name = _name        
        
        #Body rename
        sideBody = side.bRepBodies.item(side.bRepBodies.count-1)
        sideBody.name = _name     
                        
        saveToDXF(sketch, _name)
        
        return sideExtrude

#Save to DXF
def saveToDXF(sketch, name):
    # Save to DXF
        # For Windows
        if(platform.system() == 'Windows'):
            #Path to needed folder
            path = os.path.expanduser("~\Desktop\DXF")
        
            #Check that folder
            if not os.path.exists(path):
                os.makedirs(path)
                
            # Save sketch to the folder
            dxf_path = os.path.join(os.environ['USERPROFILE'], path, name + ".dxf")
            sketch.saveAsDXF(dxf_path)
        
        # For Mac
        if(platform.system() == 'Darwin'):
            #Path to needed folder
            path = os.path.expanduser("~/DXF")
        
            #Check that folder
            if not os.path.exists(path):
                os.makedirs(path)
                
            # Save sketch to the folder
            dxf_path = os.path.join("", path, name + ".dxf")
            sketch.saveAsDXF(dxf_path)

# Add data to User Parameters
def userParams():
    
    # ToDo -   
    if not paramExists(design, 'defaultBoxName'):
        design.userParameters.add('defaultBoxName', adsk.core.ValueInput.createByString(defaultBoxName), "", "Box name")
    if not paramExists(design, 'defaultWall'):
        design.userParameters.add('defaultWall', adsk.core.ValueInput.createByReal(0.03), "cm", "Wall thickness")
    if not paramExists(design, 'defaultH'):
        design.userParameters.add('defaultH', adsk.core.ValueInput.createByReal(30), "cm", "Height")
    if not paramExists(design, 'defaultW'):
        design.userParameters.add('defaultW', adsk.core.ValueInput.createByReal(10), "cm", "Width")
    if not paramExists(design, 'defaultD'):
        design.userParameters.add('defaultD', adsk.core.ValueInput.createByReal(10), "cm", "Depth")
    if not paramExists(design, 'defaultKerf'):
        design.userParameters.add('defaultKerf', adsk.core.ValueInput.createByReal(0.03), "cm", "Kerf")
    if not paramExists(design, 'defaultShiftTotal'):
        design.userParameters.add('defaultShiftTotal', adsk.core.ValueInput.createByReal(1), "cm", "Shift total")
    if not paramExists(design, 'defaultSheetAlpha'):
        design.userParameters.add('defaultSheetAlpha', adsk.core.ValueInput.createByReal(0.3), "cm", "Sheet Alpha")
    
# Check if some user parameter exist or not  
def paramExists(design, paramName):
    # Try to get the parameter with the specified name.
    param = design.userParameters.itemByName(paramName)            
    
    # Check to see if a parameter was returned.
    if param:
        return True
    else:
        return False    

def closeAll():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Build a list of the open documents.
        docs = []
        for doc in app.documents:
            docs.append(doc)
        
        # Close all open documents, without saving them.
        for doc in docs:
            doc.close(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        
        #userParams()
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
            
        
        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('BOX')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('BOX',
                    'Create Box',
                    'Create a box.',
                    './resources') # relative resource file path is specified

        onCommandCreated = BoxCommandCreatedHandler()
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