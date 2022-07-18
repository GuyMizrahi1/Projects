import rticonnextdds_connector as rti
from os import path as ospath
from time import sleep
from datetime import datetime, timedelta

filepath = ospath.dirname(ospath.realpath(__file__))

# The dashboard shall print the status of the whole system, therefore, it needs to subscribe from a few topics
connector = rti.Connector("MyParticipantLibrary::DashboardConnector",  filepath + "/DDS.xml")
input_DDSMic = connector.getInput("DashboardSub::DashReadMic")
temp_sensor1_input_DDS = connector.getInput("DashboardSub::DashReadTemp1")
temp_sensor2_input_DDS = connector.getInput("DashboardSub::DashReadTemp2")
input_DDSActuatorStatus = connector.getInput("DashboardSub::DashReadStatus")

# those variables would be relevant for next loop, that's why they were defined out of the while loop
actuator_status_list = []
all_sensor1_samples = []
all_sensor2_samples = []
sensor1_list = []
sensor2_list = []
last_calibration_time = ''

while True:
    sleep(5)
    # the samples of the last 5 seconds already have been used by the other parts of the system,
    # therefore, we used take(), and not read()
    input_DDSMic.take()
    temp_sensor1_input_DDS.take()
    temp_sensor2_input_DDS.take()
    input_DDSActuatorStatus.take()

    mic_message = ''
    for j in range(0, input_DDSMic.samples.getLength()):
        if input_DDSMic.infos.isValid(j):
            mic_message = input_DDSMic.samples.getString(j, "StringMember")

    # that temporary list, have to be clear for new samples that arrive
    all_sensor1_samples.clear()
    current_temp1 = 0
    for j in range(0, temp_sensor1_input_DDS.samples.getLength()):
        if temp_sensor1_input_DDS.infos.isValid(j):
            current_temp1 = temp_sensor1_input_DDS.samples.getNumber(j, "NumberMember")
            all_sensor1_samples.append(current_temp1)

    # that temporary list, have to be clear for new samples that arrive
    all_sensor2_samples.clear()
    current_temp2 = 0
    for j in range(0, temp_sensor2_input_DDS.samples.getLength()):
        if temp_sensor2_input_DDS.infos.isValid(j):
            current_temp2 = temp_sensor2_input_DDS.samples.getNumber(j, "NumberMember")
            all_sensor2_samples.append(current_temp2)

    # looking for an extreme temprature differences
    if len(all_sensor1_samples) > 0 and len(all_sensor2_samples) > 0:
        for i in range(0, min(len(all_sensor1_samples), len(all_sensor2_samples))):
            if abs(all_sensor1_samples[i] - all_sensor2_samples[i]) >= 7:
                sensor1_list.append(all_sensor1_samples[i])
                sensor2_list.append(all_sensor2_samples[i])
                if len(sensor1_list) > 10:
                    sensor1_list.pop(0)
                if len(sensor2_list) > 10:
                    sensor2_list.pop(0)

    # create the actuator statuses list
    actuator_message = ''
    for j in range(0, input_DDSActuatorStatus.samples.getLength()):
        if input_DDSActuatorStatus.infos.isValid(j):
            actuator_message = input_DDSActuatorStatus.samples.getString(j, "StringMember")
            actuator_status_list.append(actuator_message)
            # make sure the is no more than 10 statuses in the list, by add new status at the last position,
            # and delete from the first position (FIFO)
            if len(actuator_status_list) > 10:
                actuator_status_list.pop(0)

    # set the time pf last calibration by using the list we just have made,
    # and we know that the status update every second, that's why we subtract the seconds from the microphone
    # by the last position the "Degraded" status had shown
    position_of_calibration = 0
    for j in range(0, len(actuator_status_list)):
        if actuator_status_list[j] == "Degraded":
            position_of_calibration = j
    if position_of_calibration != 0:
        date_format_str = "%H:%M:%S"
        given_time = datetime.strptime(mic_message, date_format_str)
        last_calibration_time = given_time - timedelta(seconds=min(9, len(actuator_status_list)-1) - position_of_calibration)
        last_calibration_time = last_calibration_time.strftime("%H:%M:%S")

    print(f'Microphone: <{mic_message}>\n'
          f'Actuator: {actuator_status_list}\n'
          f'Thermometer 1:{sensor1_list}\n'
          f'Thermometer 2:{sensor2_list}\n'
          f'The last calibrations time: <{last_calibration_time}>')




