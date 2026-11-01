include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Home. Labrys",
	sub = "Pole Grip",
	head = "Gorney Morion +1",
	body = "SV Separates +1",
	hands = "SV Gauntlets +1",
	legs = "Ruwa hose",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Gerdr Belt",
	left_ear = "Brutal Earring",
	right_ear = "Alabaster Earring",
	left_ring = "Rajas Ring",
	right_ring = "Jaeger Ring",
	back = "Mauler's mantle",
}

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
	windower.send_command("bind !` input /ja Provoke <stnpc>")
	windower.send_command("bind !1 war_buffs")
	windower.send_command('bind !2 input /ja "Meditate" <me>')
	windower.send_command("bind !3 fell_cleave")
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
