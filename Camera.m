classdef Camera < Sensor & matlab.System & matlab.system.mixin.Propagates
    % Untitled19 Add summary here
    %
    % This template includes the minimum set of functions required
    % to define a System object with discrete state.

    % Public, tunable properties
    properties
        config = 'configurations/camera.json'
    end

    properties(DiscreteState)

    end

    % Pre-computed constants
    properties(Access = private)

    end

    methods(Access = protected)
        function setupImpl(obj, u)
            % Perform one-time calculations, such as computing constants
                        % Perform one-time calculations, such as computing constants
            obj.config_sensor(obj.config)
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
    end
end