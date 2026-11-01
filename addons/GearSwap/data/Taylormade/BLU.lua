include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead Blade",
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
	back = "Cornflower Cape",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Stikini Ring +1",
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

	-- Step ` (From previous setup) - Buff up
	-- Alt + ` triggers the full buff chain.
	windower.send_command(
		'bind !` input /ma "Erratic Flutter" <me>; wait 5; input /ma "Battery Charge" <me>; wait 6.5; input /ma "Cocoon" <me>; wait 5.5; input /ma "Occultation" <me>; wait 6; input /ma "Zephyr Mantle" <me>;'
	)

	-- Step 1 - Gather the enemies / Emergency CC
	-- Alt + 1 casts Dream Flower to sleep targets if the pull goes south or you need to cluster them.
	windower.send_command('bind !1 input /ma "Dream Flower" <t>; input /echo --- EMERGENCY SLEEP DEPLOYED: Cluster and reposition! ---')

	-- Step 2 - Entomb (The Opener)
	-- Alt + 2 casts Entomb to deal Earth AoE damage and petrify the group for crowd control.
	windower.send_command('bind !2 input /ma "Entomb" <t>; input /echo --- OPENER: Casting Entomb [Petrify] ---')

	-- Step 3 - Spectral Floe (The Follow-up)
	-- Alt + 3 casts Spectral Floe for Ice AoE damage and its critical Terror lockdown effect.
	windower.send_command('bind !3 input /ma "Spectral Floe" <t>; input /echo --- LOCKDOWN: Casting Spectral Floe [Terror] ---')

	-- Step 4 - Finish and Repeat (The Cleanup Nukes)
	-- Alt + 4 sequences Subduction, Tenebral Crush, and Scouring Spate to clear out survivors.
	windower.send_command(
		'bind !4 input /ma "Subduction" <t>; wait 5; input /ma "Tenebral Crush" <t>; wait 6.5; input /ma "Scouring Spate" <t>; input /echo --- CLEANUP: Executing finishing nukes! ---'
	)
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")
end
