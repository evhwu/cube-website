--take the cards in the SPAWN TOKEN ZONE
--create tokens by looking through a DECK placed in the scripting ZONE
--have a bag GUID from dragged bag

token_zone_GUID = 'dd5d59'
self_GUID = '0a6af2'

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
      copy_card(temp_obj)
    end
  end
end
---------------------------
function copy_card(card)
  local replacement = card.clone({position = {x = -93, y = 3, z = -12.5}})
  replacement.setDescription(replacement.getName())
  replacement.setName( "Copy")
  replacement.addDecal({
    name             = "Copy",
    url              = "https://i.imgur.com/8R1SH8N.png",
    position         = {0, 0.5, 0},
    rotation         = {90, 90, 328},
    scale            = {2.5, 0.65, 1.25},
  })
end
