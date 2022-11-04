
from tkinter import *
from tkinter import ttk
import csv
import os
import collections
from procedureBar import *
from tkinter import messagebox
import codeBar as cb
import settings as glob

programCode=[]    # list of commands
procedures=[]
bedBars = []
glob.init()

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

    def reorderWidgets(self):
        for widgts in programCode:
            widgts.pack_forget()
            widgts.pack()


class BedBar(LabelFrame):
    def __init__(self, parent, number, content, distance, height):
        self.parent = parent
        LabelFrame.__init__(self, parent, text=number)
        self.configure(borderwidth=3, background='yellow', relief=RAISED)
        self.pack(expand=FALSE)
        self.bedContent = StringVar()
        self.label = Entry(self, textvariable=self.bedContent, width=6, justify=CENTER)
        self.bedContent.set(content)
        self.label.pack()
        self.pict = Canvas(self, bg="blue", height=20, width=30)
        self.pict.pack()
        self.distance = distance
        self.height = height
        self.distLabel = Label(self, text=self.distance)
        self.heightLabel = Label(self, text=self.height)
        self.distLabel.pack()
        self.heightLabel.pack()

    def getContent(self):
        return self.bedContent

    def getDistance(self):
        return self.distance

    def getHeight(self):
        return self.height


class BattenPanel(Frame):
    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, parent)
        self.configure(borderwidth=3, background='black', relief=RAISED)
        self.pack(fill=X, expand=TRUE)
        self.initialize()

    def initialize(self):
        for bed in bedBars:
            newBar=BedBar(self, bed[0], bed[1], bed[2], bed[3])
            newBar.pack(side=LEFT)


class simpleapp_tk(Frame):
    groupedProcedure = []
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def addProcToGroup(self, proc):
        self.groupedProcedure.append(proc)
        self.setGroupButtonState()

    def delProcFromGroup(self, proc):
        self.groupedProcedure.remove(proc)
        self.setGroupButtonState()

    def setGroupButtonState(self):
        if self.groupedProcedure:
            self.bottonAddProc.config(state='normal')
        else:
            self.bottonAddProc.config(state=DISABLED)


    def appendProcedureToProgram(self, procedure):
        programCode.append(procedure)

    def removeProcedureFromProgram(self, procedure):
        del programCode[programCode.index(procedure)]
        procedure.destroy()

    def moveInCode(self, procedure, direction):
        procIndex = programCode.index(procedure)
        if direction == -1 and procIndex > 0:
            programCode[procIndex], programCode[procIndex-1] = programCode[procIndex-1], programCode[procIndex]
        elif direction == 1 and procIndex < (len(programCode)-1):
            programCode[procIndex], programCode[procIndex + 1] = programCode[procIndex + 1], programCode[procIndex]
        self.codePane.reorderWidgets()

    def generateGCode(self, event):
        cnt = collections.Counter()
        f = open('new.gcode', 'w')
        for procedure in programCode:
            if isinstance(procedure, cb.loadBar):
                cnt[procedure.getContent()]+=float(procedure.getInnerArg())
            commList=procedure.getCommand()
            for gCom in commList:
                f.write(gCom)
                f.write("\n")
        f.close()
        cb.setSyringeToInitialState()
        message = "GCode generation complete!\nProcedure will use:\n"
        for element in cnt:
            message += ("%s %.1f ml\n" % (element, cnt[element]))
        print(message)
        messagebox.showinfo("GCode done!", message)

    def saveProgramCode(self, event):
        f = open('new.code','w')
        for procedure in programCode:
            f.write(procedure.getName())
            f.write(";")
            f.write(procedure.getInnerArg())
            f.write("\n")
        f.close()
        print("Code saved to new.code")

    def settingWindow(self):
        top = Toplevel()
        top.title("Setting")
        top.focus_set()

        entries = {}
        entVars = []
        labels = []

        def applyConfig():
            floatParametersKeys=['MaxLoadRange', 'DefaultLoadRange']
            for keys in entries:
                if keys in floatParametersKeys:
                    glob.configs[keys] = float(entries[keys].get())
                else:
                    glob.configs[keys] = int(entries[keys].get())

            glob.saveConfig()

        rowIndx=0
        for atrribute in glob.configs:
            labels.append(Label(top, text=atrribute).grid(row=rowIndx,column=0))
            #entVars.append(StringVar())
            #entVars[-1].set(glob.configs[atrribute])
            new = Entry(top)
            new.grid(row=rowIndx,column=1)
            new.insert(0,glob.configs[atrribute])
            entries[atrribute]=new

            rowIndx += 1

        tlOk = Button(top, text="Apply", command=applyConfig).grid(row=rowIndx, column=0)
        tlClose = Button(top, text="Zavřít", command=top.destroy).grid(row=rowIndx,column=1)


    def getBedBarDist(self, procContent):
        for bed in bedBars:
            if procContent in bed:
                return bed[2]
        return 0

    def getBedBarHeight(self, procContent):
        for bed in bedBars:
            if procContent in bed:
                return bed[3]
        return 0

    def loadProgramCode(self, event):
        fName = "new.code"
        if os.path.exists(fName):
            try:
                with open(fName, 'r') as f:
                    reader = csv.reader(f)
                    for step in programCode:
                        self.removeProcedureFromProgram(step)
                    for row in reader:
                        procName, procArgs = row[0].split(";")
                        procName = procName.split()
                        if procName[0] == "Naber":
                            procContent = " ".join(procName[1:])
                            bedDistance = self.getBedBarDist(procContent)
                            bedHeight = self.getBedBarHeight(procContent)
                            if bedDistance:
                                newProc = cb.loadBar(self.codePane.interior, self, procName, procContent, bedDistance, bedHeight, loadVol=procArgs)
                                self.appendProcedureToProgram(newProc)
                            else:
                                messagebox.showwarning("No bedBar!!!",  "Content " + procContent + " not available!")
                        elif procName[0] == "Vyprazdnit":
                            bedDistance = self.getBedBarDist("HOLE")
                            #bedHeight = self.getBedBarHeight("HOLE")
                            if bedDistance:
                                newProc = cb.unloadBar(self.codePane.interior, self, procName, bedDistance, loadVol=procArgs)
                                self.appendProcedureToProgram(newProc)
                            else:
                                messagebox.showwarning("No bedBar!!!", "No HOLE at bedBar available!")
                        elif  procName[0] == "Michej":
                            newProc = cb.shakeBar(self.codePane.interior, self, procName[0], procArgs)
                            self.appendProcedureToProgram(newProc)
                        elif procName[0] == "Zaparkuj":
                            newProc = cb.homingBar(self.codePane.interior, self, procName[0])
                            self.appendProcedureToProgram(newProc)
                        else:
                            messagebox.showwarning("No procedure!!!", "Procedure " + procName + " not available!")

                    print("Code loaded from file:", fName)
            except IOError:
                print("Could not read file:", fName)
        else:
            print("File not exist:", fName)


    def prepareDefaultProcedures(self, containter):
        global procedures
        procedures = []
        newProcBar = homingProcedure(containter, self, 'Zaparkuj')
        procedures.append(newProcBar)
        newProcBar.pack(fill=X, expand=TRUE)
        newProcBar.appendProcedure()
        for bed in bedBars:
            bedContent = bed[1]
            bedDistance = bed[2]
            bedHeight = bed[3]
            if bedContent=="HOLE":
                newProcBar = unloadProcedure(containter, self, 'Vyprazdnit', bedDistance)
            else:
                newProcBar = loadProcedure(containter, self, 'Naber ' + bedContent, bedContent, bedDistance, bedHeight)
            newProcBar.pack(fill=X, expand=TRUE)
            procedures.append(newProcBar)

        newProcBar = shakeProcedure(containter, self, 'Michej', 15)
        procedures.append(newProcBar)
        newProcBar.pack(fill=X, expand=TRUE)



    def initialize(self):
        self.parent.title("PyPeS")
        self.pack(fill=BOTH, expand=True)

        TopPanel = Frame(self)
        TopPanel.pack(fill=X, expand=FALSE, padx=8, pady=8)
        loadProgramBut = Button(TopPanel, text="Load Program")
        loadProgramBut.bind("<Button-1>", self.loadProgramCode)
        loadProgramBut.pack(side=LEFT, padx=5, pady=5)

        saveProgramBut = Button(TopPanel, text="Save Program")
        saveProgramBut.bind("<Button-1>", self.saveProgramCode)
        saveProgramBut.pack(side=LEFT, padx=5, pady=5)
        gengcodeBut = Button(TopPanel, text="Generate g-code")
        gengcodeBut.bind("<Button-1>", self.generateGCode)
        gengcodeBut.pack(side=LEFT, padx=5, pady=5)
    ################################################
        MiddlePanel = Frame(self)
        MiddlePanel.pack(fill=BOTH, expand=TRUE)

        self.CodePanel = LabelFrame(MiddlePanel, text = "Program: ", borderwidth=4)
        self.CodePanel.pack(side=LEFT, fill=Y, padx=20, pady=10)
        self.codePane = VerticalScrolledFrame(self.CodePanel)
        self.codePane.pack(fill=BOTH, expand=TRUE)

        self.proceduresPanel = LabelFrame(MiddlePanel, text = "Procedures: ", borderwidth=4)
        self.proceduresPanel.pack(side=LEFT, fill=BOTH, expand=TRUE, pady=10)

        topProcPanel = Frame(self.proceduresPanel)
        topProcPanel.pack(fill=X)

        self.bottonAddProc = Button(topProcPanel, text="Group procedures", command=self.groupProcedures, state=DISABLED)
        self.bottonAddProc.pack(side=LEFT, padx=5, pady=5)

        self.bottonSettings = Button(topProcPanel, text="Settings", command=self.settingWindow)
        self.bottonSettings.pack(side=LEFT, padx=5, pady=5)

        sepLine = ttk.Separator(self.proceduresPanel, orient=HORIZONTAL)
        sepLine.pack(fill=X)

        self.proceduresPane = VerticalScrolledFrame(self.proceduresPanel)
        self.proceduresPane.pack(fill=BOTH, expand=TRUE)

        self.BaseProceduresPane = Frame(self.proceduresPane.interior)
        self.BaseProceduresPane.pack(fill=Y, expand=FALSE, side=LEFT)

        self.userProceduresPane = Frame(self.proceduresPane.interior)
        self.userProceduresPane.pack(fill=Y, expand=FALSE, side=LEFT)

        self.prepareDefaultProcedures(self.BaseProceduresPane)
    ##################################################
        BottomPanel = Frame(self)
        BottomPanel.pack(expand=FALSE)
        bottom = Button(BottomPanel, text="Synthesize")
        bottom.pack()
        battenPanel = BattenPanel(BottomPanel)
        battenPanel.pack(fill=X, expand=TRUE)

    ##################################################
    def groupProcedures(self):
        groupedProcedureName = ""
        for proc in self.groupedProcedure:
            groupedProcedureName += ("%s\n" % proc.getName())

        newProcBar = groupProcedure(self.userProceduresPane, self, groupedProcedureName, self.groupedProcedure)
        newProcBar.pack(fill=X, expand=FALSE, side=TOP, anchor=N)
        #print(groupedProcedure)

    def OnButtonClick(self):
        self.labelVariable.set( self.entryVariable.get()+" (You clicked the button)" )
        self.entry.focus_set()
        self.entry.selection_range(0, END)

    def OnPressEnter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed ENTER)" )
        self.entry.focus_set()
        self.entry.selection_range(0, END)


def loadConfFiles():
    fName = "batten.bar"
    if os.path.exists(fName):
        try:
            with open(fName, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    bedBars.append(row)
                print("Bad loaded from file:",fName)
        except IOError:
            print("Could not read file:", fName)
    else:
        print("File not exist:", fName)


def main():
    loadConfFiles()
    root = Tk()
    root.geometry("900x700")
    app = simpleapp_tk(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""
    app = simpleapp_tk(None)
    app.title('my application')
    app.mainloop()
"""


