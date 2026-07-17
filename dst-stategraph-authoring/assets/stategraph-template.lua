local StateGraph = GLOBAL.StateGraph
local State = GLOBAL.State
local EventHandler = GLOBAL.EventHandler
local TimeEvent = GLOBAL.TimeEvent
local FRAMES = GLOBAL.FRAMES

local states =
{
    State
    {
        name = 'idle',
        tags = { 'idle', 'canrotate' },

        onenter = function(inst)
            inst.Physics:Stop()
            inst.AnimState:PlayAnimation('idle', true)
        end,
    },

    State
    {
        name = 'act',
        tags = { 'busy' },

        onenter = function(inst)
            inst.Physics:Stop()
            inst.AnimState:PlayAnimation('act')
        end,

        timeline =
        {
            TimeEvent(6 * FRAMES, function(inst)
                inst:PerformBufferedAction()
            end),
        },

        events =
        {
            EventHandler('animover', function(inst)
                inst.sg:GoToState('idle')
            end),
        },

        onexit = function(inst)
            if inst:GetBufferedAction() ~= nil then
                inst:ClearBufferedAction()
            end
        end,
    },
}

local events =
{
    EventHandler('doaction', function(inst)
        if not inst.sg:HasStateTag('busy') then
            inst.sg:GoToState('act')
        end
    end),
}

return StateGraph('mod_entity', states, events, 'idle')

