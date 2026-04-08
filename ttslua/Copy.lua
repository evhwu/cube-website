--[[ take the cards in the spawn token zone, copies it with
a watermark and renames it]]

function onLoad()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.3,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Copy",
    }
    self.createButton(btn_param)
end

function action()
  local token_zone_objects = getObjectFromGUID(Global.getTable("GUIDs")["Token Zone"]).getObjects()
  for idx in ipairs(token_zone_objects) do
    local temp_obj = getObjectFromGUID(token_zone_objects[idx].guid)
    if temp_obj.name == 'CardCustom' then
      copy_card(temp_obj)
    end
  end
end
---------------------------
function copy_card(card)
  local replacement = card.clone({position = {x = -93, y = 3, z = -12.5}})
  replacement.setDescription(replacement.getName())
  replacement.setName("Copy")
  replacement.addDecal({
    name             = "Copy",
    url              = "https://i.imgur.com/8R1SH8N.png",
    position         = {0, 0.5, 0},
    rotation         = {90, 90, 328},
    scale            = {2.5, 0.65, 1.25},
  })
end
