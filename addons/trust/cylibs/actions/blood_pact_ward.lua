---------------------------
-- Action representing a Blood Pack: Ward
-- @class module
-- @name BloodPactWard

local JobAbilityCommand = require('cylibs/ui/input/chat/commands/job_ability')
local packets = require('packets')

local Action = require('cylibs/actions/action')
local BloodPactWard = setmetatable({}, {__index = Action })
BloodPactWard.__index = BloodPactWard

function BloodPactWard.new(x, y, z, blood_pact_name, target_index)
    local self = setmetatable(Action.new(x, y, z), BloodPactWard)
    self.blood_pact_name = blood_pact_name
    self.target_index = target_index or windower.ffxi.get_player().index
    return self
end

function BloodPactWard:can_perform()
    local recast_id = res.job_abilities:with('en', "Blood Pact: Ward").recast_id
    if windower.ffxi.get_ability_recasts()[recast_id] == 0 then
        return true
    end
    return false
end

function BloodPactWard:perform()
    local target = windower.ffxi.get_mob_by_index(self.target_index)
    if not target then
        self:complete(false)
        return
    end

    local battle_target = windower.ffxi.get_mob_by_target('bt')
    local player = windower.ffxi.get_player()
    if battle_target and (player.status ~= 1 or player.target_index ~= battle_target.index) then
        local packet = packets.new('outgoing', 0x01A)
        packet['Target'] = battle_target.id
        packet['Target Index'] = battle_target.index
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

    coroutine.sleep(5)

    self:complete(true)
end

function BloodPactWard:get_blood_pact_name()
    return self.blood_pact_name
end

function BloodPactWard:gettype()
    return "bloodpactwardaction"
end

function BloodPactWard:getrawdata()
    local res = {}

    res.bloodpactward = {}
    res.bloodpactward.x = self.x
    res.bloodpactward.y = self.y
    res.bloodpactward.z = self.z
    res.bloodpactward.blood_pact_name = self:get_blood_pact_name()

    return res
end

function BloodPactWard:getidentifier()
    return self.blood_pact_name
end

function BloodPactWard:copy()
    return BloodPactWard.new(self:get_position()[1], self:get_position()[2], self:get_position()[3], self:get_blood_pact_name())
end

function BloodPactWard:is_equal(action)
    if action == nil then return false end

    return self:gettype() == action:gettype() and self:get_blood_pact_name() == action:get_blood_pact_name()
end

function BloodPactWard:tostring()
    return self.blood_pact_name
end

return BloodPactWard