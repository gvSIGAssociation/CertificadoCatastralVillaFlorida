# encoding: utf-8

import gvsig
from org.gvsig.tools import ToolsLocator
from java.io import File, FileInputStream


class CertificadoCatastralVillaFloridaPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"certificadoCatastralVillaFloridaPanel.xml"))
    i18n = ToolsLocator.getI18nManager()
    self.setPreferredSize(320,180)

  def btnGenerarPdf_click(self, event):
    layout = self.loadTemplate()
    context = layout.getLayoutContext()
    feature = None #Coger la feature seleccionada de la vista
    # Nos recorremos todos los elementos del mapa buscando los que hemos etiquetado
    for elemento in  context.getAllFFrames():
      if elemento.getTag() == "Vista":
        # Ajustamos el encuadre de la vista al del elemento seleccionado
        mapContext = elemento.getMapContext()
        mapContext.getViewPort().setEnvelope(encuadre)
        mapContext.invalidate()
        
      elif elemento.getTag() == "Solicitante":
        elemento.clearText() 
        elemento.addText(self.txtSolicitante.getText())
  
      elif elemento.getTag() == "atributo":
        name = elemento.getText().get(0)
        elemento.clearText() 
        elemento.addText(feature.getString(name))
  
      elif elemento.getTag() == "Imagen1":# esto por cada imagen
        # Cambiamos la imagen del logotipo
        elemento.setImage(self.getImage(1))
  
    context.fullRefresh() 

  def getImage(self, idx):
    #TODO
    return None

  def loadTemplate(self):
    xmlFile = File(self,getResource(__file__,"plantilla.gvslt"))
    inputStream = FileInputStream(xmlFile)
  
    persistenceManager = ToolsLocator.getPersistenceManager()
    persistentState = persistenceManager.loadState(inputStream)
    layout = persistenceManager.create(persistentState)
    return layout


def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
