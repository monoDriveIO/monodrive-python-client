ID_SIMULATOR_CONFIG = "SimulatorConfig_ID"
ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND = "REPLAY_ConfigureTrajectoryCommand_ID"
ID_REPLAY_CONFIGURE_SENSORS_COMMAND = "REPLAY_ConfigureSensorsCommand_ID"

HEADER_CONTROL = uint32(hex2dec('6d6f6e6f'))
HEADER_RESPONSE = dec2bin(hex2dec('6f6e6f6d'))
%The message prefix header for response messages from the server

fid = fopen('configurations/simulator.json','r','n','UTF-8')
config = fscanf(fid, '%s');
sim_config = jsondecode(config);

control_channel = tcpip(sim_config.server_ip, sim_config.server_port)
control_channel.OutputBufferSize = 10000000;
control_channel.ByteOrder = 'bigEndian';
control_channel.Terminator('')
fopen(control_channel);

configuration_msg = struct(...
            'type', ID_SIMULATOR_CONFIG,... 
            'message', config,...
            'reference', randi(1000));
     
data_length = uint32(length(jsonencode(configuration_msg)) + 8);
fwrite(control_channel,[HEADER_CONTROL, data_length], 'uint32')
msg_bytes = native2unicode(jsonencode(configuration_msg), 'UTF-8');
fwrite(control_channel, msg_bytes)
%pause(.1)

response_header = fscanf(control_channel, '%c', 4)
response_length = fscanf(control_channel, '%c', 4)
response_length = double(response_length(4))
response = fscanf(control_channel, '%c', response_length-8)

fid = fopen('configurations/trajectories/HighWayExitReplay.json','r','n','UTF-8')
config = fscanf(fid, '%s');

trajectory_msg = struct(...
            'type', ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND,... 
            'message', config,...
            'reference', randi(1000));
     
data_length = uint32(length(jsonencode(trajectory_msg)) + 8);
fwrite(control_channel,[HEADER_CONTROL, data_length], 'uint32')
msg_bytes = native2unicode(jsonencode(trajectory_msg), 'UTF-8');
fwrite(control_channel, msg_bytes)
%pause(.1)

response_header = fscanf(control_channel, '%c', 4)
response_length = fscanf(control_channel, '%c', 4)
response_length = double(response_length(4))
response = fscanf(control_channel, '%c', response_length-8)

fid = fopen('uut/gps_config.json','r','n','UTF-8')
config = fscanf(fid, '%s');

sensor_msg = struct(...
            'type', ID_REPLAY_CONFIGURE_SENSORS_COMMAND,... 
            'message', config,...
            'reference', randi(1000));
     
data_length = uint32(length(jsonencode(sensor_msg)) + 8);
fwrite(control_channel,[HEADER_CONTROL, data_length], 'uint32')
msg_bytes = native2unicode(jsonencode(sensor_msg), 'UTF-8');
fwrite(control_channel, msg_bytes)
%pause(.1)

response_header = fscanf(control_channel, '%c', 4)
response_length = fscanf(control_channel, '%c', 4)
response_length = double(response_length(4))
response = fscanf(control_channel, '%c', response_length-8)

fclose(control_channel);
delete(control_channel);
clear control_channel