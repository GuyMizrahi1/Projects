import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep
from datetime import datetime

filepath = ospath.dirname(ospath.realpath(__file__))

connector = rti.Connector("MyParticipantLibrary::MicrophoneConnector", filepath + "/DDS.xml")
outputDDS = connector.getOutput("Microphone::MicWriter")

while True:
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    outputDDS.instance.setString("StringMember", time)
    # The microphone shall publish its current time
    outputDDS.write()
    sleep(0.1)
    print(f'Current Time: {time}')
