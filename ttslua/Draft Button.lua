draft_stage = "Pre-Draft"

stage_to_label = {["Pre-Draft"] = "Start Draft & Deal"}


function onLoad(script_state)
    if script_state ~= nil and script_state ~= "" then 
        draft_stage = JSON.decode(script_state)
    end
    btn_param = {
        click_function = "action",
        function_owner = self,
        position = {0, 0.3, 0},
        width = 750,
        height = 500,
        font_size = 75,
        label = stage_to_label[draft_stage],
    }
    self.createButton(btn_param)
end

function onSave()
    return JSON.encode(draft_stage)
end


function action()
    if draft_stage == "Pre-Draft" then 
        start_draft()
        start_round()
    end
end

function start_draft()
    local cube = getObjectFromGUID(Global.getTable("GUIDs")["Cube Bag"])
    cube = setLock(true)
    cube.shuffle()
    cube.setInvisibleTo(getSeatedPlayers())
    cube.setPosition({0, -10, 0})
    broadcastToAll("Starting Cube Draft")

    for p in pairs(players) do
        Notes.addNotebookTab({
            title = players[p].steam_name ,
            body = players[p].steam_name .. '-#-' .. players[p].color ..'\n',
            color = players[p].color})
    end
end


function start_round()
end