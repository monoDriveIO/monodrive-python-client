classdef monoDrive_control < matlab.System 
    % Untitled Add summary here
    %
    % This template includes the minimum set of functions required
    % to define a System object with discrete state.

    % Public, tunable properties

    properties
        ID_SIMULATOR_CONFIG = "SimulatorConfig_ID"
        ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND = "REPLAY_ConfigureTrajectoryCommand_ID"
        ID_REPLAY_CONFIGURE_SENSORS_COMMAND = "REPLAY_ConfigureSensorsCommand_ID"

        HEADER_CONTROL = uint32(hex2dec('6d6f6e6f'))
        HEADER_RESPONSE = dec2bin(hex2dec('6f6e6f6d'))
        sim_config_json = string
        sim_config = struct()
        control_channel = libpointer 
    end

    properties(DiscreteState)

    end

    % Pre-computed constants
    properties(Access = private)

        v_mod = libpointer 
        %vehicle = obj.v_mod.MatlabVehicle();
        vehicle = libpointer
        
    end

    methods
        function obj = monoDrive_controller(sim_config_path)
            fid = fopen(sim_config_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            obj.sim_config = jsondecode(config);
            obj.control_channel = tcpip(obj.sim_config.server_ip, obj.sim_config.server_port);
            obj.control_channel.OutputBufferSize = 10000000;
            obj.control_channel.ByteOrder = 'bigEndian';
            obj.control_channel.Terminator('');
            fclose(fid);
        end
        
        function connect(obj)
            fopen(obj.control_channel);
        end
    end
    methods(Access = protected)
        function setupImpl(obj)
            % Perform one-time calculations, such as computing constants
            coder.extrinsic('py.importlib.import_module')
            obj.v_mod = py.importlib.import_module('matlab_vehicle');
            v = obj.v_mod.MatlabVehicle();
            assignin('base','vehicle',v);
            obj.vehicle = v;
            
        end
        function dataout = getOutputDataTypeImpl(~)
            dataout = 'uint8';
        end
        function sizeout = getOutputSizeImpl(~)
            sizeout = [1 1];
        end
        function y = stepImpl(obj,u)
            % Implement algorithm. Calculate y as a function of input u and
            % discrete states.
            temp = obj.vehicle.get_number();
            y = uint8(py.bytes(temp)) + u;
        end

        function resetImpl(obj)
            % Initialize / reset discrete-state properties
        end
        
        function response = configure_simulator(obj)
            command = obj.ID_SIMULATOR_CONFIG;
            config = obj.sim_config_json;
            response = obj.configure(command, config);
        end
        
        function response = send_trajectory(obj, trajectory_path)
            command = obj.ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND;
            fid = fopen(trajectory_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            response = obj.configure(command, config);
            fclose(fid);
        end
        
        function response = config_sensor(obj, sensor_config_path)
            command = obj.ID_REPLAY_CONFIGURE_SENSORS_COMMAND;
            fid = fopen(sensor_config_path,'r','n','UTF-8');
            config = fscanf(fid, '%s');
            response = obj.configure(command, config);
            fclose(fid);
        end
        
        function response = send_message(obj, command, message)
            msg = struct(...
            'type', command,... 
            'message', message,...
            'reference', randi(1000));
     
            data_length = uint32(length(jsonencode(msg)) + 8);
            fwrite(obj.control_channel,[obj.HEADER_CONTROL, data_length], 'uint32')
            msg_bytes = native2unicode(jsonencode(configuration_msg), 'UTF-8');
            fwrite(obj.control_channel, msg_bytes)
            %pause(.1)

            response_header = fscanf(obj.control_channel, '%c', 4);
            response_length = fscanf(obj.control_channel, '%c', 4);
            response_length = double(response_length(4));
            response = fscanf(obj.control_channel, '%c', response_length-8);
        end
    end
end