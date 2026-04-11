function onLoad()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.3,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Start",
    }
    self.createButton(btn_param)
    cube = getObjectFromGUID(Global.getTable("GUIDs")["Cube Bag"])
end

function action()
  if not Global.getTable("draft_data").ready_for_round then
    broadcastToAll('Draft in progress')
    do return end
  end

  local players = Global.call('real_seated_players')

  if not Global.getTable("draft_data").draft_in_progress then
    cube.setLock(true)
    cube.shuffle()
    cube.setInvisibleTo(getSeatedPlayers())
    cube.setPosition({0,-10,0})
    broadcastToAll('Starting Cube Draft: Round 1')

    --Notes.removeNotebookTab(0)
    for p in pairs(players) do
      params = {
        title = players[p].steam_name ,
        body = players[p].steam_name .. '-#-' .. players[p].color ..'\n',
        color = players[p].color
      }
      Notes.addNotebookTab(params)
    end
    --Notes.addNotebookTab({title = 'Pack Record', body = '', color = 'Black'})
  else
    broadcastToAll('Round ' .. tostring(Global.getTable("draft_data").round))
  end
  for p in ipairs(players) do
    local pack = {}
    -- packs not getting recorded in pack records

    pack = slowDeal(pack, players[p])

    Wait.condition(
    function()
      Global.call('globalNewPack', pack)
    end,
    function() 
      return #pack == 15
    end)
    
  end

  local temp_data = Global.getTable("draft_data")
  temp_data.round = temp_data.round + 1
  temp_data.draft_in_progress = true
  temp_data.ready_for_round = false
  temp_data.hand_size = 14
  Global.setTable("draft_data", temp_data)
end
---------------------------

function slowDeal(pack, p)
  if #pack ~= 15 then
    Wait.frames(function()
      local hand_transform = p.getHandTransform()
      hand_transform.rotation["y"] = hand_transform.rotation["y"] - 180
      card = cube.takeObject({position = hand_transform.position,
                              rotation = hand_transform.rotation,
                              index = 1})
      table.insert(pack, card.getName())
      pack = slowDeal(pack, p)
    end, 6)
  end
  return pack
end

function getPlayerHandPosition(player)
    local hand = player.getPlayerHand()
    return {hand.pos_x, hand.pos_y, hand.pos_z}
end
