-- bracket data is used to both store the positions that buttons and inputs
-- will appear as well as store data between saves. For each entries entry,
-- there is also a corresponding integer entry followed with "_c"
-- not initiated, but each entry also has a "win_count" and "player parameter"
bracket_data = {
    header = {
        patch_no = {label = "0.0", position = {6.85, .65, 3.7}},
        draft_no = {label = "1", position = {6.85, .65, 4.85}},
        date_no =  {label = "MM/DD/YYYY", position = {6.85, .65, 6.05}}
    },
    entries = {
        {name = "m1p1", label = "1st seed", position = {-5.93, .65, -6.29}},
        {name = "m1p2", label = "4th seed", position = {-5.93, .65, -5.13}},
        {name = "m2p1", label = "2nd seed", position = {-5.93, .65, -2.18}},
        {name = "m2p2", label = "3rd seed", position = {-5.93, .65, -1.03}},
        {name = "m3p1", label = "loser of ws1", position = {-5.93, .65, 5.86}},
        {name = "m3p2", label = "loser of ws2", position = {-5.93, .65, 7.06}},
        {name = "m4p1", label = "winner of ws1", position = {-0.25, .65, -4.24}},
        {name = "m4p2", label = "winner of ws2", position = {-0.25, .65, -3.05}},
        {name = "m5p1", label = "loser of wf", position = {-0.25, .65, 3.85}},
        {name = "m5p2", label = "winner of lsf", position = {-0.25, .65, 5.1}},
        {name = "m6p1", label = "winner of wf", position = {5.395, .65, -0.02}},
        {name = "m6p2", label = "winner of lf", position = {5.395, .65, 1.07}},
    }
}

-- Function Creation ------------------------------------------------

-- a function is created for each element in bracket_data's header and entries.
-- _G refers to the global table that can be used universally.
-- the argument standard (obj, color, input, stillEditing) is implicit from
-- any input or button function, which is where these globally set functions are called.
for _, val in ipairs(bracket_data.entries) do
    _G[val.name] = function(obj, color, input, stillEditing)
        updateBracket(val.name, input, "player")
    end
    local win_counter = val.name .. "_c"
    _G[win_counter] = function(obj, color, input, stillEditing)
        updateBracket(win_counter, input, "win_count")
    end
end

for key, val in pairs(bracket_data.header) do 
    _G[key] = function(obj, color, input, stillEditing)
        updateBracket(key, input, "heading")
    end
end
-- Function Creation ------------------------------------------------

-- saves bracket to script_state
function onSave()
    return JSON.encode(bracket_data)
end

-- on load, creates all buttons and inputs based on bracket_data or 
-- previous saved script_state.
function onLoad(script_state)
    if script_state ~= nil and script_state ~= "" then 
        bracket_data = JSON.decode(script_state)
    end
    for _, val in pairs(bracket_data.entries) do
        local input_param = {
            input_function = val.name,
            function_owner = self,
            label = val.label,
            position = val.position,
            width = 3150, height = 400, scale = {0.5,1,1},
            font_size = 250, 
            color = {0,0,0,0}, font_color = {0,0,0,99},
            alignment = 3 --center
        }
        if val.player then
            input_param.value = val.player
        end
        self.createInput(input_param)
    end
    for _, val in pairs(bracket_data.entries) do
        local win_counter = val.name .. "_c"
        local score_param = {
            input_function  = win_counter,
            input_param = win_counter,
            function_owner = self,
            position = {val.position[1]+2, val.position[2], val.position[3]},
            width = 500, height = 400, scale = {0.5,1,1},
            font_size = 250,
            color = {0,0,0,0}, font_color = {0,0,0,99},
            alignment = 3, -- center
            validation = 2, -- only ints
            value = 0
        }
        if val.win_count then
            score_param.value = val.win_count
        end
        self.createInput(score_param)

    end
    for key, val in pairs(bracket_data.header) do
        local data_param = {
            input_function = key,
            function_owner = self,
            label = val.label,
            position = val.position,
            width = 1550, height = 400, scale = {0.5,1,1},
            font_size = 250,
            color = {0,0,0,0}, font_color = {0,0,0,99},
            alignment = 3 --center
        }
        if val.data then
            data_param.value = val.data
        end
        self.createInput(data_param)
    end

    self.createButton({
        click_function = "record_decks",
        function_owner = self,
        position = {6.85, .65, 7.05},
        width = 1550,
        height = 400,
        font_size = 250,
        scale = {0.5,1,1},
        label = "Record Decks"
    })
    self.createButton({
        click_function = "finish_draft",
        function_owner = self,
        position = {5.2, .65, 7.05},
        width = 1375,
        height = 400,
        font_size = 250,
        scale = {0.5,1,1},
        label = "Finish Draft"
    })

end

--- TODO: Implement taking bracket data, player notebooks, deck records,
--- and pack records to give a JSON representation of the draft
function finish_draft()
    do return end
end
--- Records each deck object in the Record Deck Zone. Taken from previous
--- Record Button code.
function record_decks()
  local script_zone = getObjectFromGUID(Global.getTable("GUIDs")["Record Deck Zone"])
  local decks = script_zone.getObjects()
  local text = ""

  broadcastToAll(#decks)
  for i, deck in ipairs(decks) do
    local cards = deck.getObjects()
    text = text .. deck.getName() .. '\n'
    for j, card in pairs(cards) do
      text = text .. card.name .. '\n'
    end
    text = text .. '#413' .. '\n'
  end
  Notes.editNotebookTab({index = 1, body = text})
end

--- updates bracket_data to inputs
function updateBracket(name, input, type)
    if type == "heading" then
        bracket_data.header[name].data = input
    else
        for idx, val in ipairs(bracket_data.entries) do
            if val.name == name or val.name .. "_c" == name then
                if type == "player" then 
                    bracket_data.entries[idx].player = input
                elseif type == "win_count" then
                    bracket_data.entries[idx].win_count = input
                end
            end
        end
    end
end