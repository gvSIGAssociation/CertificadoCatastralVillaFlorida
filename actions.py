# encoding: utf-8

import gvsig

import os.path

from os.path import join, dirname

from gvsig import currentView
from gvsig import currentLayer

from java.io import File
from org.gvsig.fmap.mapcontext.layers.vectorial import FLyrVect
from org.gvsig.app import ApplicationLocator
from org.gvsig.andami import PluginsLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools import ToolsLocator
from addons.CertificadoCatastralVillaFlorida.certificadoCatastralVillaFloridaPanel import CertificadoCatastralVillaFloridaPanel, isLayerValid

class CertificadoCatastralVillaFloridaExtension(ScriptingExtension):
  def __init__(self):
    pass
    
  def canQueryByAction(self):
      return True
  
  def isVisible(self, action):
    if currentView()!=None:
      return True
    return False

  def isEnabled(self, action):
    view = currentView()
    if view==None:
      return False
    layer = currentLayer()
    if layer == None:
      return False
    if not isLayerValid(layer):
        return False
    store = layer.getFeatureStore()
    selection = store.getSelection()
    if selection.getSelectedCount() != 1:
      return False
    return True

  def execute(self,actionCommand, *args):
    actionCommand = actionCommand.lower()
    print actionCommand
    if actionCommand == "settool-certificadocatastralvillaflorida":
      certificadoCatastralVillaFlorida = CertificadoCatastralVillaFloridaPanel()
      i18n = ToolsLocator.getI18nManager()
      print "showTool"
      certificadoCatastralVillaFlorida.showTool(i18n.getTranslation("_Certificado_Catastral_Villa_Florida"))
      
def selfRegisterI18n():
  i18nManager = ToolsLocator.getI18nManager()
  i18nManager.addResourceFamily("text",File(gvsig.getResource(__file__,"i18n")))
  
def selfRegister():
  selfRegisterI18n()
  i18n = ToolsLocator.getI18nManager()
  application = ApplicationLocator.getManager()
  actionManager = PluginsLocator.getActionInfoManager()
  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()

  icon = File(gvsig.getResource(__file__,"images","CertificadoCatastral_16x16.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.CertificadoCatastralVillaFlorida", "action", "tools-CertificadoCatastralVillaFlorida", None, icon)

  CertificadoCatastralVillaFlorida_extension = CertificadoCatastralVillaFloridaExtension()
  CertificadoCatastralVillaFlorida_action = actionManager.createAction(
    CertificadoCatastralVillaFlorida_extension,
    "tools-CertificadoCatastralVillaFlorida",   # Action name
    "Certificado Catastral Villa Florida",   # Text
    "settool-CertificadoCatastralVillaFlorida", # Action command
    "tools-CertificadoCatastralVillaFlorida",   # Icon name
    None,                # Accelerator
    1009000000,          # Position
    i18n.getTranslation("_Certificado_Catastral_Villa_Florida")    # Tooltip
  )
  CertificadoCatastralVillaFlorida_action = actionManager.registerAction(CertificadoCatastralVillaFlorida_action)

  # Añadimos la entrada "Report by point" en el menu herramientas
  application.addMenu(CertificadoCatastralVillaFlorida_action, "tools/"+i18n.getTranslation("_Certificado_Catastral_Villa_Florida"))
  # Añadimos el la accion como un boton en la barra de herramientas "Quickinfo".
  #application.addSelectableTool(CertificadoCatastralVillaFlorida_action, "CertificadoCatastralVillaFlorida")
  application.addTool(CertificadoCatastralVillaFlorida_action, "CertificadoCatastralVillaFlorida")

def main(*args):
  selfRegister()