pe = pyenv; %('Version', 'c:\users\celit\AppData\Local\Python\Python35\python.exe');
%pe = pyenv('Version', 'C:\Users\celit\Anaconda3\envs\python_client_env\python.exe');
if pe.Status == 'Loaded'
    disp("To change the Python version, restart MATLAB, then call pyenv('Version', '3.7')")
else
    pyenv('Version','3.7');
end
for scenario = 1:100
    v_mod = py.importlib.import_module('matlab_vehicle');
    v_mod = py.importlib.reload(v_mod);

    vehicle = v_mod.MatlabVehicle();
    vehicle.start_simulator();
    vehicle.send_sensor_configuration();
    vehicle.start_sensor_listening();
    for n = 1:100
        vehicle.step();
        cam = uint8(py.bytes(vehicle.get_camera()));
        r = cam(3:4:end);
        redChannel = reshape(r, [512,512])';
        g = cam(2:4:end);
        greenChannel = reshape(g, [512,512])';
        b = cam(1:4:end);
        blueChannel = reshape(b, [512,512])';
        rgbImage = cat(3, redChannel, greenChannel, blueChannel);
        imshow(rgbImage);
    end
    vehicle.stop()
end