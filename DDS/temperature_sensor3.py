import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep
import random

filepath = ospath.dirname(ospath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::TempSensor3Connector", filepath + "/DDS.xml")
outputDDS = connector.getOutput("TemperatureSensor3::TempSensor3Writer")

while True:
    randomNumb = random.randint(0, 2)
    temp = str(24 + randomNumb)  # creating a random temperature string
    outputDDS.instance.setString("NumberMember", temp)
    outputDDS.write()
    print(f'Current Temperature at sensor 3: {temp}')
    sleep(1)  # send every 1 seconds