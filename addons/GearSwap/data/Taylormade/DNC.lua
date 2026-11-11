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
	hands = "Olorun Gloves",
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
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()

	-- Binding your physical hotkeys
	windower.send_command("bind !` input /ra <stnpc>")
	-- windower.send_command("bind !` input /ja Provoke <stnpc>")
	windower.send_command('bind !3 input /ws "Dancing Edge"')
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !3")
end
