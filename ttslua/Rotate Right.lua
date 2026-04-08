function onLoad()
    local button_parameters = {}
    button_parameters.click_function = "onClick_RotateHands"
    button_parameters.function_owner = self
    button_parameters.label = "Rotate\nHands\n(Right)"
    button_parameters.position = {0, 0.5, 0}
    button_parameters.width = 400
    button_parameters.height = 400
    button_parameters.font_size = 100
    self.createButton(button_parameters)
end

function onClick_RotateHands()
    local players = getRealSeatedPlayers()
    local playersCounterClockwise = playersCounterClockwise(players)

    if not Global.getVar("goingClockwise") then
      broadcastToAll('wrong button dumbass')
      do return end
    end

    for pidx in ipairs(players) do
      if #players[pidx].getHandObjects() ~= Global.getVar("handSize") then
        broadcastToAll(players[pidx].steam_name .. ' has ' .. #players[pidx].getHandObjects().. ' cards')
        broadcastToAll('Players should have ' .. Global.getVar("handSize") .. ' cards.')
        do return end
      end
    end

    Global.call('globalScanHandsPack')
    ----------------------------------------------
    for i, player in ipairs(playersCounterClockwise) do
        local moveToIndex = 1
        if i == #players
        then
            moveToIndex = 1
        else
            moveToIndex = i + 1
        end
        local moveToPlayer = playersCounterClockwise[moveToIndex]
        local hold = player.getHandObjects()
        hand = moveToPlayer.getPlayerHand()
        for i,card in ipairs(hold) do
            card.setPosition({hand.pos_x, hand.pos_y, hand.pos_z})
            card.setRotation({hand.rot_x, hand.rot_y+180, hand.rot_z})
        end
    end

    for i,obj in ipairs(getAllObjects()) do
        if obj.getVar('tobiiDraftTools_isReadyToken')
        then
            cur = obj.getRotation()
            obj.setRotation({cur.x,cur.y,180})
        end
    end
    --------------------------------------------------
    Wait.frames(function() Global.call('globalLastCard') end, 15)
end

-- getSeatedPlayers() doesn't return the actual Player objects.
-- This function will instead return the 'real' Player objects.
function getRealSeatedPlayers()
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

-- Returns a Table with player angles (in radians) as the keys
function playerAngles(players)
    local angles = {}
    for i, player in pairs(players) do
        angles[getPlayerAngle(player)] = player
    end
    return angles
end

function playersCounterClockwise(players)
    local newPlayers = {}
    local newI = 1
    for i, player in pairsByKeys(playerAngles(players)) do
        newPlayers[newI] = player
        newI = newI + 1
    end
    return newPlayers
end

function playersClockwise(players)
    local newPlayers = {}
    local newI = #players
    for i, player in pairsByKeys(playerAngles(players)) do
        newPlayers[newI] = player
        newI = newI - 1
    end
    return newPlayers
end

function getPlayerAngle(player)
    local hand = player.getPlayerHand()
    --print("DEBUG: Player color: " .. player.color)
    return math.atan2(hand.pos_z, hand.pos_x)
end

-- Copied from LUA docs... returns iterator in order of keys
function pairsByKeys (t, f)
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
