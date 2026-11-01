---------------------------
-- Action representing a blood pact rage.
-- @class module
-- @name BloodPactRage

local JobAbilityCommand = require('cylibs/ui/input/chat/commands/job_ability')
local packets = require('packets')

local Action = require('cylibs/actions/action')
local BloodPactRage = setmetatable({}, {__index = Action })
BloodPactRage.__index = BloodPactRage

function BloodPactRage.new(x, y, z, blood_pact_name)
    local conditions = L{
        NotCondition.new(L{InMogHouseCondition.new()}),
        NotCondition.new(L{HasBuffsCondition.new(L{'sleep', 'petrification', 'charm', 'terror', 'amnesia','Invisible'}, 1)}, windower.ffxi.get_player().index),
    }

    local self = setmetatable(Action.new(x, y, z, nil, conditions), BloodPactRage)
    self.blood_pact_name = blood_pact_name
    return self
end

function BloodPactRage:can_perform()
    local recast_id = res.job_abilities:with('en', "Blood Pact: Rage").recast_id
    if windower.ffxi.get_ability_recasts()[recast_id] == 0 then
        return Action.can_perform(self)
    end
    return false
end

function BloodPactRage:perform()
    local target = windower.ffxi.get_mob_by_target("bt")
    if target then
        local player = windower.ffxi.get_player()
        if player.status ~= 1 or player.target_index ~= target.index then
            local packet = packets.new('outgoing', 0x01A)
            packet['Target'] = target.id
            packet['Target Index'] = target.index
            packet['Category'] = player.status == 1 and 0x0F or 0x02
            packet['Param'] = 0
            packet['X Offset'] = 0
            packet['Z Offset'] = 0
            packet['Y Offset'] = 0
            packets.inject(packet)
            coroutine.sleep(3)
        end

        local command = JobAbilityCommand.new(self.blood_pact_name, target.id)
        command:run(true)
    end

    coroutine.sleep(2)

    self:complete(true)
end

function BloodPactRage:get_blood_pact_name()
    return self.blood_pact_name
end

function BloodPactRage:gettype()
    return "bloodpactrageaction"
end

function BloodPactRage:getrawdata()
    local res = {}

    res.bloodpactrage = {}
    res.bloodpactrage.x = self.x
    res.bloodpactrage.y = self.y
    res.bloodpactrage.z = self.z
    res.bloodpactrage.command = self:get_command()

    return res
end

function BloodPactRage:getidentifier()
    return self.blood_pact_name
end

function BloodPactRage:copy()
    return BloodPactRage.new(self:get_position()[1], self:get_position()[2], self:get_position()[3], self:get_command())
end

function BloodPactRage:is_equal(action)
    if action == nil then return false end

    return self:gettype() == action:gettype() and self:get_blood_pact_name() == action:get_blood_pact_name()
end

function BloodPactRage:tostring()
    return "BloodPactRage command: %s":format(self.command)
end

return BloodPactRage