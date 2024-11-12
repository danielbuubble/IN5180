import pyvisa
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

def exisiting_tool(lab_num,tool,socket_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(socket_num)+"::SOCKET")
    fung.read_termination = '\n'
    if(tool == "gpp"):
        pass 
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung

if (__name__=="__main__"):