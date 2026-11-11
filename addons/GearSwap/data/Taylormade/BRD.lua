include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Kaja Knife",
	sub = "Homestead Dagger",
	range = "Blurred Harp +1",
	head = "Weatherspoon corona +1",
	--body = "Brioso justaucorps +1",
	body = "Inyanga jubbah +2",
	hands = "Brioso Cuffs",
	legs = "Inyanga Shalwar +2",
	feet = "Egbesu Clogs",
	neck = "Mnbw. Whistle +1",
	waist = "Gerdr Belt",
	left_ear = "Moonshade Earring",
	right_ear = "Alabaster Earring",
	left_ring = "Opal Ring",
	-- left_ring = "Stikini ring +1",
	right_ring = "Murky Ring",
	back = { name = "Mecisto. Mantle", augments = { "Cap. Point+38%", "MP+25", "Mag. Acc.+3", "DEF+3" } },
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
	-- left_ring = "Luzaf's Ring",
})

function get_sets()
	taylormade_common.setup()

	-- Registering your custom aliases
	windower.send_command(
		'alias war_buffs input /ja "Berserk" <me>; wait 2; input /ja "Aggressor" <me>; wait 2; input /ja "Hasso" <me>; wait 1; input /ja "Restraint" <me>; wait 1; input /ja "Blood Rage" <me>; wait 1; input /ja "Warcry" <me>'
	)
	windower.send_command('alias fell_cleave input /ja "Sekkanoki" <me>; wait 1.2; input /ws "Fell Cleave" <t>')

	-- Binding your physical hotkeys
	windower.send_command('bind ^` input /ma "Horde Lullaby II" <stnpc>')
	windower.send_command('bind !` input /ma "Carnage Elegy" <stnpc>')
	windower.send_command('bind !1 input /ja "Nightingale" <me>; wait 1.2; input /ja "Troubadour" <me>; echo [NiTro Fired]')
	windower.send_command('bind !2 input /ma "Valor Minuet IV"')
	windower.send_command('bind !3 input /ma "Valor Minuet V"')
	windower.send_command('bind !4 input /ma "Victory March"')
	windower.send_command('bind !5 input /ma "Advancing March"')
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind ^`")
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")

	windower.send_command("unalias war_buffs")
	windower.send_command("unalias fell_cleave")
end
