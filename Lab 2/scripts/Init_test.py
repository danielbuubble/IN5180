import pyvisa

rm = pyvisa.ResourceManager()
rm.list_resources_info()

def exisiting_tool(lab_num,tool,soccet_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(soccet_num)+"::SOCKET")
    fung.read_termination = '\n'
    if(tool == "gpp"):
        pass 
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))

print("Lab 1:")
exisiting_tool(1,"mdo",3000) #oscilloscope
exisiting_tool(1,"mfg",1026) #function generator
exisiting_tool(1,"gdm",3001) #multi meter
exisiting_tool(1,"gpp",1026) #power supply

print("Lab 2:")
exisiting_tool(2,"mdo",3000) #oscilloscope
exisiting_tool(2,"mfg",1026) #function generator
exisiting_tool(2,"gdm",3001) #multi meter
exisiting_tool(2,"gpp",1026) #power supply

print("Lab 3:")
exisiting_tool(3,"mdo",3000) #oscilloscope
exisiting_tool(3,"mfg",1026) #function generator
exisiting_tool(3,"gdm",3001) #multi meter
exisiting_tool(3,"gpp",1026) #power supply

print("Lab 4:")
exisiting_tool(4,"mdo",3000) #oscilloscope
exisiting_tool(4,"mfg",1026) #function generator
exisiting_tool(4,"gdm",3001) #multi meter
exisiting_tool(4,"gpp",1026) #power supply

print("Lab 5:")
exisiting_tool(5,"mdo",3000) #oscilloscope
exisiting_tool(5,"mfg",1026) #function generator
exisiting_tool(5,"gdm",3001) #multi meter
#exisiting_tool(5,"gpp",1026) #power supply

print("Lab 6:")
exisiting_tool(6,"mdo",3000) #oscilloscope
exisiting_tool(6,"mfg",1026) #function generator
exisiting_tool(6,"gdm",3001) #multi meter
exisiting_tool(6,"gpp",1026) #power supply

