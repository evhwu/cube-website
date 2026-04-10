draft_stage = "Pre-Draft"

g_hand_size = -1
g_packs = {}
g_clockwise = false
stage_to_label = {["Pre-Draft"] = "Start Draft & Deal"}


function onLoad(script_state)
  if script_state ~= nil and script_state ~= "" then 
    draft_stage = JSON.decode(script_state)
  end
  btn_param = {
    click_function = "action",
    function_owner = self,
    position = {0, 0.3, 0},
    width = 750,
    height = 500,
    font_size = 75,
    label = stage_to_label[draft_stage],
  }
  self.createButton(btn_param)
  cube = getObjectFromGUID(Global.getTable("GUIDs")["Cube Bag"])
end

function onSave()
  return JSON.encode(draft_stage)
end

-- control ------------------------
function action()
  if draft_stage == "Pre-Draft" then 
    start_draft()
    start_round()
    change_stage("Mid-Round")
  elseif draft_stage == "Mid-Round" then 

  end
end

function change_stage(stage) 
  draft_stage = stage
  self.editButton({index = 0, label = "grande gonzales"} )
end

function update_label()

end

------------------------------------

-- Start.action
-- Start.slowDeal
-- Global.globalNewPack
-- Start.getPlayerHandPosition
-- begin draft ---------------------
function start_draft()
  broadcastToAll("Starting Cube Draft")
  -- Makes the cube bag uniteractable after draft has started
  cube.setLock(true)
  cube.shuffle()
  cube.setInvisibleTo(getSeatedPlayers())
  cube.setPosition({0, -10, 0})

  -- Creates a draft log for each seated player 
  local players = Global.call('real_seated_players')
  for p in pairs(players) do
    Notes.addNotebookTab({
      title = players[p].steam_name,
      body = players[p].steam_name .. '-#-' .. players[p].color ..'\n',
      color = players[p].color})
  end
end

-- deal -------------------------------
function start_round()
  broadcastToAll("Round XX IMPLMENET")
  local players = Global.call('real_seated_players')
  for p in pairs(players) do
    local pack = {}
    pack = slow_deal(pack, players[p])
    
    Wait.condition(
    function() write_pack(pack) end,
    function() return #pack == 15 end)
  end
end

function write_pack(pack)
  table.insert(g_packs, pack)

  local body = ""
  for _, val in ipairs(pack) do
    body = body .. val .. "\n"
  end
  body = body .. "#413\n"

  local temp_tab = Global.call("get_note_tab", {title="Pack Records"})
  if temp_tab ~= nil then
    Notes.editNotebookTab({index = temp_tab.index, body = temp_tab.body .. body})
  end
end

function slow_deal(pack, p)
  if #pack ~= 15 then
    Wait.frames(function()
      local hand = p.getPlayerHand()
      local hand_position = {hand.pos_x, hand.pos_y, hand.pos_z}
      local card = cube.takeObject({position = hand_position, index = 1})
      table.insert(pack, card.getName())
      pack = slow_deal(pack, p)
    end, 6)
  end
  return pack
end

-- rotate hands ----------------------------

function transformHand(hand)
  local stringed_hand = {}
  for idx in ipairs(hand) do
    table.insert(stringed_hand, hand[idx].getName())
  end
  return stringed_hand
end

function has_value(tabl, val)
  for index, value in ipairs(tabl) do
    if value == val then
      return true
    end
  end
  return false
end


function rotate_hands() 
  local players = Global.call("real_seated_players")
  local next_players = get_next_players(players)

  for idx, _ in ipairs(players) do 
    if #players[idx].getHandObjects() ~= g_hand_size then 
      broadcastToAll(players[idx].steam_name .. ' has ' .. #players[idx].getHandObjects().. ' cards')
      broadcastToAll('Players should have ' .. g_hand_size .. ' cards.')
      do return end
    end
  end
---------------globalScanHandsPack
--[[  local flips = {"Green Flip", "Blue Flip", "Red Flip", "Purple Flip"}
  for _, val in ipairs(flips) do
    getObjectFromGUID(GUIDs[val]).flip()
  end]]

  if g_hand_size == 0 then 
    g_clockwise = not g_clockwise
    --ready for round = true ?
  else 
    for idx, player in ipairs(players) do
      -- looks at all cards in player hand, first one to match in
      -- pack record has that record pack as 'matching_pack'
      -- recode, this is very horrendous
      local player_hand = transformHand(player.getHandObject())
      local matching_pack = -1
      local super_break = false
      for pack_index, pack in ipairs(g_packs) do
        for _, card in ipairs(pack) do
          if has_value (player_hand, card) then
            matching_pack = pack_index
            super_break = true 
            break
          end
        end
        if super_break then
          break
        end
      end
      local missingIndex, missingCard = helperFindCard()
    end
  end
------------------------------------
  for idx, player in ipairs(next_players) do
    local move_to_index = (idx == #players) and 1 or idx + 1
    local move_to_player = next_players[move_to_index]
    local hold = player.getHandObjects()
    local hand = move_to_player.getPlayerHand()
    for _, card in ipairs(hold) do
      card.setPosition({hand.pos_x, hand.pos_y, hand.pos_z})
      card.setRotation({hand.rot_x, hand.rot_y + 180, hand.rot_z})
    end
  end

  Wait.frames(function() Global.call('globalLastCard') end, 15)
end

function get_next_players(players)
  local next_players = {}
  local new_i = clockwise and #players or 1 
  local inc = clockwise and 1 or -1

  -- Copied from LUA docs... returns iterator in order of keys
  local function pairsByKeys(t, f)
    local a = {}
    for n in pairs(t) do table.insert(a, n) end
      table.sort(a, f)
      local i = 0      -- iterator variable
      local iter = function ()   -- iterator function
      i = i + 1
      if a[i] == nil then return nil
        else return a[i], t[a[i]]
      end
    end 
    return iter
  end

  local function player_angles()
    local angles = {}
    for _, p in pairs(players) do
      local hand = p.getPlayerHand()
      angles[math.atan2(hand.pos_z, hand.pos_x)] = p
    end
    return angles
  end

  for _, p in pairsByKeys(player_angles()) do
    next_players[new_i] = p
    new_i = new_i + inc
  end
  return next_players
end



