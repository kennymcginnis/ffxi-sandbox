include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Homestead Staff",
	sub = "Tokko Grip",
	ammo = "Memoria Sachet",
	head = "Weath. Corona +1",
	body = "SV Separates +1",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Rep. Silver Medal",
	waist = "Tarutaru Sash",
	left_ear = "Moonshade Earring",
	right_ear = "Moldavite Earring",
	left_ring = "Murky Ring",
	right_ring = "Shneddick Ring",
	back = "Peace Cape",
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

	-- Stance Switches
	windower.send_command('bind !l input /ja "Light Arts" <me>') -- Alt + L (Switch to Light Arts)
	windower.send_command('bind !d input /ja "Dark Arts" <me>') -- Alt + D (Switch to Dark Arts)

	-- Addendums (Requires an active Arts stance first)
	windower.send_command('bind @w input /ja "Addendum: White" <me>') -- Windows + W (Unlocks high-tier White Magic)
	windower.send_command('bind @b input /ja "Addendum: Black" <me>') -- Windows + B (Unlocks high-tier Black Magic)

	-- The Ultimate Party Regen (Light Arts)
	windower.send_command('bind ^1 input /ja "Perpetuance" <me>; wait 1.2; input /ja "Accession" <me>; wait 1.2; input /ma "Regen IV" <t>') -- Ctrl + 1

	-- Party-Wide Stoneskin (Light Arts + Addendum: White)
	windower.send_command('bind ^2 input /ja "Accession" <me>; wait 1.2; input /ma "Stoneskin" <me>') -- Ctrl + 2

	-- MP Engine Management
	windower.send_command('bind !s input /ja "Sublimation" <me>') -- Alt + S (Toggle to charge / complete Sublimation)

	-- Complete Solo Detonation (Wind) Skillchain on one button
	windower.send_command(
		'bind !6 input /ja "Immanence" <me>; wait 1.2; input /ma "Stone" <t>; wait 4.5; input /ja "Immanence" <me>; wait 1.2; input /ma "Aero" <t>'
	) -- Alt + 6

	-- The "Iroha Setup" Opener (Immanence + Fire)
	-- This creates Liquefaction. Iroha will jump in to close Fusion or Distortion.
	windower.send_command('bind !7 input /ja "Immanence" <me>; wait 1.2; input /ma "Fire" <t>') -- Alt + 7
	windower.send_command('bind !3 input /ja "Immanence" <me>; wait 1.2; input /ma "Water" <t>')

	-- Your Blizzard Burst / Closer (Immanence + Blizzard)
	-- Use this if Iroha opens Distortion, or use it to close Induration on your own.
	windower.send_command('bind !8 input /ja "Immanence" <me>; wait 1.2; input /ma "Blizzard" <t>') -- Alt + 8

	-- Your Thunder Burst / Closer (Immanence + Thunder)
	-- Use this to Magic Burst when Iroha closes Fusion, or use it to close Impaction on your own.
	windower.send_command('bind !9 input /ja "Immanence" <me>; wait 1.2; input /ma "Thunder" <t>') -- Alt + 9

	windower.send_command("bind ^` input /ma Aspir")

	windower.send_command('bind !` input /ma "Fire II" <stnpc>') -- Alt + 3
	windower.send_command('bind !1 input /ma "Aero II" <t>') -- Alt + 3
	-- windower.send_command('bind !2 input /ma "Blizzard II" <t>') -- Alt + 1
	windower.send_command('bind !2 input /ma "Thunder II" <t>') -- Alt + 2
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
