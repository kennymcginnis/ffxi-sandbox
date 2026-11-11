include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead Lance",
	sub = "Pole Grip",
	range = "Lightning Bow +1",
	ammo = "Scorpion Arrow",
	head = "Ruwa Armet",
	body = "Ruwa Breastplate",
	hands = "Ruwa Gauntlets",
	legs = "Ruwa Hose",
	feet = "Ruwa Leggings",
	neck = "Gaudryi Necklace",
	waist = "Gerdr Belt",
	left_ear = "Brutal Earring",
	right_ear = "Alabaster Earring",
	left_ring = "Jaeger Ring",
	right_ring = "Rajas Ring",
	back = "Bushido Cape",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()

	windower.send_command("bind ^` input /ra <stnpc>")
	windower.send_command("bind !` input /ja Jump <stnpc>")
	windower.send_command("bind !1 war_buffs")
	windower.send_command('bind !2 input /ja "Meditate" <me>')
	windower.send_command('bind !3 input /ws "Penta Thrust" <t>')
end

function midcast(spell)
	if spell.skill == "Ninjutsu" and spell.element and spell.element ~= "None" then
		equip(sets.midcast.MagicBurst)
	end
end

function aftercast(spell)
	equip(sets.default)
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind ^`")
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")

	windower.send_command("unalias war_buffs")
	windower.send_command("unalias fell_cleave")
end
