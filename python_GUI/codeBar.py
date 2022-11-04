from tkinter import *
from tkinter import messagebox
import settings as glob

'''
_WorkHeight=60
_StartxPosition=100

_ShakeHeight=60
_ShakeXDist=150
_ShakeStepDelay = 800
_ShakeStepAngleRange = [5, 160]

_servoFillAngle=171

_Zfeedrate=666
_Xfeedrate=1500

_HWservoDelay=5 #Delay after servo move (MUST BE SAME IN FIRMWARE (for MARLIN in config.h)!!!)
'''
_ActualSyringeStatus=180
'''
_SyringeHomeRest=20 #sec to wait before synthesis start

_servosAttachPin=57
_LoadStepDelay=230
_UnloadStepDelay=140
_MaxLoadRange=8.0 #ml
'''

def volumeToServoAngles(vol, totalVolume):
    servoSteps=180
    return servoSteps*float(vol)/float(totalVolume)

def setSyringeToInitialState():
    global _ActualSyringeStatus
    _ActualSyringeStatus=180

class codeBar(PanedWindow):
    def __init__(self, parent, root, procedureName, innerArg=0):
        self.parent = parent
        self.root = root
        self.procName = procedureName
        PanedWindow.__init__(self, parent)
        self.configure(borderwidth=3, background='green')
        self.pack(fill=BOTH, expand=TRUE)

        self.procPad = Frame(self)
        self.procPad.pack(fill=Y)
        self.add(self.procPad)
        self.label = Label(self.procPad, text=self.procName)
        self.label.pack(fill=X)
        self.innerArg = StringVar()
        self.innerArg.set(innerArg)
        if innerArg:
            self.entry=Entry(self.procPad, textvariable=self.innerArg, width=6, justify=CENTER)
            self.entry.pack()

        self.buttonPad = Frame(self)
        self.buttonPad.pack(fill=NONE)
        self.add(self.buttonPad)
        self.bottomUp = Button(self.buttonPad, text="UP", command=self.moveProcedureUpInCode)
        self.bottomUp.pack(fill=X)
        self.bottomDown = Button(self.buttonPad, text="DOWN", command=self.moveProcedureDownInCode)
        self.bottomDown.pack(fill=X)
        self.bottomRem = Button(self.buttonPad, text="Remove", command=self.removeProcedureFromCode)
        self.bottomRem.pack(fill=X)

    def removeProcedureFromCode(self):
        self.root.removeProcedureFromProgram(self)

    def moveProcedureUpInCode(self):
        self.root.moveInCode(self, -1)

    def moveProcedureDownInCode(self):
        self.root.moveInCode(self, 1)

    def getName(self):
        return self.procName

    def getIndex(self):
        return self.indexInCode

    def getCommand(self):
        pass

    def getInnerArg(self):
        return self.innerArg.get()

    def sanityCheck(self, sLevel):
        if (sLevel < 0 or sLevel > 180):
            messagebox.showwarning("Syringe overflow!!!", "Warning syringe overflow or underflow during procedure!")

class homingBar(codeBar):
    def __init__(self, parent, root, procedureName):
        codeBar.__init__(self, parent, root, procedureName)

    def getCommand(self):
        HomingString = ["M280 P0 S%i" % glob.configs['ServoFillAngle'],
                        "G28 X Z ; Home the X and Z axes",
                        "M280 P0 S%i" % glob.configs['ServoFillAngle'],
                        "G21 ; set units to millimeters",
                        "G90 ; use absolute positioning",
                        "G1 Z%i F%i ; gain attitude" % (glob.configs['WorkHeight'], glob.configs['Zfeedrate']),
                        "G1 X%i F%i ;" % (glob._StartxPosition, glob.configs['Xfeedrate']),
                        "M42 P%i S255 ; turn servos on" % glob.configs['ServosAttachPin'],
                        "M280 P1 S180 ; set max unload",
                        "G4 S%i ; wait" % glob.configs['SyringeHomeRest'],
                        "M42 P%i S0 ; turn servos off" % glob.configs['ServosAttachPin']]
        return HomingString


class loadBar(codeBar):
    def __init__(self, parent, root, procedureName, bedContent, bedDistance, bedHeight, loadVol):
        codeBar.__init__(self, parent, root, procedureName, loadVol)
        self.bedDistance = bedDistance
        self.bedHeight = bedHeight
        self.bedContent = bedContent

    def getContent(self):
        return self.bedContent

    def getLoadVol(self):
        return float(self.entry.get())

    def getCommand(self):
        global _ActualSyringeStatus
        comString = ["G1 Z%i F%i" % (glob.configs['WorkHeight'], glob.configs['Zfeedrate']),
                     "M280 P0 S%i" % glob.configs['ServoFillAngle'],
                     "G1 X%i F%i ; go to %s position" % (int(self.bedDistance), glob.configs['Xfeedrate'], self.bedContent),
                     "G1 Z%i F%i ;" % (int(self.bedHeight), glob.configs['Zfeedrate']),
                     "M280 P0 S%i" % glob.configs['ServoFillAngle'],
                     "M42 P%i S255 ; turn servos on" % glob.configs['ServosAttachPin']]
        syringeEndState=int(_ActualSyringeStatus-volumeToServoAngles(self.entry.get(), glob.configs['MaxLoadRange']))
        self.sanityCheck(syringeEndState)
        for i in range(_ActualSyringeStatus, syringeEndState, -1):
            comString.append("M280 P1 S%i" % i)
            comString.append("G4 P%i" % glob.configs['LoadStepDelay'])

        comString.append("M281 P1 ; detach servo 1")
        comString.append("M42 P%i S0 ; turn servos off" % glob.configs['ServosAttachPin'])
        comString.append("M280 P0 S%i" % glob.configs['ServoFillAngle'])
        comString.append("G1 Z%i F%i ; elevate to work height" % (glob.configs['WorkHeight'], glob.configs['Zfeedrate']))
        _ActualSyringeStatus = syringeEndState
        return comString

volumeToServoAngles
class unloadBar(codeBar):
    def __init__(self, parent, root, procedureName, bedDistance, loadVol):
        codeBar.__init__(self, parent, root, procedureName, loadVol)
        self.bedDistance = bedDistance

    def getCommand(self):
        global _ActualSyringeStatus
        comString = ["G1 Z%i F%i" % (glob.configs['WorkHeight'], glob.configs['Zfeedrate']),
                     "M280 P0 S%i" % glob.configs['ServoFillAngle'],
                     "G1 X%i F%i ; go to HOLE position" % (int(self.bedDistance), glob.configs['Xfeedrate']),
                     "G28 Z ; Home Z axes",
                     "M280 P0 S%i" % glob._servoFillAngle,
                     "M42 P%i S255 ; turn servos on" % glob.configs['ServosAttachPin']]
        syringeEndState=int(_ActualSyringeStatus+volumeToServoAngles(self.entry.get(), glob.configs['MaxLoadRange']))
        self.sanityCheck(syringeEndState)
        for i in range(_ActualSyringeStatus, syringeEndState, 1):
            comString.append("M280 P1 S%i" % i)
            comString.append("G4 P%i" % glob.configs['UnloadStepDelay'])

        comString.append("M281 P1 ; detach servo 1")
        comString.append("M42 P%i S0 ; turn servos off" % glob.configs['ServosAttachPin'])
        comString.append("M280 P0 S%i" % glob.configs['ServoFillAngle'])
        comString.append("G1 Z%i F%i ; elevate to work height" % (glob.configs['WorkHeight'], glob.configs['Zfeedrate']))
        _ActualSyringeStatus = syringeEndState
        return comString


class shakeBar(codeBar):
    def __init__(self, parent, root, procedureName, totalTime):
        codeBar.__init__(self, parent, root, procedureName, totalTime)

    def getCommand(self):
        nofCycles = int(float(self.entry.get())*60000/(2*glob.configs['ShakeStepDelay'] + glob.configs['HWservoDelay']))

        comString = ["G1 Z%i F%i; park in safe zone" % (glob.configs['ShakeHeight'], glob.configs['Zfeedrate']),
                     "G1 X%i F%i" % (glob.configs['ShakeXDist'], glob.configs['Xfeedrate'])]

        for i in range(nofCycles):
            comString.append("G4 P%i" % glob.configs['ShakeStepDelay'])
            comString.append("M280 P0 S%i" % glob.configs['ShakeTopAngle'])
            comString.append("G4 P%i" % glob.configs['ShakeStepDelay'])
            comString.append("M280 P0 S%i" % glob.configs['ShakeBottomAngle'])
        comString.append("M280 P0 S%i" % glob.configs['ServoFillAngle'])
        return comString
