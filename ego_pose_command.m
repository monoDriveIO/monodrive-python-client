function result = ego_pose_command()
% [{'frame': [{'name': 'EgoVehicle_0',
%              'orientation': [-2.03e-05,
%                              -1.72e-05,
%                              0.719,
%                              0.694],
%              'position': [-8847.83,
%                           14146.69,
%                           11.72],
%              'tags': ['dynamic',
%                       'vehicle', 'ego'],
%              'velocity': [1.31, 0.042,
%                           14.85]}],
%   'game_time': 32920.484,
%   'time': 1549487213}]
name = "EgoVehicle";
position = [-8847.837890625, 14146.6982421875, 11.72198486328125];
velocity = [1.3106634616851807, 0.04288967326283455, 14.853866577148438];
tags = ["dynamic", "vehicle", "ego"];
orientation = [-2.0383697119541466e-05, -1.7237640349776484e-05, 0.7191743850708008, 0.6948296427726746];
game_time = 32920.484375;
time = 1549487213;

s = {struct("frame", {{struct('name', name, 'position', position, 'velocity',... 
            velocity, 'tags', tags, 'orientation', orientation)}},'game_time', game_time, 'time', time )};
%S.features = {S.features};
result = jsonencode(s);