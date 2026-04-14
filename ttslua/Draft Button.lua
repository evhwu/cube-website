draft_data =  {
  phase = "Pre-Draft", --Phase of draft, dictates click_function action
  round = 1, -- Current round
  hand_size = -1, -- # of cards that should be in hand before click_function mid-round
  remaining_packs = {}, -- All remaining cards in the round. Diminishes over time, per round.
  pick_order = {}, -- Order of taken cards. Will start to be displayed once a full go-around has occured.
  is_clockwise = false, -- Direction that players are passing

  -- below are essentially constants, but are implemented to support draft changes
  pack_size = 15, -- # of cards dealt in each pack
  max_rounds = 3, -- # of rounds until finished
  num_players = 4,
  snipping = true
}

function onLoad(script_state)
  if script_state ~= nil and script_state ~= "" then
    -- Todo: change to draft_data, onsave as well
    draft_data = JSON.decode(script_state)
  end
  local btn_param = {
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
  return JSON.encode(draft_data)
end


-- Control ----------------------------------------------------------

--- Controls what the click_function will do based on draft phase. 
--- Typical draft order with 3 rounds should be:
--- Pre-Draft -> Mid-Round (1) -> Pre-Round (2) -> Mid-Round(2) ->
--- Pre-Round (3) -> Mid-Round (3) -> Finished
function action()
  if draft_data.phase == "Pre-Draft" then 
    start_draft()
    start_round()
  elseif draft_data.phase == "Mid-Round" then 
    rotate_hands()
  elseif draft_data.phase == "Pre-Round" then
    start_round()
  end

  update_label()
end

--- Updates the label of the button based on draft_data
function update_label()
  local new_label = ""
  if draft_data.phase == "Pre-Draft" then
    new_label = "Start Draft & Deal"
  elseif draft_data.phase == "Mid-Round" then
    local direction = draft_data.is_clockwise and "CW" or "CCW" 
    local pick = draft_data.pack_size - draft_data.hand_size
    new_label = "Pack " .. draft_data.round .. "\nPick " ..
                 pick .. "\nPassing " .. direction
  elseif draft_data.phase == "Pre-Round" then
    new_label = "Start Round " .. draft_data.round
  elseif draft_data.phase == "Finished" then
    new_label = "Draft Finished"
  end
  self.editButton({index = 0, label = new_label})
end
-- Control ----------------------------------------------------------

-- Begin Draft ------------------------------------------------------

--- Called at start of draft
--- Makes cube uninteractable and makes a pick log for each seated player.
function start_draft()
  broadcastToAll("Starting Cube Draft")
  cube.setLock(true)
  cube.shuffle()
  cube.setInvisibleTo(getSeatedPlayers())
  cube.setPosition({0, -10, 0})

  local players = get_ordered_players()
  for pidx, _ in pairs(players) do
    Notes.addNotebookTab({
      title = players[pidx].steam_name,
      body = players[pidx].steam_name .. '-#-' .. players[pidx].color ..'\n',
      color = players[pidx].color})
  end
end
-- Begin Draft ------------------------------------------------------

-- Start Round ------------------------------------------------------

--- Starts each draft round. Deals a pack to each player, and records 
--- that pack as "remaining_packs". This is used to determine what
--- players pick in future turns.
function start_round()
  draft_data.hand_size = draft_data.pack_size - 1
  draft_data.pick_order = {}
  broadcastToAll("Round " .. draft_data.round)
  local players = get_ordered_players()
  for _, player in pairs(players) do
    local pack = {}
    local hand_transform = player.getHandTransform()
    hand_transform.rotation["y"] = hand_transform.rotation["y"] - 180
    pack = recursive_deal(pack, hand_transform)
 
    -- This waits until recursive_deal deals up to pack_size 
    -- before calling write_pack.
    Wait.condition(
    function() write_pack(pack, player.color) end,
    function() return #pack == draft_data.pack_size end)
  end
  draft_data.phase = "Mid-Round"
end

--- Helper function for start_round. Writes pack to be tracked
--- in remaining_packs for the round and permanently in "Pack Records" note
--- @param table of strings of card names
function write_pack(pack, player_color)
  -- remaining_packs and pick_order are set with the same key. Remaining_packs
  -- is used mainly to find which card was taken from a pack, while pick_order
  -- is used to record the pick order and display for players as round continues.
  draft_data.remaining_packs[pack[1]] = pack
  draft_data.pick_order[pack[1]] = {color = player_color, picks = {}}

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

--- Helper function for start_round. Deals a card one at a time
--- and calls itself after X frames. This is done because takeObject()
--- takes some frames to execute, and write_pack needs to execute after
--- all cards in the pack have been dealt.
--- @param pack table of strings which will be recursively added to
--- @param ht position of hand 
--- @return pack table of strings added to
function recursive_deal(pack, ht)
  if #pack ~= draft_data.pack_size then
    Wait.frames(function()
      local card = cube.takeObject({position = ht.position,
                                    rotation = ht.rotation,
                                    index = 1})
      table.insert(pack, card.getName())
      pack = recursive_deal(pack, ht)
    end, 5)
  end
  return pack
end
-- Start Round ------------------------------------------------------

-- Rotate Hands -----------------------------------------------------

--- Clicked once round has start and cards are dealt. Records the cards taken
--- by players in the Notebook. Passes either clockwise or counter_clockwise.
--- Once finished, sets phase to deal a new round.
function rotate_hands() 
  local players = get_ordered_players()

  -- If each player didn't take exactly one card, the function halts.
  for _, p in ipairs(players) do 
    if #p.getHandObjects() ~= draft_data.hand_size then 
      broadcastToAll(p.steam_name .. " has " .. #p.getHandObjects().. " cards")
      broadcastToAll("Players should have " .. draft_data.hand_size .. " cards.")
      do return end
    end
  end

  -- Turns each Active / Passed token back to the Active side.
  for key, val in pairs(Global.getTable("GUIDs")) do
    if string.find(key, "Flip") then
      getObjectFromGUID(val).flip()
    end
  end

  -- If hand_size is 0 (after pick), i.e. there's only 1 card for the players to
  -- take, that last click will change direction, move round up, and change draft
  -- phase based on round number. Recording cards is not necessary because the previous
  -- call of rotate_hands records the last pick automatically.
  if draft_data.hand_size == 0 then 
    draft_data.is_clockwise = not draft_data.is_clockwise
    draft_data.round = draft_data.round + 1
    if draft_data.round > draft_data.max_rounds then 
      draft_data.phase = "Finished"
    else
      draft_data.phase = "Pre-Round"
    end
  -- Otherwise, we check each player's hand object (pack) against the remaining_packs
  -- to see the missing card in each. The missing card is recorded in Notes and
  -- added to pick_order, to be displayed later in UI. Limitations explained below.
  else 
    for idx, player in ipairs(players) do
      local player_hand = {}
      for _, card in ipairs(player.getHandObjects()) do
        table.insert(player_hand, card.getName())
      end

      for pack_key, pack in pairs(draft_data.remaining_packs) do
        -- "pack" is the matching global pack to "player"'s hand
        if has_value(pack, player_hand[1]) then
          -- removes the "missing_card" (card taken from pack in previous pick)
          -- from remaining_packs, puts in pick_order with corresponding pack_key.
          -- then updates that pick_order with the color of the player that picked.
          local pack_missing_index = find_difference(pack, player_hand)
          local missing_card = table.remove(draft_data.remaining_packs[pack_key], pack_missing_index)
          table.insert(draft_data.pick_order[pack_key].picks, missing_card)
          local next_idx = (idx == #players) and 1 or idx+1
          draft_data.pick_order[pack_key].color = players[next_idx].color
          -- record to Notes
          local temp_tab = Global.call("get_note_tab", {title = player.steam_name})
          if temp_tab == nil then
            print("missing " .. player.color)
          else 
            Notes.editNotebookTab({index = temp_tab.index,
                                   body = temp_tab.body .. missing_card .. "\n"})
          end
          break 
        end
      end
    end
  end
  draft_data.hand_size = draft_data.hand_size - 1

  -- Passes all hand objects to the next player
  for idx, player in ipairs(players) do
    local next_idx = (idx == #players) and 1 or idx + 1
    local next_player = players[next_idx]
    local hold = player.getHandObjects()
    local hand = next_player.getPlayerHand()
    for _, card in ipairs(hold) do
      card.setPosition({hand.pos_x, hand.pos_y, hand.pos_z})
      card.setRotation({hand.rot_x, hand.rot_y + 180, hand.rot_z})
    end
  end

  --After passing: 
  Wait.frames(
    function()
      -- If the hand_size is 0 (i.e., 1 card left in pack after click), The
      -- last card is automatically recorded. This is due to the limitations 
      -- of the above function, which needs at least 1 object to be in the player's
      -- hand for it to be matched against remaining_packs.
      if draft_data.hand_size == 0 then
        for idx, val in pairs(players) do
          local temp_tab = Global.call("get_note_tab", {title = val.steam_name})
          local card = players[idx].getHandObjects()[1].getName()
          Notes.editNotebookTab({index = temp_tab.index,
                                 body = temp_tab.body .. card .. "\n"})
        end
      end
    end, 10)
  
  -- calls update_UI to show previously taken cards for next pick
  if draft_data.snipping then
    Wait.frames(function() update_UI() end, 15)
  end
end

--- helper function for rotate_hands, checks is a table has a value
--- @param tabl table to search in
--- @param val value to check for
--- @return whether or not tabl contains val
function has_value(tabl, val)
  for _, t_val in ipairs(tabl) do
    if t_val == val then
      return true
    end
  end
  return false
end

--- a helper function in rotate_hands to find the picked card
--- from player_cards (hand object) and pack_cards (remaining_packs).
--- uses set uniqueness as opposed to a nested loop for O(n)
--- @param pack_cards the table containing the cards that were previously 
--- in the pack. Should contain 1 more element than player_cards.
--- @param player_cards the table containing the cards that are currently in 
--- the player's hand.
--- @return first index in pack_cards that has an element not in player_cards
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

--- function that returns a list of Players that are ordered by 
--- the current direction of the draft and the angles of 
--- the player's hand zones.
--- @return table of players in passing order
function get_ordered_players()
  local colors = getSeatedPlayers()
  local players = {}
  for _, c in pairs(colors) do
    if Player[c].getPlayerHand() ~= nil then
      table.insert(players, Player[c])
    end
  end

  --- Copied from LUA docs... returns iterator in order of keys
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

  --- returns a key value pair mapping hand angle to Player. 
  --- Taken directly from Rotate Hands (Right) module on workshop.
  local function player_angles()
    local angles = {}
    for _, p in pairs(players) do
      local hand = p.getPlayerHand()
      angles[math.atan2(hand.pos_z, hand.pos_x)] = p
    end
    return angles
  end

  local ordered_players = {}
  local new_i = draft_data.is_clockwise and #players or 1 
  local inc = draft_data.is_clockwise and -1 or 1
  for _, p in pairsByKeys(player_angles()) do
    ordered_players[new_i] = p
    new_i = new_i + inc
  end
  return ordered_players
end

--- function that broadcasts to each player the cards taken from pack
--- since the last pick the player made.
function update_UI()
  --- Fisher-Yates shuffle
  local function fy_shuffle(t)
    math.randomseed(os.time())
    for i = #t, 2, -1 do
      local j = math.random(i)
        t[i], t[j] = t[j], t[i]
    end
  end

  -- runs after a full go - around (for 4 players, will start on pick 5)
  if draft_data.pack_size >= num_players + 1 + draft_data.hand_size then
    for _, val in pairs(draft_data.pick_order) do
      local last_picks = {}
      -- adds the cards taken from the time since the player last held the pack
      -- to a table, shuffles it, and broadcasts to that player 
      for i = 0, draft_data.num_players-2 do
        table.insert(last_picks, val.picks[#val.picks - i])
      end
      fy_shuffle(last_picks)
      for _, card in ipairs(last_picks) do
        broadcastToColor(card, val.color, Color.fromString(val.color))
      end
    end
  end
end 


