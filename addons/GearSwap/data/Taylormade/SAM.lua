include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Senkuto",
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

	-- Registering your custom aliases
	windower.send_command('alias sam_buffs input /ja "Berserk" <me>; wait 1; input /ja "Hasso" <me>;')
	-- input /ja "Aggressor" <me>; wait 1; input /ja "Blood Rage" <me>; wait 1; input /ja "Warcry" <me>; wait 2; input /ja "Restraint" <me>; wait 1;
	windower.send_command('alias tachi_gekko input /ja "Sekkanoki" <me>; wait 1.2; input /ws "Tachi: Gekko" <t>')

	-- Binding your physical hotkeys
	windower.send_command("bind ^` input /ra <stnpc>")
	windower.send_command("bind !` input /ja Provoke <stnpc>")
	windower.send_command("bind !1 sam_buffs")
	windower.send_command('bind !2 input /ja "Meditate" <me>')
	windower.send_command("bind !3 tachi_gekko")
	windower.send_command('bind !4 input /ja "Konzen-ittai"')
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind ^`")
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")

	windower.send_command("unalias sam_buffs")
	windower.send_command("unalias tachi_gekko")
end
