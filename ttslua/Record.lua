-- Records each deck in record deck zone to decklist note

function onLoad()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.25,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Record"
    }
    self.createButton(btn_param)
end

function action()
  local decks = getObjectFromGUID(Global.getTable("GUIDs")["Record Deck Zone"])
  local text = ''

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
