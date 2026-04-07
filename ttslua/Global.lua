GUIDs = {["Rotate Right"] = 'e69660', ["Rotate Left"] = '17bafe', ["Cube Bag"] = '687d2b',
         ["Green Flip"] = '153b25', ["Blue Flip"] = 'ba77ba', ["Red Flip"] = '940fce', ["Purple Flip"] = '4ca315',
         ["Start Button"] = 'ef2df3', ["Spawn Token Button"] = 'ee63dd', ["Copy Button"] = '0a6af2',
         ["Token Zone"] = '665d59', ["Record Deck Zone"] = '1f0f34'}

function onLoad(script_state)
  --[[rewrite this: all loads are LOAD SAVE, no fresh save
    can also change global getters to just Global.getVar(), etc.
    merge globaldraftstarted, globaldraftinprogress (in start button)
  ]]
  flips = {getObjectFromGUID(GUIDs["Green Flip"]),
           getObjectFromGUID(GUIDs["Blue Flip"]),
           getObjectFromGUID(GUIDs["Red Flip"]),
           getObjectFromGUID(GUIDs["Purple Flip"])}

  if script_state == nil or script_state == '' then
    broadcastToAll("fresh save")
    packs = {}
    handSize = -5
    goingClockwise = true
    readyToStart = true
    rounds = 1
    draftInProgress = false
  else
    broadcastToAll("load save")
    local state = JSON.decode(script_state)
    packs = state.pp
    handSize = state.hs
    goingClockwise = state.gc
    readyToStart = state.rts
    rounds = state.rr
    draftInProgress = state.dip
    --return JSON.encode(state)
  end
end

function onSave()
  local state = {hs = handSize, gc = goingClockwise, rr = rounds, rts = readyToStart, dip = draftInProgress, pp = packs}
  return JSON.encode(state)
end

function globalResumeDraft(params)
  handSize = params[1]
  goingClockwise = params[2]
  rounds = params[3]
  --continue, address temp "pack"
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
  for idx, val in ipairs(flips) do
    val.flip()
  end

  local players = globalRealSeatedPlayers()

  if handSize == 0 then
    readyToStart = true
    if goingClockwise then
      goingClockwise = false
    else
      goingClockwise = true
    end
  else
    for player_index, player in ipairs(players) do
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
  handSize = handSize - 1
end

function globalLastCard()
  if handSize == 0 then
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
