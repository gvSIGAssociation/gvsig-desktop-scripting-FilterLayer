# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel
import os
from javax.swing import DefaultListModel
from org.gvsig.fmap.dal import DALLocator
from java.lang import Number
from javax.swing.table import DefaultTableModel
from java.awt import BorderLayout
from org.gvsig.app.gui.filter import FilterDialog

from org.gvsig.fmap.dal.swing import DALSwingLocator

class AdvancedFilterDialog(FilterDialog):
    pass
    
class Panel(FormPanel):
    view = None
    
    def __init__(self):
        FormPanel.__init__(self, os.path.join(os.path.dirname(__file__), "filterdata.xml"))
        self.view = gvsig.currentView()
        self.nw = None

        # Advanced dialog
        #tbpanel = AdvancedFilterDialog()

        ##
        #nw = DALSwingLocator.getSwingManager().createExpression()
        #self.jpFilter.add(tbpanel)
        self.jpFilter.updateUI()

        # Fill dialog
        layers = gvsig.currentView().getLayers()
        self.cmbLayers.removeAllItems()
        for layer in layers:
           self.cmbLayers.addItem(str(layer.getName()))
        self._updateFields()
        
        self.nw = DALSwingLocator.getSwingManager().createQueryFilterExpresion(gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem()).getFeatureStore())
        bl = BorderLayout()
        self.jpFilter.setLayout(bl)
        self.jpFilter.add(self.nw)
        
    def _updateAdvancedFilter(self):
        #self.jpFilter.getComponents()[0]
        if self.nw == None:
            return
        store = gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem()).getFeatureStore()
        self.nw.setFeatureStore(store)
        
    def _updateFields(self):
        self.cmbFields.removeAllItems()
        layer = gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem())
        if layer == None:
            return
        ft = layer.getFeatureStore().getDefaultFeatureType()
        ds = ft.getAttributeDescriptors()
        self.cmbFields.addItem("")
        for d in ds:
            self.cmbFields.addItem(str(d.getName())) 

    def _updateListValues(self):
        field = self.cmbFields.getSelectedItem()
        if field == None or field == "":
            return
        layer = gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem())
        if layer == None:
            return
        features = layer.getFeatureStore().getFeatureSet()
        count = {}
        for f in features:
            try:
                ff = f.get(field)
            except:
                continue
            if ff in count.keys():
                count[ff] += 1
            else:
                count[ff] = 1
        #print "COUNT FOR ", field, " : ", count
        # jlist
        
        model = DefaultListModel()
        for i in sorted(count.keys()):
            model.addElement(i)
        self.lstValues.setModel(model)
        """
        # jtable
        dtm = DefaultTableModel()  #ount.keys(), count.values())
        for i in sorted(count.keys()):
            dtm.addRow([i, count[i]])
        self.tbmValues.setModel(tm)
        dtm.fireTableDataChanged()
        """
    
    def cmbLayers_change(self, *args):
        self._updateFields()
        self._updateAdvancedFilter()
    def cmbFields_change(self, *args):
        self._updateListValues()
    def lstValues_change(self, *args):
        self.process()

    def process(self):#btnProcess_click(self, *args):
        layer = gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem())
        store = layer.getFeatureStore()
        field = self.cmbFields.getSelectedItem()
        if field == "":
            # TODO: si el campo esta vacio devolver el query sin filtro
            #filter = DALLocator.getDataManager().createExpresion()
            return
        else:
            value = self.lstValues.getSelectedValue()
            store = layer.getFeatureStore()
            if isinstance(value, Number):
                expression = '%s = %s'%(field, value)
            else:
                expression = "%s = '%s'"%(field, value)
            filter = DALLocator.getDataManager().createExpresion(expression)
        fq = store.createFeatureQuery()
        fq.retrievesAllAttributes()
        fq.addAttributeName(field)
        fq.setFilter(filter)
        layer.setBaseQuery(fq)
        #port = gvsig.currentView().getMapContext().getViewPort()
        #port.refreshExtent()
        view = gvsig.currentView()
        #import pdb
        #pdb.set_trace()
        #gvsig.currentView().getMapContext().invalidate()
        gsv = self.view.getMapContext().getScaleView()
        self.view.getMapContext().setScaleView(gsv+1)
        self.view.getMapContext().setScaleView(gsv)
    
        
        #gvsig.currentView().getMapContext().getMapContextDrawer()
        #gvsig.currentView().getMapContext().getViewPort().refreshExtent()
        
def main(*args):
    l = Panel()
    l.showTool("Entities filter")
    pass