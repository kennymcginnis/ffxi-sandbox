include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Home. Claymore",
	sub = "Pole Grip",
	head = "Meghanada Visor",
	body = "Olorun Harness",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Gerdr Belt",
	left_ear = "Brutal Earring",
	right_ear = "Alabaster Earring",
	left_ring = "Rajas Ring",
	right_ring = "Jaeger Ring",
	back = { name = "Evasionist's Cape", augments = { "Enmity+1", '"Embolden"+12', '"Dbl.Atk."+3' } },
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()

	-- Binding your physical hotkeys
	windower.send_command("bind !` input /ja Provoke <stnpc>")
	windower.send_command('bind !1 input /ma "Flash" <stnpc>')
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
end
