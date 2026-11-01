include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Kaja Knife",
	sub = "Homestead Dagger",
	range = "Chakram",
	head = "Mummu Bonnet",
	body = "Olorun Harness",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "Olorun boots",
	neck = "Sanctity necklace",
	waist = "Gerdr Belt",
	left_ear = "Brutal Earring",
	right_ear = "Alabaster Earring",
	left_ring = "Mummu Ring",
	right_ring = "Meghanada ring",
	back = { name = "Mecisto. Mantle", augments = { "Cap. Point+38%", "MP+25", "Mag. Acc.+3", "DEF+3" } },
}

sets.idle = set_combine(sets.default, {
	-- left_ring = "Shneddick Ring",
})

sets.precast = {}
sets.precast.WS = set_combine(sets.default, {
	back = "Alabaster Mantle",
})

function get_sets()
	taylormade_common.setup()

	-- Registering your custom aliases
	windower.send_command('alias thf_buffs input /ja "Haste Samba" <me>; wait 2; input /ja "Conspirator" <me>;')
	windower.send_command(
		'alias thf_sa_evis input /turnat; wait 0.5; input /ja "Sneak Attack" <me>; wait 1.0; input /ws "Evisceration" <t>'
	)
	windower.send_command(
		'alias thf_ta_evis input /turnat; wait 0.5; input /ja "Trick Attack" <me>; wait 1.0; input /ws "Evisceration" <t>'
	)
	windower.send_command(
		'alias bully_sata_evis input /ja "Bully" <t>; wait 1.2; input /turnat; wait 0.5; input /ja "Sneak Attack" <me>; wait 1.2; input /ja "Trick Attack" <me>; wait 1.2; input /ws "Evisceration" <t>'
	)

	-- Binding your physical hotkeys
	windower.send_command("bind !` input /ra <stnpc>")
	windower.send_command("bind !2 thf_buffs")
	windower.send_command("bind !3 thf_sa_evis")
	windower.send_command("bind !4 bully_sata_evis")
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
	-- Windower unbinds keys by passing the key name with no command string
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")

	-- Clear out your custom alias
	windower.send_command("unalias thf_sa_evis")
	windower.send_command("unalias thf_ta_evis")
end
