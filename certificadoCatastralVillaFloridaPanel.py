# encoding: utf-8

import gvsig
import os
from ConfigParser import SafeConfigParser

from gvsig.uselib import use_plugin
use_plugin("org.gvsig.app.document.layout2.app.mainplugin")
use_plugin("org.gvsig.pdf.app.mainplugin")

from gvsig.commonsdialog import msgbox

from org.gvsig.tools import ToolsLocator
from org.gvsig.pdf.swing.api import PDFSwingLocator, PDFViewer
from org.gvsig.pdf.lib.api import PDFLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator, ToolsSwingUtils
from org.gvsig.tools.swing.api.windowmanager import WindowManager
from java.io import File, FileInputStream, FileOutputStream
from gvsig.libs.formpanel import FormPanel, FormComponent
from gvsig import currentLayer, currentView
from org.gvsig.app.project.documents.layout.gui import DefaultLayoutPanel
from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools.dispose import DisposeUtils
from java.awt.event import ComponentAdapter
from org.gvsig.tools.util import ToolsUtilLocator
from org.gvsig.fmap.mapcontext.layers.vectorial import FLyrVect
from org.apache.commons.text import WordUtils


from org.gvsig.scripting import ScriptingLocator

REQUIRED_ATTR_NAMES = [
  'CODIGO', 
  'MAPA', 
  'CUADRANTE', 
  'MANZANA', 
  'N_LOTE', 
  'PROPIETARI', 
  'TENENCIA', 
  'AREA_DE_TE', 
  'TIPO_DE_CA', 
  'USO_DE_SUE', 
  'MEJORAS_DE', 
  'USO_CONSTR', 
  'BARRIO', 
  'UBICACION', 
  'IMAGEN1',
  'IMAGEN2',
  'IMAGEN3'
]
def isLayerValid(layer):
  if not isinstance(layer, FLyrVect):
    return False
  store = layer.getFeatureStore()
  featureType = store.getDefaultFeatureTypeQuietly()
  for attrName in REQUIRED_ATTR_NAMES:
    if featureType.get(attrName) == None:
      return False
  return True

def getDataFolder():
  return ScriptingLocator.getManager().getDataFolder("CertificadoCatastralVillaFlorida").getAbsolutePath()

def getConfigFilePath():
  ap = ScriptingLocator.getManager().getDataFolder("CertificadoCatastralVillaFlorida").getAbsolutePath()
  configFile = os.path.join(ap, "config.ini")
  return configFile
  
def readConfigFile():
  parser = SafeConfigParser()
  configFile = getConfigFilePath()
  if os.path.exists(configFile):
    parser.read(configFile) 
    items = dict(parser.items('preferences'))
    return items
  else:
    writeConfigFile(imagesfolder = "")
    return readConfigFile()

def writeConfigFile(**args):
  parser = SafeConfigParser()
  configFile = getConfigFilePath()
  parser.add_section('preferences')
  for k,v in args.items():
    parser.set('preferences', k, v)
  cfgfile = open(configFile,'w')
  parser.write(cfgfile)
  cfgfile.close()


class CertificadoCatastralVillaFloridaPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self, gvsig.getResource(__file__,"certificadoCatastralVillaFloridaPanel.xml"))
    i18n = ToolsLocator.getI18nManager()
    swingManager = ToolsSwingLocator.getToolsSwingManager()

    self.pickerFolder = swingManager.createFolderPickerController(
    self.txtImagesFolder,
    self.btnImagesFolder)

    swingManager.translate(self.lblApplicant)
    swingManager.translate(self.lblImagesFolder)
    swingManager.translate(self.btnGenerateCertificate)
    swingManager.translate(self.lblFecha)
    swingManager.translate(self.lblHora)
    swingManager.translate(self.lblObservaciones)

    config = readConfigFile()
    imagesFolder = config.get("imagesfolder",None)
    if imagesFolder != None:
      self.pickerFolder.set(File(imagesFolder))
    ToolsSwingUtils.ensureRowsCols(self.asJComponent(), 9, 70, 12, 100)


  def btnGenerateCertificate_click(self, event):
    layer = currentLayer()
    if layer == None:
      msgbox(u"Debe seleccionar una capa")
      return
    if not isLayerValid(layer):
      msgbox(u"La capa seleccionada no es válida")
      return
    store = layer.getFeatureStore()
    selection = store.getSelection()
    if selection.getSelectedCount() != 1:
      msgbox(u"Debe seleccionar una y solo una geometría")
      return
    observaciones = WordUtils.wrap(self.txtObservaciones.getText(), 80).split("\n")[:4]
    mapContext = None
    imageFrames = [None, None, None]
    viewFrame = None
    try:
      layout = loadTemplate()
      context = layout.getLayoutContext()
      feature = selection.first()
      
      if feature:
        images = self.getImages(feature)
        #feature = None #Coger la feature seleccionada de la vista
        geometry = feature.getDefaultGeometry()
        encuadre = geometry.buffer(2).getEnvelope()
        # Nos recorremos todos los elementos del mapa buscando los que hemos etiquetado
        for elemento in  context.getAllFFrames():
          if elemento.getTag() == "VISTA":
            # Ajustamos el encuadre de la vista al del elemento seleccionado
            elemento.setView(currentView())
            mapContext = elemento.getMapContext()
            mapContext.getViewPort().setEnvelope(encuadre)
            mapContext.invalidate()
            viewFrame = elemento
          elif elemento.getTag() == "SOLICITANTE":
            elemento.clearText() 
            elemento.addText(self.txtSolicitante.getText())
          elif elemento.getTag() == "FECHA":
            elemento.clearText() 
            elemento.addText(self.txtFecha.getText())
          elif elemento.getTag() == "HORA":
            elemento.clearText() 
            elemento.addText(self.txtHora.getText())
          elif elemento.getTag() == "OBSERVACIONES":
            elemento.clearText() 
            for line in observaciones:
              elemento.addText(line)
          elif elemento.getTag() == "ATRIBUTO":
            name = elemento.getText().get(0)
            elemento.clearText() 
            value = feature.getString(name)
            if value:
              elemento.addText(value)
            else:
              elemento.addText("")
          elif elemento.getTag() == "IMAGEN0":
            elemento.setImage(images[0])
            imageFrames[0] = elemento
      
          elif elemento.getTag() == "IMAGEN1":
            elemento.setImage(images[1])
            imageFrames[1] = elemento
      
          elif elemento.getTag() == "IMAGEN2":
            elemento.setImage(images[2])
            imageFrames[2] = elemento
      for n in range(0,3):
        if images[n] == None:
          context.delFFrame(imageFrames[n])
      
      context.fullRefresh() 
      layout.getLayoutControl().getLayoutDraw().initialize()
  
      tmpFile = ToolsLocator.getFoldersManager().getUniqueTemporaryFile("informe.pdf")
      self.highlightFeature(layer, feature, mapContext)
      layout.layoutToPDF(tmpFile);
    finally:
      DisposeUtils.disposeQuietly(mapContext)
      for f in imageFrames:
        if f != None:
          f.setImage(None)


    desktop = ToolsUtilLocator.getToolsUtilManager().createDesktopOpen()
    desktop.open(tmpFile)

    '''
    pdfDoc = PDFLocator.getPDFManager().createPDFDocument(tmpFile)
    pdfViewer = PDFSwingLocator.getPDFSwingManager().createPDFViewer()
    pdfViewer.setMode(PDFViewer.MODE_COMPLETE)
    pdfViewer.put(pdfDoc)
    pdfViewer.asJComponent().addComponentListener(OnComponentHidden(lambda: pdfViewer.dispose()))

    i18n = ToolsLocator.getI18nManager()
    ToolsSwingLocator.getWindowManager().showWindow(
      pdfViewer.asJComponent(), 
      i18n.getTranslation("_Report"), 
      WindowManager.MODE.WINDOW
      )
      '''

    writeConfigFile(imagesfolder=self.txtImagesFolder.getText())

  def getImages(self, feature):
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    images = [None] * 3
    folder=self.pickerFolder.get()
    if not folder:
      # return a list with 3 None
      return images
    basePath = folder.getAbsolutePath()
    n = 0;
    for s in ["IMAGEN1","IMAGEN2","IMAGEN3"]:
      featImageString = feature.getStringOrDefault(s, None)
      if featImageString:
        imagePath = os.path.join(basePath, featImageString).replace("\\","/")
        if os.path.exists(imagePath):
          image = toolsSwingManager.createSimpleImage(File(imagePath))
          images[n] = image.getBufferedImage()
      n = n+1
    return images

  def highlightFeature(self, layer, feature, mapContext):
    graphics = mapContext.getGraphicsLayer()
    graphics.clearAllGraphics()
    graphics.clearAllSymbols()
    f = os.path.join(getDataFolder(), "selection.gvssym")
    sym = None
    if os.path.exists(f):
      sym = MapContextLocator.getSymbolManager().loadSymbol(File(f))
    if sym == None:
      sym = layer.getLegend().getSymbolByFeature(feature).getSymbolForSelection()
      setTransparency = getattr(sym, 'setTransparency', None)
      if setTransparency != None:
        setTransparency(0.5)
    n = graphics.addSymbol(sym)
    graphics.addGraphic("CertificadoCatastralVillaFlorida", feature.getDefaultGeometry(), n)

def loadTemplate():
  xmlFile = File(gvsig.getResource(__file__,"plantilla.gvslt"))
  inputStream = FileInputStream(xmlFile)

  persistenceManager = ToolsLocator.getPersistenceManager()
  persistentState = persistenceManager.loadState(inputStream)
  layout = persistenceManager.create(persistentState)
  return layout

def saveTemplate(layout):
  xmlFile = File(gvsig.getResource(__file__,"plantilla.gvslt"))
  fos = FileOutputStream(xmlFile)

  persistenceManager = ToolsLocator.getPersistenceManager()
  persistentState = persistenceManager.getState(layout)
  persistenceManager.saveState(persistentState, fos)

class OnComponentHidden(ComponentAdapter):
  def __init__(self, listener):
    self.listener = listener

  def componentHidden(self, *args):
    self.listener();

def fixTemplate():
  layout = loadTemplate()
  context = layout.getLayoutContext()
  for elemento in  context.getAllFFrames():
    if elemento.getTag() == "VISTA":
      # Ajustamos el encuadre de la vista al del elemento seleccionado
      elemento.setView(None)
  saveTemplate(layout)

def main(*args):

    i18n = ToolsLocator.getI18nManager()
    swingManager = ToolsSwingLocator.getToolsSwingManager()
    f = CertificadoCatastralVillaFloridaPanel()
    f.showWindow(i18n.getTranslation("_Certificado_Catastral_Villa_Florida"))
    #fixTemplate()
