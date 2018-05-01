# encoding: utf-8

import gvsig

def main(*args):

    field = "MAPA"
    des = gvsig.currentLayer().getFeatureStore().getDefaultFeatureType().getAttributeDescriptor(field) 
    print des.getObjectClass(), des.getSubtype()
