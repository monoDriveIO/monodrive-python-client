function msg = to_json(command, message)
        %Convert the message contents to its JSON representation.
        %Returns:
        %    Dictionary with JSON.
        msg = struct(...
            'type', command,... 
            'message', message,...
            'reference', randi(1000))
end
 
  

