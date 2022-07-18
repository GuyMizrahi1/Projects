from sys import path as syspath
import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep
import random

filepath = ospath.dirname(ospath.realpath(__file__))

# The sensor shall publish its current temprature, but needs to be aware of the actuator status,
# therefore, it is also a subscriber
connector = rti.Connector("MyParticipantLibrary::TempSensor2Connector", filepath + "/DDS.xml")
outputDDS = connector.getOutput("TemperatureSensor2Pub::TempSensor2Writer")
input_DDS = connector.getInput("TemperatureSensor2Sub::TempSensor2Reader")

while True:
    # read the status of the actuator
    status_input = input_DDS.read()
    numOfSamples = input_DDS.samples.getLength()
    for j in range(0, numOfSamples):
        if input_DDS.infos.isValid(j):
            # waiting for status "working"
            while input_DDS.samples.getString(j, "StringMember") == "Working":
                # modeling the temprature (25 +5/-5) by 20 deg + random number between 0 to 10
                randomNumb = random.randint(0, 10)
                temp = 20 + randomNumb
                outputDDS.instance.setNumber("NumberMember", temp)
                # The sensor shall publish its current temprature
                outputDDS.write()
                sleep(0.1)
                print(f'Current Temperature at sensor 2: {temp}')
