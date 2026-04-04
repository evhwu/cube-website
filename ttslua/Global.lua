turnything_1_GUID = 'e69660' --right
turnything_2_GUID = '17bafe'
startbutton_GUID  = 'ef2df3'
flippy_1_GUID = '4ca315'
flippy_2_GUID = '940fce'
flippy_3_GUID = '153b25'
flippy_4_GUID = 'ba77ba'
cube_bag_GUID = '687d2b'
token_zone_GUID = 'dd5d59'
spawn_token_button_GUID = 'ee63dd'
copy_button_GUID = '0a6af2'
record_deck_zone_GUID = '1f0f34'

GUIDs = {["Rotate Right"] = 'e69660', ["Rotate Left"] = '17bafe', ["Cube Bag"] = '687d2b',
         ["Green Flip"] = '153b25', ["Blue Flip"] = 'ba77ba', ["Red Flip"] = '940fce', ["Purple Flip"] = '4ca315',
         ["Start Button"] = 'ef2df3', ["Spawn Token Button"] = 'ee63dd', ["Copy Button"] = '0a6af2',
         ["Token Zone"] = '665d59', ["Record Deck Zone"] = '1f0f34'}

function onLoad(script_state)
  packs = {}
  hand_size = -5
  goingClockwise = true
  readyToStart = true
  rounds = 1
  draftInProgress = false

  --turn into iteration
  turnything_1 = getObjectFromGUID(turnything_1_GUID)
  turnything_2 = getObjectFromGUID(turnything_2_GUID)
  startbutton = getObjectFromGUID(startbutton_GUID)
  flippy_1 = getObjectFromGUID(flippy_1_GUID)
  flippy_2 = getObjectFromGUID(flippy_2_GUID)
  flippy_3 = getObjectFromGUID(flippy_3_GUID)
  flippy_4 = getObjectFromGUID(flippy_4_GUID)

  if script_state == nil or script_state == '' then
    broadcastToAll("fresh save")
  else
    broadcastToAll("load save")
    local state = JSON.decode(script_state)
    packs = state.pp
    hand_size = state.hs
    goingClockwise = state.gc
    readyToStart = state.rts
    rounds = state.rr
    draftInProgress = state.dip
    return JSON.encode(state)
  end
end

function onSave()
  local state = {hs = hand_size, gc = goingClockwise, rr = rounds, rts = readyToStart, dip = draftInProgress, pp = packs}
  return JSON.encode(state)
end

function globalResumeDraft(params)
  hand_size = params[1]
  goingClockwise = params[2]
  rounds = params[3]
  --continue, address temp "pack"
end

function globalDraftInProgress()
  draftInProgress = true
end

function globalGetRounds()
  return rounds
end

function globalSetRounds(params)
  rounds = params[1]
end

function globalDraftStatus()
  return {hand_size, goingClockwise, readyToStart, draftInProgress}
end

function globalDraftStarted()
  readyToStart = false
end

function globalSetHandSize(params)
  hand_size = params[1]
end

function globalRealSeatedPlayers()
    local playerColors = getSeatedPlayers()
    local players = {}
    local newI = 1
    for i, playerColor in pairs(playerColors) do
        if Player[playerColor].getPlayerHand() ~= nil
        then
            players[newI] = Player[playerColor]
            newI = newI + 1
        end
    end
    return players
end

function findTabIndexByColor(color)
  local tabs = Notes.getNotebookTabs()
  for i, tab in pairs(tabs) do
    if tab.color == color then
      return tab
    end
  end
  print('yikers')
  return nil
end

function globalNewPack(params)
  local new_pack = params
  table.insert(packs, new_pack)

  local new_body = ''
  for i in ipairs(new_pack) do
    new_body = new_body .. new_pack[i] .. '\n'
  end
  new_body = new_body .. '#413\n'
  local temp_tab = findTabIndexByColor('Black')
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
  flippy_1.flip()
  flippy_2.flip()
  flippy_3.flip()
  flippy_4.flip()
  local players = globalRealSeatedPlayers()

  if hand_size == 0 then
    readyToStart = true
    if goingClockwise then
      goingClockwise = false
    else
      goingClockwise = true
    end
  else
    for player_index,player in ipairs(players) do
      local player_hand = transformHand(player.getHandObjects())
      local matching_pack = -1
      local super_break = false
      for pack_index, pack in ipairs(packs) do
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
      local missingIndex, missingCard = helperFindCard(packs[matching_pack], player_hand)
      table.remove(packs[matching_pack], missingIndex)

      local temp_tab = findTabIndexByColor(player.color)
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
  hand_size = hand_size - 1
end

function globalLastCard()
  if hand_size == 0 then
    local players = globalRealSeatedPlayers()
    for p in ipairs(players) do
      local temp_tab = findTabIndexByColor(players[p].color)
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
