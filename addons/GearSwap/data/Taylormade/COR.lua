include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}
sets.default = {
	main = "Kaja Knife",
	sub = "Arasy knife",
	range = "Homestead Gun",
	ammo = "Bronze Bullet",
	head = "Mummu Bonnet",
	body = "SV Separates +1",
	hands = "SV Gauntlets +1",
	legs = "SV Loincloth +1",
	feet = "SV Gaiters +1",
	neck = "Sanctity necklace",
	waist = "Gerdr Belt",
	left_ear = "Brutal Earring",
	right_ear = "Suppanomimi",
	left_ring = "Meghanada Ring",
	right_ring = "Mummu Ring",
	back = "Nexus Cape",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

sets.rolling = set_combine(sets.default, {
	left_ring = "Barataria Ring",
	right_ring = "Luzaf's Ring",
})

local lucky_roll_pending = false

function get_sets()
	taylormade_common.setup()

	-- Wrap the inner text containing apostrophes in brackets [ ]
	-- This tells the FFXI game engine to read the string exactly as written.
	windower.send_command("bind !1 input /ja [Bolter's Roll] <me>")
	windower.send_command('bind !2 input /ja "Double Up" <me>')

	windower.send_command("bind !3 input /ja [Corsair's Roll] <me>")
	-- [Hunter\'s Roll]
	windower.send_command("bind !4 input /ja [Chaos Roll] <me>")
	-- [Tactician\'s Roll]

	-- Single Roll on !5
	windower.send_command("bind !5 input /ja [Hunter's Roll] <me>")
end

function self_command(command)
	if command == "lucky_roll" then
		lucky_roll_pending = true
		taylormade_common.debug("COR debug: lucky_roll state enabled.")
	elseif command == "clear_lucky_roll" then
		lucky_roll_pending = false
		taylormade_common.debug("COR debug: lucky_roll state cleared.")
	elseif command == "auto_double_up" then
		taylormade_common.debug("COR debug: auto Double Up queued.")
		windower.send_command('wait 1;input /ja "Double Up" <me>')
	end
end

function precast(spell)
	if spell.english == "Double Up" or spell.english == "Double-Up" then
		if lucky_roll_pending then
			lucky_roll_pending = false
			taylormade_common.debug("COR debug: blocking first Double Up after lucky roll; repeat to confirm.")
			cancel_spell()
			return
		end
		return
	end

	if spell.type == "CorsairRoll" then
		taylormade_common.debug("COR debug: " .. spell.english .. " precast; equipping rolling set.")
		equip(sets.rolling)
	end
end

function job_aftercast(spell)
	taylormade_common.debug("COR debug: job_aftercast received type=" .. tostring(spell.type) .. "; action=" .. tostring(spell.english))
	if spell.type == "CorsairRoll" then
		taylormade_common.debug("COR debug: " .. spell.english .. " aftercast; restoring engaged/default set.")
		equip(sets.engaged or sets.default)
	end
end

function file_unload()
	-- This natively triggers when you un-load or change jobs to wipe the keys
	windower.send_command("unbind ^`")
	windower.send_command("unbind !`")
	windower.send_command("unbind !1")
	windower.send_command("unbind !2")
	windower.send_command("unbind !3")
	windower.send_command("unbind !4")
	windower.send_command("unbind !5")
end
