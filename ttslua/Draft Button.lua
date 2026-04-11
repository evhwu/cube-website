draft_stage = "Pre-Draft"

g_round = 1
g_hand_size = -1
g_packs = {}
g_clockwise = false

num_cards = 15
num_rounds = 3


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
    label = "Draft Button"
  }
  self.createButton(btn_param)
  update_label()
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
    rotate_hands()
  elseif draft_stage == "Pre-Round" then
    start_round()
    change_stage("Mid-Round")
  end
  update_label()
end

function change_stage(stage) 
  draft_stage = stage
end

function update_label()
  local new_label = ""
  if draft_stage == "Pre-Draft" then
    new_label = "Start Draft & Deal"
  elseif draft_stage == "Mid-Round" then
    local direction = clockwise and "CW" or "CCW" 
    local pick = 15 - g_hand_size
    new_label = "Pack " .. g_round .. "\nPick " .. pick .. "\nPassing " .. direction
  elseif draft_stage == "Pre-Round" then
    new_label = "Start Round " .. g_round
  end
  self.editButton({index = 0, label = new_label })
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
  local players = get_ordered_players()
  for p in pairs(players) do
    Notes.addNotebookTab({
      title = players[p].steam_name,
      body = players[p].steam_name .. '-#-' .. players[p].color ..'\n',
      color = players[p].color})
  end
end

-- deal -------------------------------
function start_round()
  g_hand_size = 14
  broadcastToAll("Round " .. g_round)
  local players = get_ordered_players()
  for p in pairs(players) do
    local pack = {}
    pack = slow_deal(pack, players[p])
    
    Wait.condition(
    function() write_pack(pack) end,
    function() return #pack == 15 end)
  end

  -- increment round, DIP = true, R4R = false ?
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
      local hand_transform = p.getHandTransform()
      hand_transform.rotation["y"] = hand_transform.rotation["y"] - 180
      local card = cube.takeObject({position = hand_transform.position,
                                    rotation = hand_transform.rotation, index = 1})
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

function find_difference(pack_cards, player_cards)
  local set = {}
  for _, val in ipairs(player_cards) do
    set[val] = true
  end

  for idx, val in ipairs(pack_cards) do
    if not set[val] then
      return idx
    end
  end
  return nil
end



function rotate_hands() 
  local players = get_ordered_players()

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
    g_round = g_round + 1
    change_stage("Pre-Round")
    --ready for round = true ?
  else 
    for _, player in pairs(players) do
      local player_hand = transformHand(player.getHandObjects())
      for pack_idx, pack in ipairs(g_packs) do 
        if has_value(pack, player_hand[1]) then
          -- "pack" is the matching global pack to "player"'s hand
          local g_pack_missing_index = find_difference(pack, player_hand)
          local missingCard = table.remove(g_packs[pack_idx], g_pack_missing_index)
          -- idea - give each pack when dealt a key, [Noble Hierach]
          -- create a second list of packs with the same key 
          -- when you remove here, you add to the second list
          -- UI will display the last 3 entries in random order
          local temp_tab = Global.call("get_note_tab", {title = player.steam_name})
          if temp_tab == nil then
            print("missing " .. player.color)
          else 
            Notes.editNotebookTab({index = temp_tab.index,
                                   body = temp_tab.body .. missingCard .. "\n"})
          end
          ------------------
          break 
        end
      end
    end
  end
  g_hand_size = g_hand_size - 1
------------------------------------
  for idx, player in ipairs(players) do
    local move_to_index = (idx == #players) and 1 or idx + 1
    local move_to_player = players[move_to_index]
    local hold = player.getHandObjects()
    local hand = move_to_player.getPlayerHand()
    for _, card in ipairs(hold) do
      card.setPosition({hand.pos_x, hand.pos_y, hand.pos_z})
      card.setRotation({hand.rot_x, hand.rot_y + 180, hand.rot_z})
    end
  end

  Wait.frames(
    function()
      if g_hand_size == 0 then
        for idx, val in pairs(players) do
          local temp_tab = Global.call("get_note_tab", {title = val.steam_name})
          local card = players[idx].getHandObjects()[1].getName()
          Notes.editNotebookTab({index = temp_tab.index,
                                 body = temp_tab.body .. card .. "\n"})
        end
      end

    end, 10)
end

--function get_next_players(players)
function get_ordered_players()
  local colors = getSeatedPlayers()
  local players = {}
  for _, c in pairs(colors) do
    if Player[c].getPlayerHand() ~= nil then
      table.insert(players, Player[c])
    end
  end

  local ordered_players = {}
  local new_i = clockwise and #players or 1 
  local inc = clockwise and -1 or 1

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
    ordered_players[new_i] = p
    new_i = new_i + inc
  end
  return ordered_players
end



