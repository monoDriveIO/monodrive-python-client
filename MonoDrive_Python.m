
classdef MonoDrive_Python < matlab.System & matlab.system.mixin.Propagates
    % Untitled Add summary here
    %
    % This template includes the minimum set of functions required
    % to define a System object with discrete state.

    % Public, tunable properties
    properties

    end

    properties(DiscreteState)

    end

    % Pre-computed constants
    properties(Access = private)
        v_mod = libpointer 
        %vehicle = obj.v_mod.MatlabVehicle();
        vehicle = libpointer
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
    end
end
