include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead Staff",
	range = "Matre Bell",
	head = "Weath. Corona +1",
	body = "SV Separates +1",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Arachne Obi",
	left_ear = "Alabaster Earring",
	right_ear = "Moldavite Earring",
	left_ring = "Warp Ring",
	right_ring = "Echad Ring",
	back = {
		name = "Mecisto. Mantle",
		augments = { "Cap. Point+38%", "MP+25", "Mag. Acc.+3", "DEF+3" },
	},
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

sets.resting = set_combine(sets.default, {
	head = "Orvail Corona +1",
	body = "Orvail Robe +1",
	feet = "Numerist Pumps",
	neck = "Rep. Silver Medal",
	waist = "Tarutaru Sash",
})

sets.learning = set_combine(sets.default, {
	hands = "Magus Bazubands",
})

function get_sets()
	taylormade_common.setup()

	windower.send_command('bind !` input /ma "Fire II" <stnpc>') -- Alt + 3
	windower.send_command('bind !1 input /ma "Aero II" <t>') -- Alt + 3
	windower.send_command('bind !2 input /ma "Blizzard II" <t>') -- Alt + 1
	windower.send_command('bind !3 input /ma "Thunder II" <t>') -- Alt + 2
	windower.send_command('bind !4 input /ma "Stone III" <t>') -- Alt + 5
	windower.send_command('bind !5 input /ma "Water II" <t>') -- Alt + 4
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")
end
