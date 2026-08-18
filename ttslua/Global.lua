GUIDs = {["Rotate Right"] = 'e69660', ["Rotate Left"] = '17bafe', ["Cube Bag"] = '687d2b',
         ["Green Flip"] = '153b25', ["Blue Flip"] = 'ba77ba', ["Red Flip"] = '940fce', ["Purple Flip"] = '4ca315',
         ["Draft Button"] = '4d7c8c', ["Spawn Token Button"] = 'ee63dd', ["Copy Button"] = '0a6af2',
         ["Token Zone"] = 'dd5d59', ["Record Deck Zone"] = '1f0f34',
         ["Green Companion Zone"] = '0c9c94', ["Blue Companion Zone"] = '3cc265',
         ["Red Companion Zone"] = 'ba44ab', ["Purple Companion Zone"] = '521e66'}

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
