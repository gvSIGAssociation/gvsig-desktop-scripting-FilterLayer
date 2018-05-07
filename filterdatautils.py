# encoding: utf-8

import gvsig
from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator


from org.gvsig.fmap.mapcontext.layers import LayerCollectionListener
from org.gvsig.fmap.mapcontext.layers.operations import LayerCollection
from org.gvsig.fmap.mapcontext.layers import LayerListener


class UpdateToCListener(LayerListener,LayerCollectionListener):
  def __init__(self, id, callable):
    self.callable = callable
    self.id = id

  def getId(self):
    return self.id

  def fireEvent(self):
    try:
      self.callable()
    except Exception,ex:
      pass
  
  def layerAdded(self, e):
    layer = e.getAffectedLayer()
    if isinstance(layer,LayerCollection):
      layer.addLayerCollectionListener(self)
    self.fireEvent()
    
  def layerAdding(self, e):
    pass

  def layerMoved(self, e):
    self.fireEvent()

  def layerMoving(self, e):
    pass

  def layerRemoved(self, e):
    self.fireEvent()

  def layerRemoving(self, e):
    pass

  def visibilityChanged(self, e):
    self.fireEvent()
  
  def activationChanged(self,e):
    self.fireEvent()

  def drawValueChanged(self,e):
    self.fireEvent()

  def editionChanged(self,e):
    self.fireEvent()

  def nameChanged(self,e):
    self.fireEvent()


class UpdateListener():
  def __init__(self, ui):
    self.ui = ui

  def __call__(self):
    #updateAll(self.tree, self.mapContext)
    self.ui._updateUI()
    print "ui"
    pass
    
def addUpdateToCListener(id, mapContext, func):
  layers = mapContext.getLayers()
  if layers == None:
    return
  mylistener = UpdateToCListener(id,func)
  layersList = list()
  layersList.append(layers)
  layersList.extend(mapContext.deepiterator()) 
  for layer in layersList:
    listeners = layer.getLayerListeners()
    for listener in listeners:
      if isinstance(listener,UpdateToCListener) and listener.getId()==id:
        layer.removeLayerListener(listener)
    if isinstance(layer, LayerCollection):
      layer.addLayerCollectionListener(mylistener)
    layer.addLayerListener(mylistener)
    
def getIconFromLayer(layer):
  global mapContextManager
  global iconTheme
  if layer == None or layer.getDataStore()==None:
      return None
  providerName = layer.getDataStore().getProviderName()
  if providerName != None:
    if mapContextManager == None:
      mapContextManager = MapContextLocator.getMapContextManager()
    iconName = mapContextManager.getIconLayer(providerName)
    if iconTheme == None:
      iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
    icon = iconTheme.get(iconName)
    return icon
  return 
