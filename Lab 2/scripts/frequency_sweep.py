import pyvisa
import time

rm = pyvisa.ResourceManager()
rm.list_resources()

#Checking of tool is available
def exisiting_tool(lab_num,tool,soccet_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(soccet_num)+"::SOCKET")
    fung.read_termination = '\n'
    if(tool == "gpp"):
        pass 
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung
	
mfg = exisiting_tool(1,"mfg",1026)

mfg.write('source1:appl:sin 2KHZ,1,0')
mfg.write('source2:appl:sin 4KHZ,1,0')


# Frequency sweep operation:
# 1. Enable sweep
mfg.write('source1:sweep:state on')
# 2. Select waveform shape
mfg.write('source1:appl:sin 2KHZ,1,0')
# 3. Select sweep boundaries 
mfg.write('source1:frequency:start 1') #Start frequency = 1 Hz
mfg.write('source1:frequency:stop 10E+03') #End frequency = 10 kHz
# 4. Set frequency spacing
mfg.write('source1:sweep:spacing linear') # choose either linear or logarithmic
# 5. Choose sweep time
mfg.write('source1:sweep:time 10')
# 6. Select sweep trigger source 
mfg.write('source1:sweep:source manual')
# 7. Select the marker frequency
#mfg.query('source1:marker:frequency?') #This only checks what the marker frequency is.

#To trigger a sweep event do:
mfg.write('*TRG')