import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep
import time

filepath = ospath.dirname(ospath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::buttonConnector", filepath + "/DDS.xml")
outputDDS = connector.getOutput("button::buttonWriter")
stop_command = "Stop!"
start_command = "Start!"


def stopwatch(seconds, command):  # method is responsible for counting 5 sec and than send start command
    start = time.time()
    elapsed = 0
    while elapsed < seconds:
        elapsed = time.time() - start
    outputDDS.instance.setString("StringMember", start_command)
    outputDDS.write()
    print(f'Button Command: {start_command}')


outputDDS.instance.setString("StringMember", start_command)  # default is start
outputDDS.write()
print(f'Button Command: {start_command}')
sleep(20)  # A stop command shall be sent every 20 sec
while True:
    outputDDS.instance.setString("StringMember", stop_command)
    outputDDS.write()
    print(f'Button Command: {stop_command}')
    stopwatch(5, start_command)
    sleep(15)  # 5 + 15 = 20
