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
from javax.swing import JPanel

    
class FilterLayerPanel(FormPanel):
    def __init__(self):
        FormPanel.__init__(self, os.path.join(os.path.dirname(__file__), "filterdata.xml"))
        
        #self.setPreferredSize(300,300)
        self.nw = None
        self.view = gvsig.currentView()
        self.layer = self.view.getLayer(self.cmbLayers.getSelectedItem()).getFeatureStore()
        # Fill dialog
        layers = self.view.getLayers()
        self.cmbLayers.removeAllItems()
        for layer in layers:
           self.cmbLayers.addItem(layer.getName())
           
        self.valuesList = self.lstValues
        self.nw = None
        if self.layer!=None:
            store  = self.layer.getFeatureStore()
            if store != None: 
                self.nw = DALSwingLocator.getSwingManager().createQueryFilterExpresion(store)
                bl = BorderLayout()
                self.pnlFilter.setLayout(bl)
                self.pnlFilter.add(self.nw)

    def _updateAdvancedFilter(self):
        if self.nw == None:
            return
        self.nw.setFeatureStore(self.layer.getFeatureStore())
        
    def _updateFields(self):
        self.cmbFields.removeAllItems()
        self.cmbDuplicates.removeAllItems()
        if self.layer == None:
            return
        ft = self.layer.getFeatureStore().getDefaultFeatureType()
        ds = ft.getAttributeDescriptors()
        self.cmbFields.addItem("")
        self.cmbDuplicates.addItem("")
        for d in ds:
            self.cmbFields.addItem(str(d.getName())) 
            self.cmbDuplicates.addItem(str(d.getName()))

    def _getCountValues(self,comboField):
        #self.lstValues.getModel().removeAllElements()
        field = comboField.getSelectedItem()
        if field == None or field == "":
            return
        if self.layer == None:
            return
        features = self.layer.getFeatureStore().getFeatureSet()
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
        return count
        
    def _updateListValues(self):
        # LIST
        count = self._getCountValues(self.cmbFields)
        if count == None: return
        model = DefaultListModel()
        for i in sorted(count.keys()):
            model.addElement(i)
        self.valuesList.setModel(model)

        
    def _updateListDuplicates(self):
        # DUPLICATES TABLE
        count = self._getCountValues(self.cmbDuplicates)
        if count == None: return
        dict_list=[]
        for i,j in count.iteritems():
            dict_list.append ((i,j))
        sorted_list = sorted(dict_list,key=lambda x: x[1],reverse=True)
        tableModel = DefaultTableModel(sorted_list, ["Field", "Duplicates"])
        self.tblFilter.setModel(tableModel)

    def cmbLayers_change(self, *args):
        self.layer = gvsig.currentView().getLayer(self.cmbLayers.getSelectedItem())
        self._updateFields()
        self._updateAdvancedFilter()
        #self._updateListValues()
        
    def cmbFields_change(self, *args):
        self._updateListValues()
        
    def lstValues_change(self, *args):
        self.process("basicFilter")
        
    def btnAdvancedFilter_click(self,*args):
        self.process("advancedFilter")
        
    def cmbDuplicates_change(self,*args):
        self._updateListDuplicates()
        
    def process(self, filterType):#btnProcess_click(self, *args):
        store = self.layer.getFeatureStore()

        # TODO: si el campo esta vacio devolver el query sin filtro
        #filter = DALLocator.getDataManager().createExpresion()

        if filterType=="basicFilter":
            fq = store.createFeatureQuery()
            fq.retrievesAllAttributes()
            for field  in store.getDefaultFeatureType().getAttrNames():
                fq.addAttributeName(field)
            for value in self.valuesList.getSelectedValuesList():
                field = self.cmbFields.getSelectedItem()
                if field == "": return
                if isinstance(value, Number):
                    expression = '%s = %s'%(field, value)
                else:
                    expression = "%s = '%s'"%(field, value)
                expression = DALLocator.getDataManager().createExpresion(expression)
                fq.addFilter(expression)
            print fq.getFilter()
            from org.gvsig.tools.evaluator import Evaluator
            if isinstance(fq, Evaluator):
                self.layer.addBaseFilter(fq)
            else:
                self.layer.setBaseQuery(fq)
        elif filterType=="advancedFilter":
            expression = self.nw.getExpresion()
            fq = store.createFeatureQuery()
            fq.retrievesAllAttributes()
            for field  in store.getDefaultFeatureType().getAttrNames():
                fq.addAttributeName(field)
            fq.setFilter(expression)
            self.layer.setBaseQuery(fq)

        else:
            return

        #port = gvsig.currentView().getMapContext().getViewPort()
        #port.refreshExtent()
        #gvsig.currentView().getMapContext().invalidate()
        gsv = self.view.getMapContext().getScaleView()
        self.view.getMapContext().setScaleView(gsv+1)
        self.view.getMapContext().setScaleView(gsv)
    
        
        #gvsig.currentView().getMapContext().getMapContextDrawer()
        #gvsig.currentView().getMapContext().getViewPort().refreshExtent()
        
def main(*args):
    l = FilterLayerPanel()
    l.showTool("Filter Layer")
    pass