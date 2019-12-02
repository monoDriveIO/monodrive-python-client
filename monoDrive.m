classdef monoDrive < matlab.System & matlab.system.mixin.Propagates ...
        & matlab.system.mixin.CustomIcon
    % Example usage
    % mono = monoDrive('configurations/simulator.json')
    % mono.connect()
    % mono.configure_simulator()
    % mono.send_trajectory('configurations/trajectories/HighWayExitReplay.json')
    % mono.config_sensor('uut/gps_config.json')
    
    % This template includes the minimum set of functions required
    % to define a System object with discrete state.

    % Public, tunable properties

    properties

    end

    properties(DiscreteState)

    end

    % Pre-computed constants
    properties(Access = private)
        ID_SIMULATOR_CONFIG = "SimulatorConfig_ID"
        ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND = "REPLAY_ConfigureTrajectoryCommand_ID"
        ID_REPLAY_CONFIGURE_SENSORS_COMMAND = "REPLAY_ConfigureSensorsCommand_ID"

        HEADER_CONTROL = uint32(hex2dec('6d6f6e6f'))
        HEADER_RESPONSE = dec2bin(hex2dec('6f6e6f6d'))
        sim_config_json = string
        sim_config = struct()
        control_channel = libpointer
    end
        
    methods(Access = protected)
        function y = setupImpl(obj, u)
            % Perform one-time calculations, such as computing constants
            sim_config_path = 'configurations/simulator.json';
            fid = fopen(sim_config_path,'r','n','UTF-8');
            obj.sim_config_json = fscanf(fid, '%s');
            obj.sim_config = jsondecode(obj.sim_config_json);
            obj.control_channel = tcpip(obj.sim_config.server_ip, obj.sim_config.server_port);
            obj.control_channel.OutputBufferSize = 10000000;
            obj.control_channel.ByteOrder = 'bigEndian';
            obj.control_channel.Terminator('');
            fclose(fid);
            obj.connect()
            obj.configure_simulator()
            %obj.send_trajectory('configurations/trajectories/HighWayExitReplay.json')
            %obj.config_sensor('uut/gps_config.json')
            y =u
        end
        %function dataout = getOutputDataTypeImpl(~)
        %    dataout = 'float';
        %end
        %function sizeout = getOutputSizeImpl(~)
        %    sizeout = [1 1];
        %end
        function y = stepImpl(obj,u)
            % Implement algorithm. Calculate y as a function of input u and
            % discrete states.
            %temp = obj.vehicle.get_number();
            %y = uint8(py.bytes(temp)) + u;
            y = u
        end

        function resetImpl(obj)
            % Initialize / reset discrete-state properties
        end
        
        function icon = getIconImpl(obj)
            % Define icon for System block
            icon = mfilename("class"); % Use class name
            % icon = "My System"; % Example: text icon
            % icon = ["My","System"]; % Example: multi-line text icon
            % icon = matlab.system.display.Icon("myicon.jpg"); % Example: image file icon
        end
       function connect(obj)
            fopen(obj.control_channel);
        end
        
        function response = configure_simulator(obj)
            command = obj.ID_SIMULATOR_CONFIG;
            config = obj.sim_config;
            response = obj.send_message(command, config);
        end
        
        function response = send_trajectory(obj, trajectory_path)
            command = obj.ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND;
            fid = fopen(trajectory_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            response = obj.send_message(command, config);
            fclose(fid);
        end
        
        function response = config_sensor(obj, sensor_config_path)
            command = obj.ID_REPLAY_CONFIGURE_SENSORS_COMMAND;
            fid = fopen(sensor_config_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            response = obj.send_message(command, config);
            fclose(fid);
        end
        
        function response = send_message(obj, command, message)
            msg = struct(...
            'type', command,... 
            'message', message,...
            'reference', randi(1000));
     
            data_length = uint32(length(jsonencode(msg)) + 8);
            fwrite(obj.control_channel,[obj.HEADER_CONTROL, data_length], 'uint32')
            msg_bytes = native2unicode(jsonencode(msg), 'UTF-8');
            fwrite(obj.control_channel, msg_bytes)
            %pause(.1)

            response_header = fscanf(obj.control_channel, '%c', 4);
            response_length = fscanf(obj.control_channel, '%c', 4);
            response_length = double(response_length(4));
            response = fscanf(obj.control_channel, '%c', response_length-8);
        end
    end
end