--take the cards in the SPAWN TOKEN ZONE
--create tokens by looking through a DECK placed in the scripting ZONE
--have a bag GUID from dragged bag

token_zone_GUID = 'dd5d59'
self_GUID = 'ee63dd'

function onload()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.25,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Button",

    }
    self.createButton(btn_param)
    token_zone = getObjectFromGUID(token_zone_GUID)
end

function update()
    if btn_param.label ~= self.getName() then
        btn_param.label = self.getName()
        self.clearButtons()
        self.createButton(btn_param)
    end
end

function action()
  stuff = token_zone.getObjects()
  for i in ipairs(stuff) do
    temp_obj = getObjectFromGUID(stuff[i].guid)
    if temp_obj.name == 'CardCustom' then
      spawn_token(temp_obj.getName())
    elseif temp_obj.name == 'Deck' then
      spawn_token(temp_obj.getObjects())
    end
  end
end
---------------------------
function spawn_token(deck)
  token_bag = getObjectFromGUID(getObjectFromGUID(self_GUID).getDescription())
  tokens = token_bag.getObjects()
  guids = {}
  if type(deck) == 'table' then
    for deck_i in ipairs(deck) do
      for tock_i in ipairs(tokens) do
        if tokens[tock_i].description == deck[deck_i].name then
          table.insert(guids, tokens[tock_i].guid)
        end
      end
    end
    for g in ipairs(guids) do
      taken = token_bag.takeObject({guid = guids[g]})
      replacement = taken.clone({position = {x = -85, y = 5, z = -25}})
      token_bag.putObject(replacement)
    end
  elseif type(deck) == 'string' then
    for tock_i in ipairs(tokens) do
      if tokens[tock_i].description == deck then
        table.insert(guids, tokens[tock_i].guid)
      end
    end
    for g in ipairs(guids) do
      taken = token_bag.takeObject({guid = guids[g]})
      replacement = taken.clone({position = {x = -85, y = 5, z = -25}})
      token_bag.putObject(replacement)
    end
  end
end
