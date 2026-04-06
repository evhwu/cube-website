bracket_entries = {
    {name = "m1p1", label = "1st seed", position = {-5.96, .65, -6.22}},
    {name = "m1p2", label = "4th seed", position = {-5.96, .65, -5.1}},
    {name = "m2p1", label = "2nd seed", position = {-5.96, .65, -2.25}},
    {name = "m2p1", label = "3rd seed", position = {-5.96, .65, -1.05}},
    {name = "m3p1", label = "loser of ws1", position = {-5.96, .65, 5.935}},
    {name = "m3p2", label = "loser of ws2", position = {-5.96, .65, 7.05}},
    {name = "m4p1", label = "winner of ws1", position = {-0.35, .65, -4.1}},
    {name = "m4p2", label = "winner of ws2", position = {-0.35, .65, -3.}},
    {name = "m5p1", label = "loser of wf", position = {-0.35, .65, 3.9}},
    {name = "m5p2", label = "winner of lsf", position = {-0.35, .65, 5.1}},
    {name = "m6p1", label = "winner of wf", position = {5.4, .65, -0.05}},
    {name = "m6p2", label = "winner of lf", position = {5.4, .65, 1.05}},
}

for idx, val in ipairs(bracket_entries) do
    _G[val.name] = function(obj, color, input, stillEditing)
        updateBracket(val.name, input, "player")
    end
    local win_counter = val.name .. "_c"
    _G[win_counter] = function(obj, color, input, stillEditing)
        updateBracket(win_counter, input, "win_count")
    end
end


function onLoad(script_state)
    broadcastToAll(script_state.. "C")
    if script_state == nil or script_state == "" then
        broadcastToAll("new save")
    else 
        broadcastToAll("load save")
        bracket_entries = JSON.decode(script_state)
    end
    for idx, val in pairs(bracket_entries) do
        local input_param = {
         function_owner = self,
         width = 3150,
         height = 400,
         font_size = 250,
         scale = {0.5,1,1},
         color = {0,0,0,0},
         font_color = {0,0,0,99},
         alignment = 3, --center
        }
        input_param.input_function = val.name
        input_param.label = val.label
        input_param.position = val.position
        if val.player then
            input_param.value = val.player
        end
        self.createInput(input_param)
    end
    for idx, val in pairs(bracket_entries) do
        local score_param = {
        function_owner = self,
        width = 500,
        height = 400,
        font_size = 250,
        value = 0,
        scale = {0.5,1,1},
        color = {0,0,0,0},
        font_color = {0,0,0,99},
        alignment = 3, -- center
        validation = 2 -- only ints
        }
        local win_counter = val.name .. "_c"
        score_param.input_function = win_counter
        score_param.position = {val.position[1]+2, val.position[2], val.position[3]}
        if val.win_count then
            score_param.value = val.win_count
        end
        self.createInput(score_param)

    end
end


function updateBracket(name, input, type)
    for idx, val in ipairs(bracket_entries) do
        if val.name == name or val.name .. "_c" == name then
            if type == "player" then 
                bracket_entries[idx].player = input
            elseif type == "win_count" then
                bracket_entries[idx].win_count = input
            end
        end
    end
    self.script_state = JSON.encode(bracket_entries)
end