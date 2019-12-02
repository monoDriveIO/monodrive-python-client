classdef ExtendedBasicClass < BasicClass
    %UNTITLED4 Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        ExtendedValue {mustBeNumeric}
    end
    
    methods
        
      function r = multiplyBy(obj,n)
         r = [obj.Value] * n * n;
      end
      function r = addOne(obj,n)
          r = [obj.Value] + n + 2;
      end
      
    end
end

