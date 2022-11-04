from tkinter import *
from tkinter import ttk
import codeBar as cb
import settings as glob

class procedureBar(Frame):
    def __init__(self, parent, root, procedureName, procArg = 0):
        self.parent = parent
        self.root = root
        self.events_listeners = {}
        self.name = procedureName
        self.toggled = IntVar()
        self.procArg = StringVar()
        self.procArg.set(procArg)
        Frame.__init__(self, parent)
        self.configure(borderwidth=3, background='black', relief=RAISED)
        self.pack(fill=NONE, expand=FALSE)
        self.procButton = Checkbutton( self, text=self.name, variable=self.toggled, onvalue="1", offvalue="0", indicatoron=0, command=self.groupAssign)
        self.procButton.pack(side=LEFT, fill=BOTH, expand=TRUE)
        buttonPad = Frame(self)
        buttonPad.pack(side=LEFT, fill=BOTH)
        procAddButt = Button(buttonPad, text="Add to program", command=self.appendProcedure)
        procAddButt.pack(fill=X)
        self.procEntry = Entry(buttonPad, textvariable=self.procArg, width=6, justify=CENTER)
        self.procEntry.pack(fill=X)

    def assignCommands(self, commands):
        self.commands = commands

    def getToggleStatus(self):
        return self.toggled.get()

    def groupAssign(self):
        if self.toggled.get():
            self.root.addProcToGroup(self)
        else:
            self.root.delProcFromGroup(self)


    def appendProcedure(self):
        newProc = cb.codeBar(self.root.codePane.interior, self.root, self.name)
        self.root.appendProcedureToProgram(newProc)

    def getName(self):
        return self.name

#########HOMING##################

class homingProcedure(procedureBar):
    def __init__(self, parent, root, procedureName):
        procedureBar.__init__(self, parent, root, procedureName)
        self.procEntry.config(state=DISABLED)

    def appendProcedure(self):
        newProc=cb.homingBar(self.root.codePane.interior, self.root, self.name)
        self.root.appendProcedureToProgram(newProc)

#########LOAD##################

class loadProcedure(procedureBar):
    def __init__(self, parent, root, procedureName, content, xDist, zDist):
        procedureBar.__init__(self, parent, root, procedureName, glob.configs['DefaultLoadRange'])
        self.content = content
        self.xDist = xDist
        self.zDist = zDist

    def appendProcedure(self):
        newProc=cb.loadBar(self.root.codePane.interior, self.root, self.name, self.content, self.xDist, self.zDist, self.procArg.get())
        self.root.appendProcedureToProgram(newProc)

#########UNLOAD##################

class unloadProcedure(procedureBar):
    def __init__(self, parent, root, procedureName, xDist):
        procedureBar.__init__(self, parent, root, procedureName, glob.configs['DefaultLoadRange'])
        self.xDist = xDist

    def appendProcedure(self):
        newProc = cb.unloadBar(self.root.codePane.interior, self.root, self.name, self.xDist, self.procArg.get())
        self.root.appendProcedureToProgram(newProc)

#########SHAKE##################

class shakeProcedure(procedureBar):
    def __init__(self, parent, root, procedureName, totalTime):
        procedureBar.__init__(self, parent, root, procedureName, totalTime)

    def appendProcedure(self):
        newProc = cb.shakeBar(self.root.codePane.interior, self.root, self.name, self.procArg.get())
        self.root.appendProcedureToProgram(newProc)


class groupProcedure(procedureBar):
    def __init__(self, parent, root, procedureName, procList):
        procedureBar.__init__(self, parent, root, procedureName)
        self.procEntry.config(state=DISABLED)
        self.procedures = list(procList)


    def appendProcedure(self):
        for proc in self.procedures:
            proc.appendProcedure()