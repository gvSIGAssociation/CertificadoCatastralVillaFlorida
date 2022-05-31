# encoding: utf-8

import gvsig
import os

from gvsig.uselib import use_plugin
use_plugin("org.gvsig.app.document.layout2.app.mainplugin")

from org.gvsig.tools import ToolsLocator
from org.gvsig.pdf.swing.api import PDFSwingLocator, PDFViewer
from org.gvsig.pdf.lib.api import PDFLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager
from java.io import File, FileInputStream
from gvsig.libs.formpanel import FormPanel, FormComponent
from gvsig import currentLayer
from org.gvsig.app.project.documents.layout.gui import DefaultLayoutPanel




class CertificadoCatastralVillaFloridaPanel(FormPanel):
  def __init__(self, layer):
    FormPanel.__init__(self, gvsig.getResource(__file__,"certificadoCatastralVillaFloridaPanel.xml"))
    i18n = ToolsLocator.getI18nManager()
    swingManager = ToolsSwingLocator.getToolsSwingManager()
    self.setPreferredSize(480,180)
    self.layer = layer

    self.pickerFolder = swingManager.createFolderPickerController(
    self.txtImagesFolder,
    self.btnImagesFolder)

    swingManager.translate(self.lblApplicant)
    swingManager.translate(self.lblImagesFolder)
    swingManager.translate(self.btnGenerateCertificate)


  def btnGenerateCertificate_click(self, event):
    layout = self.loadTemplate()
    context = layout.getLayoutContext()
    store = self.layer.getFeatureStore()
    selection = store.getSelection()
    if selection.getSelectedCount() != 1:
      return

    images = self.getImages()
    for feature in selection:
      #feature = None #Coger la feature seleccionada de la vista
      geometry = feature.getDefaultGeometry()
      encuadre = geometry.buffer(2).getEnvelope()
      # Nos recorremos todos los elementos del mapa buscando los que hemos etiquetado
      for elemento in  context.getAllFFrames():
        if elemento.getTag() == "VISTA":
          # Ajustamos el encuadre de la vista al del elemento seleccionado
          mapContext = elemento.getMapContext()
          mapContext.getViewPort().setEnvelope(encuadre)
          mapContext.invalidate()
          
        elif elemento.getTag() == "SOLICITANTE":
          elemento.clearText() 
          elemento.addText(self.txtSolicitante.getText())
    
        elif elemento.getTag() == "ATRIBUTO":
          name = elemento.getText().get(0)
          elemento.clearText() 
          elemento.addText(feature.getString(name))

        elif elemento.getTag() == "IMAGEN0" and len(images) > 0:
          elemento.setImage(images[0])
    
        elif elemento.getTag() == "IMAGEN1" and len(images) > 1:
          elemento.setImage(images[1])
    
        elif elemento.getTag() == "IMAGEN2" and len(images) > 2:
          elemento.setImage(images[2])
      break
    context.fullRefresh() 
    layout.getLayoutControl().getLayoutDraw().initialize()

    tmpFile = ToolsLocator.getFoldersManager().getUniqueTemporaryFile("informe.pdf")
    
    layout.layoutToPDF(tmpFile);

    pdfDoc = PDFLocator.getPDFManager().createPDFDocument(tmpFile)
    pdfViewer = PDFSwingLocator.getPDFSwingManager().createPDFViewer()
    pdfViewer.setMode(PDFViewer.MODE_COMPLETE)
    pdfViewer.put(pdfDoc)

    i18n = ToolsLocator.getI18nManager()
    ToolsSwingLocator.getWindowManager().showWindow(
      pdfViewer.asJComponent(), 
      i18n.getTranslation("_Report"), 
      WindowManager.MODE.WINDOW
      ) 

  def getImages(self):
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    folder=self.pickerFolder.get()
    if folder == None:
      return list()
    basePath = folder.getAbsolutePath()
    imagesPath = os.listdir(basePath)
    images = list()
    for n in range(0,3):
      if len(imagesPath) <= n:
        images.append(None)
        continue
      image = toolsSwingManager.createSimpleImage(basePath+os.sep+imagesPath[n])
      images.append(image.getBufferedImage())
    return images

  def loadTemplate(self):
    xmlFile = File(gvsig.getResource(__file__,"plantilla.gvslt"))
    inputStream = FileInputStream(xmlFile)
  
    persistenceManager = ToolsLocator.getPersistenceManager()
    persistentState = persistenceManager.loadState(inputStream)
    layout = persistenceManager.create(persistentState)
    return layout


def main(*args):

    i18n = ToolsLocator.getI18nManager()
    swingManager = ToolsSwingLocator.getToolsSwingManager()
    f = CertificadoCatastralVillaFloridaPanel(currentLayer())
    f.showWindow(i18n.getTranslation("_Certificado_Catastral_Villa_Florida"))

    print "hola mundo"
    pass
