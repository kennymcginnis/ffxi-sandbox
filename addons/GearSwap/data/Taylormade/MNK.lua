include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead Cesti",
	range = "Mamoolbane",
	head = "Mummu Bonnet",
	body = "Olorun Harness",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Gerdr Belt",
	left_ear = "Hollow Earring",
	right_ear = "Brutal Earring",
	left_ring = "Rajas Ring",
	right_ring = "Jaeger Ring",
	back = "Bushido Cape",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

sets.precast = {}
sets.precast.WS = set_combine(sets.default, {
	back = "Alabaster Mantle",
})

function get_sets()
	taylormade_common.setup()

	-- Binding your physical hotkeys
	windower.send_command("bind ^` input /ra <stnpc>")
	windower.send_command("bind !` input /ja Provoke <stnpc>")

	windower.send_command("bind !2 gs c do_buffs") -- Alt+1 to Cycle Buffs
	windower.send_command("bind !3 gs c do_ws") --    Alt+2 to Boost + WS
end

function self_command(command)
	local player = windower.ffxi.get_player()

	-- Defensive & Offensive Long-Term Stances/Buffs Cycle
	if command == "do_buffs" then
		local buff_cycle = {
			"Focus",
			"Dodge",
			"Counterstance",
			"Footwork",
			-- "Mantra",
			-- "Formless Strikes",
			"Perfect Counter",
		}

		for _, ability in ipairs(buff_cycle) do
			if not buffactive[ability] and taylormade_common.ability_ready(ability) then
				send_command('input /ja "' .. ability .. '" <me>')
				return
			end
		end
		windower.add_to_chat(167, "*** All Monk buffs are active or on cooldown! ***")

	-- Boost + Conditional Footwork WS Macro
	elseif command == "do_ws" then
		if player.vitals.tp >= 1000 then
			local ws_name = buffactive.Footwork and "Dragon Kick" or "Asuran Fists"
			local ws_command = 'input /ws "' .. ws_name .. '" <t>'

			if taylormade_common.ability_ready("Boost") then
				send_command('input /ja "Boost" <me>; wait 1.2; ' .. ws_command)
			else
				send_command(ws_command)
			end
		else
			windower.add_to_chat(167, "*** Not enough TP to Weapon Skill! ***")
		end
	end
end

function precast(spell)
	if spell.type == "WeaponSkill" then
		equip(sets.precast.WS)
	end
end

function job_aftercast(spell)
	if spell.type == "WeaponSkill" then
		equip(sets.default)
	end
end

function file_unload()
	-- Clean up keybinds when changing jobs or unloading GearSwap
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
end
