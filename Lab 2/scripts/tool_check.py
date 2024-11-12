import pyvisa
import argparse

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

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(
        description="Setting a DC voltage with the power supply (gpp) and reading it with the digital multimeter(gdm)"
    )
    parser.add_argument("--slab_num", required=True, type=int, help="Lab space number between 1 and 6")
    parser.add_argument("--tool", required=True, type=str, help="Tools: gpp, gdm, mdo, mfg")
    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()
	
    if(args.tool == "mdo"):
        socket_num = 3000
    elif(args.tool == "gdm"):
        socket_num = 3001
    else:
        socket_num = 1026
	
    
    exisiting_tool(args.slab_num,args.tool,socket_num) 