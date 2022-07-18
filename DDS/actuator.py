import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep

filepath = ospath.dirname(ospath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::ActuatorConnector", filepath + "/DDS.xml")
button_input_DDS = connector.getInput("ActuatorSub::ActuatorReadButton")
temp_sensor1_input_DDS = connector.getInput("ActuatorSub::ActuatorReadTemp1")
temp_sensor2_input_DDS = connector.getInput("ActuatorSub::ActuatorReadTemp2")
temp_sensor3_input_DDS = connector.getInput("ActuatorSub::ActuatorReadTemp3")
outputDDS = connector.getOutput("ActuatorPub::ActuatorStatusWriter")

status = 'Working'  # start point
outputDDS.instance.setString("StringMember", status)
outputDDS.write()  # "The actuator shall publish its current status upon change"
current_temp1 = 0
current_temp2 = 0
current_temp3 = 0
while True:

    button_input_DDS.take()  # take the whole batch
    for j in range(0, button_input_DDS.samples.getLength()):
        if button_input_DDS.infos.isValid(j):
            command = button_input_DDS.samples.getString(j, "StringMember")
            if command == 'Stop!':
                status = 'Stopped'
                scenario = 'Received A STOP Command'
                outputDDS.instance.setString("StringMember", status)
                outputDDS.write()  # "The actuator shall publish its current status upon change"
            elif command == 'Start!':
                status = 'Working'
                outputDDS.instance.setString("StringMember", status)
                outputDDS.write()  # "The actuator shall publish its current status upon change"

    temp_sensor1_input_DDS.read()  # take the whole batch
    for j in range(0, temp_sensor1_input_DDS.samples.getLength()):
        if temp_sensor1_input_DDS.infos.isValid(j):
            current_temp1 = temp_sensor1_input_DDS.samples.getNumber(j, "NumberMember")

    temp_sensor2_input_DDS.read()  # take the whole batch
    for j in range(0, temp_sensor2_input_DDS.samples.getLength()):
        if temp_sensor2_input_DDS.infos.isValid(j):
            current_temp2 = temp_sensor2_input_DDS.samples.getNumber(j, "NumberMember")

    temperature_diff = abs(current_temp1 - current_temp2)
    if temperature_diff >= 7 and status == 'Working':
        status = 'Degraded'
        outputDDS.instance.setString("StringMember", status)
        outputDDS.write()  # "The actuator shall publish its current status upon change"

    if temperature_diff < 7 and status == 'Degraded':
        status = 'Working'
        outputDDS.instance.setString("StringMember", status)
        outputDDS.write()  # "The actuator shall publish its current status upon change"

    temp_sensor3_input_DDS.take()  # take the whole batch
    for j in range(0, temp_sensor3_input_DDS.samples.getLength()):
        if temp_sensor3_input_DDS.infos.isValid(j):
            current_temp3 = temp_sensor3_input_DDS.samples.getNumber(j, "NumberMember")

    if status == 'Degraded':
        status = 'Stopped'
        outputDDS.instance.setString("StringMember", status)
        outputDDS.write()  # "The actuator shall publish its current status upon change"
        scenario = 'Calibration is needed'

    if status == 'Stopped':
        print(f'Reason for stopping: {scenario}')  # "Before waiting, the actuator shall print to a console the
        if scenario == 'Calibration is needed':  # reason for stopping"
            print(f'Difference measured: {temperature_diff}, Calibration Thermometer Measurement: {current_temp3}')
        sleep(0.5)  # calibration
        status = 'Working'
    print(f'Status: {status}')
    sleep(1)