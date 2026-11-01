include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Joyeuse",
	sub = "Genbu's Shield",
	head = "Nashira Turban",
	body = "Nashira Manteel",
	hands = "Nashira Gages",
	legs = "Nashira Seraweels",
	feet = "Nashira Crackows",
	neck = "Stone Gorget",
	waist = "Swift Belt",
	left_ear = "Ethereal Earring",
	right_ear = "Loquac. Earring",
	left_ring = "Jelly Ring",
	right_ring = "Tamas Ring",
	back = "Merciful Cape",
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
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")
end
