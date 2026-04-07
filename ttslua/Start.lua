function onLoad()
    btn_param = {
        click_function = 'action',
        function_owner = self,
        position = {0,0.25,0},
        width = 900,
        height = 450,
        font_size = 300,
        label = "Start",
    }
    self.createButton(btn_param)
    cube = getObjectFromGUID(Global.getTable("GUIDs")["Cube Bag"])
end

function action()
  if not Global.getVar("readyToStart") then
    broadcastToAll('Draft in progress')
    do return end
  end

  Global.setVar("handSize", 14)
  local players = Global.call('globalRealSeatedPlayers')

  if not Global.getVar("draftInProgress") then
    cube.setLock(true)
    cube.shuffle()
    cube.setInvisibleTo(getSeatedPlayers())
    cube.setPosition({0,-10,0})
    broadcastToAll('Starting Cube Draft: Round 1')

    --Notes.removeNotebookTab(0)
    for p in ipairs(players) do
      params = {
        title = players[p].steam_name ,
        body = players[p].steam_name .. '-#-' .. players[p].color ..'\n',
        color = players[p].color
      }
      Notes.addNotebookTab(params)
    end
    --Notes.addNotebookTab({title = 'Pack Record', body = '', color = 'Black'})
  else
    broadcastToAll('Round ' .. tostring(Global.getVar("rounds")))
  end
  for p in ipairs(players) do
    pack = {}
    for i = 1, 15 do
      card = cube.takeObject({position =getPlayerHandPosition(players[p]), index = 1})
      table.insert(pack, card.getName())
    end

    Global.call('globalNewPack', pack)
  end

  Global.setVar("rounds", Global.getVar("rounds") + 1)
  Global.setVar("draftInProgress", true)
  Global.setVar("readyToStart", false)
end
---------------------------

function getPlayerHandPosition(player)
    local hand = player.getPlayerHand()
    return {hand.pos_x, hand.pos_y, hand.pos_z}
end
