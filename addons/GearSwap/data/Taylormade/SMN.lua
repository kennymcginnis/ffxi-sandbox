include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Lehbrailg +2",
	head = "Weath. Corona +1",
	body = "SV Separates +1",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Tarutaru Sash",
	left_ear = "Moonshade Earring",
	right_ear = "Moldavite Earring",
	left_ring = "Stikini Ring +1",
	right_ring = "Murky Ring",
	back = "Conveyance cape",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()

	-- Binding your physical hotkeys
	windower.send_command("bind !` input /ma Dia <stnpc>")
	-- windower.send_command("bind !` input /ja Provoke <stnpc>")
	windower.send_command('bind !3 input /ws "Dancing Edge"')
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !3")
end
