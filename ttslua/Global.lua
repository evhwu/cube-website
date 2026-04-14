GUIDs = {["Rotate Right"] = 'e69660', ["Rotate Left"] = '17bafe', ["Cube Bag"] = '687d2b',
         ["Green Flip"] = '153b25', ["Blue Flip"] = 'ba77ba', ["Red Flip"] = '940fce', ["Purple Flip"] = '4ca315',
         ["Start Button"] = 'ef2df3', ["Spawn Token Button"] = 'ee63dd', ["Copy Button"] = '0a6af2',
         ["Token Zone"] = 'dd5d59', ["Record Deck Zone"] = '1f0f34'}

function onLoad(script_state)
  if script_state ~= nil or script_state ~= "" then
    broadcastToAll("load save")
    --____= JSON.decode(script_state)
  end
end

--[[
function onSave()
  return JSON.encode(draft_data)
end
]]

function get_note_tab(params)
  local tabs = Notes.getNotebookTabs()
  for _, tab  in pairs(tabs) do
    if tab.title == params.title then
      return tab
    end
  end
  broadcastToAll("Notebook tab w/ title " .. title " not found.")
  return nil
end
