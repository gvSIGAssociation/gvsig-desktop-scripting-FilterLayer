# encoding: utf-8

import gvsig

def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass

def fixMapcontextInvalidate(mapContext):
    gsv = mapContext.getScaleView()
    mapContext.setScaleView(gsv+1)
    mapContext.setScaleView(gsv)