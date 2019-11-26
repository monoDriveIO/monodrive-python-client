function result = monodrive_test()

    pe = pyenv;
    if pe.Status == 'Loaded'
        disp("To change the Python version, restart MATLAB, then call pyenv('Version','3.5').")
    else
        pyenv('Version','3.5');
    end

    mod = py.importlib.import_module('mmm');
    mod = py.importlib.reload(mod);

    result = mod.test_func.feval;