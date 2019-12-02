classdef BasicClass
   properties
      Value {mustBeNumeric}
      v_mod = py.importlib.import_module('matlab_vehicle');
   end
   methods
      function r = roundOff(obj)
         r = round([obj.Value],2);
      end
      function r = multiplyBy(obj,n)
         r = [obj.Value] * n;
      end
      function r = addOne(obj,n)
          r = [obj.Value] + n + 1;
      end
   end
end