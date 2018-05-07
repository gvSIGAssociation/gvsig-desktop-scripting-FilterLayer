# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel
import os
from javax.swing import DefaultListModel
#from org.gvsig.fmap.dal import DALLocator
from java.lang import Number
from javax.swing.table import DefaultTableModel
from java.awt import BorderLayout
from org.gvsig.app.gui.filter import FilterDialog
from org.gvsig.fmap.dal.swing import DALSwingLocator
from java.lang import Double
from javax.swing import JPanel
import sys
    
from gvsig import getResource
from org.gvsig.tools.evaluator import Evaluator
#
#  org.gvsig.tools.swing.api ListElement para crear objetos lista para gvSIG
#

from org.gvsig.tools.swing.api import ListElement

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

from paths.fixmapcontextinvalidate import fixMapcontextInvalidate

mapContextManager = None
iconTheme = None

from java.lang import String
from java.util import Date
  
class FilterLayerPanel(FormPanel):
    def __init__(self,view):
        FormPanel.__init__(self, getResource(__file__, "filterdata.xml"))
        
        #self.setPreferredSize(300,300)
        self.filterExpresionSwing = None
        self.view = view
        self.valuesList = self.lstValues
        self._updateUI()
        mapContext = self.view.getMapContext()
        #addUpdateToCListener("FilterDataTool",  mapContext, UpdateListener(self))
        
    def _updateUI(self):
        # Fill dialog
        layers = self.view.getLayers()
        self.cmbLayers.removeAllItems()
        
        for layer in layers:
           #print getIconFromLayer(layer)
           self.cmbLayers.addItem(ListElement(layer.getName(),layer))

        # Advanced dialog
        item = self.cmbLayers.getSelectedItem()
        
        #self.valuesList = self.lstValues
        if item != None and item.getValue()!=None:
            self.layer = item.getValue()
            if self.layer!=None:
                self._updateAdvancedFilter()

        # Duplicates table
        tableModel = DefaultTableModel(None, ["Field", "Count"])
        self.tblFilter.setModel(tableModel)

    def _updateAdvancedFilter(self):
        if self.filterExpresionSwing == None:
            store = self.layer.getFeatureStore()
            self.filterExpresionSwing = DALSwingLocator.getSwingManager().createQueryFilterExpresion(store)
            bl = BorderLayout()
            self.pnlFilter.setLayout(bl)
            self.pnlFilter.add(self.filterExpresionSwing)
        self.filterExpresionSwing.setFeatureStore(self.layer.getFeatureStore())
        
    def _updateFields(self):
        self.cmbFields.removeAllItems()
        self.cmbDuplicates.removeAllItems()
        if self.layer == None:
            return
       
        ft = self.layer.getFeatureStore().getDefaultFeatureType()
        ds = ft.getAttributeDescriptors()
        self.cmbFields.addItem(ListElement("",""))
        self.cmbDuplicates.addItem(ListElement("",""))
        for d in ds:
            self.cmbFields.addItem(ListElement(str(d.getName()),str(d.getName()))) 
            self.cmbDuplicates.addItem(ListElement(str(d.getName()),str(d.getName()))) 

    def _getCountValues(self,comboField):
        #self.lstValues.getModel().removeAllElements()
        field = comboField.getSelectedItem().getValue()
        if field in ("",None ):
            return
        if self.layer == None:
            return
        features = self.layer.getFeatureStore().getFeatureSet()
        count = {}
        for f in features:
            ff = f.get(field)
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
        tableModel = DefaultTableModel(sorted_list, ["Field", "Count"])
        self.tblFilter.setModel(tableModel)

    def cmbLayers_change(self, *args):
        #self.layer = self.view.getLayer(self.cmbLayers.getSelectedItem())
        self.layer = self.cmbLayers.getSelectedItem().getValue()
        self._updateFields()
        self._updateAdvancedFilter()
        #self._updateListValues()
    def btnCleanFilter_click(self, *args):
        bq = self.layer.getBaseQuery()
        self.layer.setBaseQuery(bq)
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

        # TODO: if field is empty, return all features filter

        if filterType=="basicFilter":
            fq = store.createFeatureQuery()
            fq.retrievesAllAttributes()
            ft = store.getDefaultFeatureType()
            for field  in ft.getAttrNames():
                fq.addAttributeName(field)
            for value in self.valuesList.getSelectedValuesList():
                field = self.cmbFields.getSelectedItem()
                if field == "": return
                des = store.getDefaultFeatureType().getAttributeDescriptor(field)
                
                expression = "%s = '%s'"%(field, value)
                goc = des.getObjectClass()
                #import pdb
                #pdb.set_trace()
                
                if goc is String:
                    expression = "%s = '%s'"%(field, value)
                elif goc is Double:
                    expression = "%s = %s"%(field, str(value))
                elif goc is Number:
                    expression = '%s = %s'%(field, str(value))
                elif goc is Date:
                    expression = "%s = DATE('%s')"%(field, str(value))
                else:
                    expression = "%s = %s"%(field, str(value))

                expression = ExpressionEvaluatorLocator.getManager().createEvaluator(expression)

                fq.addFilter(expression)
            if isinstance(fq, Evaluator):
                self.layer.addBaseFilter(fq)
            else:
                self.layer.setBaseQuery(fq)
        elif filterType=="advancedFilter":
            expression = self.filterExpresionSwing.getExpresion()
            fq = store.createFeatureQuery()
            fq.retrievesAllAttributes()
            for field  in store.getDefaultFeatureType().getAttrNames():
                fq.addAttributeName(field)
            fq.setFilter(expression)
            self.layer.setBaseQuery(fq)

        else:
            return
        #self.view.getWindowOfView()
        fixMapcontextInvalidate(self.view.getMapContext())

        
def main(*args):
    l = FilterLayerPanel(gvsig.currentView())
    l.showTool("Filter Layer")
    pass