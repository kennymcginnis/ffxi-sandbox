include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead scythe",
	sub = "Pole Grip",
	range = "Mamoolbane",
	head = "Ruwa Armet",
	body = "Ruwa Breastplate",
	hands = "Ruwa Gauntlets",
	legs = "Ruwa Hose",
	feet = "Ruwa Leggings",
	neck = "Sanctity necklace",
	waist = "Swift Belt",
	left_ear = "Cassie Earring",
	right_ear = "Hollow Earring",
	left_ring = "Rajas Ring",
	right_ring = "Jaeger Ring",
	back = "Bushido Cape",
}

sets.midcast = {}
sets.midcast.MagicBurst = set_combine(sets.default, {
	head = "Ninja Hatsuburi",
	neck = "Sanctity necklace",
	left_ear = "Moldavite Earring",
	right_ear = "Phantom Earring",
})

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()

	-- Registering your custom aliases
	windower.send_command(
		'alias war_buffs input /ja "Berserk" <me>; wait 2; input /ja "Aggressor" <me>; wait 2; input /ja "Hasso" <me>; wait 1; input /ja "Restraint" <me>; wait 1; input /ja "Blood Rage" <me>; wait 1; input /ja "Warcry" <me>'
	)
	windower.send_command('alias fell_cleave input /ja "Sekkanoki" <me>; wait 1.2; input /ws "Fell Cleave" <t>')

	-- Binding your physical hotkeys
	windower.send_command("bind ^` input /ra <stnpc>")
	windower.send_command("bind !` input /ma Bio <stnpc>")
	windower.send_command("bind !1 war_buffs")
	windower.send_command('bind !2 input /ja "Meditate" <me>')
	windower.send_command("bind !3 fell_cleave")
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
