# LazyRolls roller blind plugin
#
# Author: ACE ace@imlazy.ru 
#
# v0.01 29.02.2020
# v0.02 30.02.2020 Fixed some errors in domoticz log file
# v0.03 30.02.2020 Fixed some more errors in domoticz log file
#
"""
<plugin key="LazyRolls" name="LazyRolls roller blinds" author="ACE" version="0.03" wikilink="http://imlazy.ru/rolls/domoticz.html" externallink="http://imlazy.ru/">
    <description>
        <h2>LazyRolls roller blinds plugin</h2><br/>
        <h3>Configuration</h3>
        Configuration options:
    </description>
    <params>
	<param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
    </params>
</plugin>
"""
import Domoticz

class BasePlugin:
    httpXml = None
    httpCmd = None
    GoTo = 0
    NextUpdate = 0

    def __init__(self):
        return

    def onStart(self):
        # Domoticz.Log("onStart called")
       	if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()
        
        if (len(Devices) == 0):
            Domoticz.Device(Name="LazyRoll", Unit=1, Type=244, Subtype=73, Switchtype=13, Image=3).Create()
            Domoticz.Log("Device created.")
        self.httpCmd = Domoticz.Connection(Name="LazyRollCmd", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
        self.httpXml = Domoticz.Connection(Name="LazyRollXml", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        #Domoticz.Log("onConnect called")
        if (Connection == self.httpCmd):
            sendData = { 'Verb' : 'GET',
                    'URL'  : '/set?pos='+str(self.GoTo),
                     'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                   'Connection': 'keep-alive', \
                                   'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                   'Host': Parameters["Address"]+":80", \
                                   'User-Agent':'Domoticz/1.0' }
                   }
            self.httpCmd.Send(sendData)
        if (Connection == self.httpXml):
            sendData = { 'Verb' : 'GET',
                    'URL'  : '/xml',
                     'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                   'Connection': 'keep-alive', \
                                   'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                   'Host': Parameters["Address"]+":80", \
                                   'User-Agent':'Domoticz/1.0' }
                   }
            self.httpXml.Send(sendData)

    def onMessage(self, Connection, Data):
        #Status = int(Data["Status"])
        if (Connection == self.httpCmd):
            Domoticz.Heartbeat(1);
            self.NextUpdate=1;

        if (Connection == self.httpXml):
            try:
                strData = Data["Data"].decode("utf-8", "ignore")
                #Domoticz.Log("onMessage Xml called")
                import xml.etree.ElementTree as ET
                root = ET.fromstring(strData)
                p_now = int(root.find("Position/Now").text)
                p_dst = int(root.find("Position/Dest").text)
                p_max = int(root.find("Position/Max").text)
                if (p_max == 0): p_max=100;
                percent = round(p_now*100/p_max)
                nVal = 2
                if (p_now <= 0): nVal = 0
                if (p_now >= p_max): nVal = 1
                for d in Devices:
                    Devices[d].Update(nVal, str(percent))
                #Domoticz.Log(str(percent))
                if (p_now == p_dst): 
                    Domoticz.Heartbeat(10);
                    self.NextUpdate=3;
                    #Domoticz.Log('30s')
                else:
                    Domoticz.Heartbeat(1);
                    self.NextUpdate=1;
                    #Domoticz.Log('1s')
            except:
                pass

        if (Connection.Connected()): Connection.Disconnect()

    def onCommand(self, Unit, Command, Level, Hue):
        #Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if (Command == "Set Level"): self.GoTo=Level
        if (Command == "Off"): self.GoTo=0
        if (Command == "On"): self.GoTo=100
        self.httpCmd.Connect()

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        #Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)
        return

    def onDisconnect(self, Connection):
        #Domoticz.Log("onDisconnect called")
        return

    def onHeartbeat(self):
        # Domoticz.Log("onHeartbeat called")
        if (self.NextUpdate > 0): self.NextUpdate=self.NextUpdate-1;
        if (self.NextUpdate == 0):
            NextUpdate=3;
            if (self.httpXml.Connected() or self.httpXml.Connecting()): 
                self.httpXml.Disconnect()
            else:
                self.httpXml.Connect()


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return