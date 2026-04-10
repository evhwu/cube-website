GUIDs = {["Rotate Right"] = 'e69660', ["Rotate Left"] = '17bafe', ["Cube Bag"] = '687d2b',
         ["Green Flip"] = '153b25', ["Blue Flip"] = 'ba77ba', ["Red Flip"] = '940fce', ["Purple Flip"] = '4ca315',
         ["Start Button"] = 'ef2df3', ["Spawn Token Button"] = 'ee63dd', ["Copy Button"] = '0a6af2',
         ["Token Zone"] = 'dd5d59', ["Record Deck Zone"] = '1f0f34'}

draft_data = {
  packs = {},
  hand_size = -1,
  is_clockwise = true,
  ready_for_round = true, 
  round = 1,
  draft_in_progress = false
}
function onLoad(script_state)
  if script_state ~= nil or script_state ~= "" then
    broadcastToAll("load save")
    draft_data = JSON.decode(script_state)
    broadcastToAll(JSON.encode(draft_data))
  end
end

function onSave()
  return JSON.encode(draft_data)
end

function real_seated_players()
  local colors = getSeatedPlayers()
  local players = {}
  for _, c in pairs(colors) do
    if Player[c].getPlayerHand() ~= nil then
      table.insert(players, Player[c])
    end
  end
  return players
end

function get_note_tab(title)
  local tabs = Notes.getNotebookTabs()
  for _, tab  in pairs(tabs) do
    if tab.title == title then
      return tab
    end
  end
  broadcastToAll("Notebook tab w/ title " .. title " not found.")
  return nil
end


--move and rewrite to start, doesn't need to be in global
function globalNewPack(params)
  local new_pack = params
  table.insert(draft_data.packs, new_pack)

  local new_body = ''
  for i in ipairs(new_pack) do
    new_body = new_body .. new_pack[i] .. '\n'
  end
  new_body = new_body .. '#413\n'
  local temp_tab = get_note_tab('Pack Records')
  if temp_tab == nil then
    print('missing Black')
  else
    params = {
      index = temp_tab.index,
      body = temp_tab.body .. new_body
    }
    Notes.editNotebookTab(params)
  end
end


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

function helperFindCard(pack_cards, player_cards)
  for index, value in ipairs(pack_cards) do
    if not has_value(player_cards, value) then
      return index, value
    end
  end
  print('You fucked up somewhere Evan u stupid fuck this is the helper method to that one find card function')
  return 'ERROR'
end

function globalScanHandsPack()
  local flips = {"Green Flip", "Blue Flip", "Red Flip", "Purple Flip"}
  for _, val in ipairs(flips) do
    getObjectFromGUID(GUIDs[val]).flip()
  end

  local players = real_seated_players()

  if draft_data.hand_size == 0 then
    draft_data.ready_for_round = true
    draft_data.is_clockwise = not draft_data.is_clockwise
  else
    for player_index, player in ipairs(players) do
      local player_hand = transformHand(player.getHandObjects())
      local matching_pack = -1
      local super_break = false
      for pack_index, pack in ipairs(draft_data.packs) do
        for i, card in ipairs(pack) do
          if has_value(player_hand, card) then
            matching_pack = pack_index
            super_break = true
            break
          end
        end
        if super_break then
          break
        end
      end
      local missingIndex, missingCard = helperFindCard(draft_data.packs[matching_pack], player_hand)
      table.remove(draft_data.packs[matching_pack], missingIndex)

      local temp_tab = get_note_tab(player.steam_name)
      if temp_tab == nil then
        print('missing ' .. player.color)
      else
        params = {
          index = temp_tab.index,
          body = temp_tab.body .. missingCard .. '\n'
        }
        Notes.editNotebookTab(params)
      end
    end
  end
  draft_data.hand_size = draft_data.hand_size - 1
end

function globalLastCard()
  if draft_data.hand_size == 0 then
    local players = real_seated_players()
    for p, val in pairs(players) do
      local temp_tab = get_note_tab(val.steam_name)
      local newCard = players[p].getHandObjects()[1].getName()
      if newCard == nil or newCard == '' then
        newCard = 'MISSING'
      end
      if temp_tab == nil then
        print('missing ' .. players[p].color)
      else
        params = {
          index = temp_tab.index,
          body = temp_tab.body .. newCard  .. '\n'
        }
        Notes.editNotebookTab(params)
      end
    end
  end
end
