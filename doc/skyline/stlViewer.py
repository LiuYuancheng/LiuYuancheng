# This Stl viewer is follow Pollux31's implement VTK in a wxPython Window example 
# to show the STL file in a wxPython window.

import os
import vtk
from vtk.wx.wxVTKRenderWindow import wxVTKRenderWindow
import wx

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = "LiuYuancheng-2024-github-skyline.stl"  

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class VTKFrame(wx.Frame):
    def __init__(self, parent, id):
        # create wx.Frame and wxVTKRenderWindowInteractor to put in it
        wx.Frame.__init__(self, parent, id, "STL Viewer", size=(800,600))
        
        # create a menu
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        quitMenu = menu.Append(-1, "&Open", "Open")
        self.Bind(wx.EVT_MENU, self.onOpenFile, quitMenu)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        
        # create a donut polydata source
        self.filePath = FILE_NAME
        self.actor = None
        # the render is a 3D Scene
        if self.filePath: self.actor = self.getStlFileActor()

        self.ren = vtk.vtkRenderer()
        if self.actor: self.ren.AddActor(self.actor)
        self.ren.SetBackground(0.121, 0.121, 0.121)

        #make sure the RWI sizes to fill the frame
        self.rwi = wxVTKRenderWindow(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rwi, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        # sequence of init is different
        self.rwi.Enable(1)
        # add created renderer to the RWI's buit-in renderer window
        self.rwi.GetRenderWindow().AddRenderer(self.ren)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def getStlFileActor(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(self.filePath)
        # connect it to Polydatamapper
        m = vtk.vtkPolyDataMapper()
        m.SetInputConnection(reader.GetOutputPort())
        # create an actor to represent the donut in the scene
        actor = vtk.vtkActor()
        actor.SetMapper(m)
        actor.GetProperty().SetColor(0.25, 0.768, 0.388)
        actor.GetProperty().SetSpecular(0.3)
        return actor

    def onOpenFile(self, event):
        openFileDialog = wx.FileDialog(self, "Open", dirpath, "", 
            "Packet Capture Files (*.stl)|*.stl", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.filePath = str(openFileDialog.GetPath())
        openFileDialog.Destroy()
        print(self.filePath)
        self.actor = self.getStlFileActor()
        if self.actor: self.ren.RemoveAllViewProps()

        self.ren.AddActor(self.actor)
        print("load stl file done")
        self.Refresh()

    def onClose(self, envent):
        self.ren.RemoveAllViewProps() 
        del self.ren 
        self.rwi.GetRenderWindow().Finalize() 
        del self.rwi 
        self.Destroy()

# start the wx loop
app = wx.PySimpleApp()
frame = VTKFrame(None, -1)
frame.Show()
app.MainLoop()
