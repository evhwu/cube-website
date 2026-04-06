--[[ take the cards in the spawn token zone, creates tokens
tagged in tagged token bag. The GUID of the token deck must be 
the same as the description of the Spawn Token Button]]

function onLoad()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.25,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Spawn Tokens",
    }
    self.createButton(btn_param)
    token_zone = getObjectFromGUID(Global.getTable("GUIDs")["Token Zone"])
end

--[[ click action for button. On click, will call spawn_token on all cards and deck
     in the token zone]]
function action()
  local token_zone_objects = token_zone.getObjects()
  for idx in ipairs(token_zone_objects) do
    local temp_obj = getObjectFromGUID(token_zone_objects[idx].guid)
    -- If object is a cube card - will also trigger on tokens and copies
    if temp_obj.name == 'CardCustom' then
      spawn_token(temp_obj.getName())
    -- If player places entire deck - assumes deck will be of cards
    elseif temp_obj.name == 'Deck' then
      spawn_token(temp_obj.getObjects())
    end
  end
end
--[[ takes input of string or table of card objects. 
]]
function spawn_token(input)
  local token_bag =  getObjectFromGUID(self.getDescription())
  local tokens = token_bag.getObjects()
  local matched_guids = {}
  -- if input is a table of objects (player's deck)
  if type(input) == 'table' then
    --looks through each card in deck and each card in token bag
    for deck_idx in ipairs(input) do
      for token_idx in ipairs(tokens) do
        if tokens[token_idx].description == input[deck_idx].name then
          table.insert(matched_guids, tokens[token_idx].guid)
        end
      end
    end
  elseif type(input) == 'string' then
    for token_idx in ipairs(tokens) do
      if tokens[token_idx].description == input then
        table.insert(matched_guids, tokens[token_idx].guid)
      end
    end
  end
  -- for each matched guid in tokens, take that token, clone it, and place it
  for guid_idx in ipairs(matched_guids) do
    local taken = token_bag.takeObject({guid = matched_guids[guid_idx]})
    local replacement = taken.clone({position = {x = -85, y = 5, z = -25}})
    token_bag.putObject(replacement)
  end
end
