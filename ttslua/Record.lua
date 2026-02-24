script_zone_GUID = '1f0f34'
function onload()
    -- Parameters that create the button
    btn_param = {
        -- I wouldn't recommend changing any of these values
        click_function = 'action',
        function_owner = self,
        position = {0,0.25,0},

        -- These are okay to change
        width = 900,
        height = 450,
        font_size = 300,
        label = "Button"
    }
    self.createButton(btn_param) -- create button
end

function update()
    if btn_param.label ~= self.getName() then
        btn_param.label = self.getName()
        self.clearButtons()
        self.createButton(btn_param)
    end
end

function action()
  script_zone = getObjectFromGUID(script_zone_GUID)
  decks = script_zone.getObjects()
  text = ''
  for i, deck in pairs(decks) do
    cards = deck.getObjects()
    text = text .. deck.getName() .. '\n'
    for j, card in pairs(cards) do
      text = text .. card.name .. '\n'
    end
    text = text .. '#413' .. '\n'
  end
  params = {
    title = 'Decklists',
    body = text,
    color = 'Black'
  }
  Notes.addNotebookTab(params)
end
