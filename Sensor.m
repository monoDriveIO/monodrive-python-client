classdef Sensor < matlab.System & matlab.system.mixin.Propagates
    % Untitled19 Add summary here
    %
    % This template includes the minimum set of functions required
    % to define a System object with discrete state.

    % Public, tunable properties
    properties

    end

    properties(DiscreteState)

    end

    % Pre-computed constants
    properties(Access = protected)
        ID_REPLAY_CONFIGURE_SENSORS_COMMAND = "REPLAY_ConfigureSensorsCommand_ID"
        HEADER_CONTROL = uint32(hex2dec('6d6f6e6f'))
        HEADER_RESPONSE = dec2bin(hex2dec('6f6e6f6d'))
        sim_config = struct
        control_channel = libpointer
    end

    methods(Access = protected)
        function setupImpl(obj, u)
            % Perform one-time calculations, such as computing constants
                        % Perform one-time calculations, such as computing constants
            sim_config_path = 'configurations/simulator.json';
            fid = fopen(sim_config_path,'r','n','UTF-8');
            sim_config_json = fscanf(fid, '%s');
            obj.sim_config = jsondecode(sim_config_json);
            obj.control_channel = tcpip(obj.sim_config.server_ip, obj.sim_config.server_port);
            obj.control_channel.OutputBufferSize = 10000;
            obj.control_channel.ByteOrder = 'bigEndian';
            obj.control_channel.Terminator('');
            fclose(fid);
            obj.connect()
            y = u
        end

        function y = stepImpl(obj,u)
            % Implement algorithm. Calculate y as a function of input u and
            % discrete states.
            y = u;
        end

        function resetImpl(obj)
            % Initialize / reset discrete-state properties
        end
       function connect(obj)
            fopen(obj.control_channel);
        end
        
        function response = config_sensor(obj, sensor_config_path)
            command = obj.ID_REPLAY_CONFIGURE_SENSORS_COMMAND;
            fid = fopen(sensor_config_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            response = obj.send_message(command, config);
            fclose(fid);
        end
        
        function response = send_message(obj, command, message)
            msg_decoded = jsondecode(message);
            msg = struct(...
            'type', command,... 
            'message', msg_decoded,...
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


