taylormade_common = {}
taylormade_debug = false

organizer_items = {
	warp_ring = "Warp Ring",
	echad_ring = "Echad Ring",
	empress_band = "Empress Band",
	shneddick_ring = "Shneddick Ring",
	mecisto_mantle = "Mecisto. Mantle",
	instant_warp = "Instant Warp",
	grape_daifuku = "Grape Daifuku",
}

local res = require("resources")

function taylormade_common.debug(message)
	if taylormade_debug then
		windower.add_to_chat(122, message)
	end
end

function taylormade_common.setup()
	if sets.default and next(sets.default) then
		if world.in_mog_house then
			windower.send_command("wait 2;gs org;wait 2;gs equip idle")
		else
			windower.send_command("wait 2;gs equip idle")
		end
	end
end

function taylormade_common.equip_status(status)
	if status == "Idle" then
		taylormade_common.debug("Gear debug: Idle status; equipping idle set.")
		equip(sets.idle or sets.default)
	elseif status == "Engaged" then
		taylormade_common.debug("Gear debug: Engaged status; equipping engaged set.")
		equip(sets.engaged or sets.default)
	elseif status == "Resting" then
		if sets.resting then
			taylormade_common.debug("Gear debug: Resting status; equipping resting set.")
			equip(sets.resting)
		else
			taylormade_common.debug("Gear debug: Resting status; no resting set is defined.")
		end
	end
end

function taylormade_common.ability_ready(name)
	local ability = res.job_abilities:with("en", name)
	if not ability or not ability.recast_id then
		windower.add_to_chat(167, "*** Could not find recast data for " .. name .. "! ***")
		return false
	end
	local recasts = windower.ffxi.get_ability_recasts()
	return recasts[ability.recast_id] == 0
end

function status_change(new, old)
	if job_status_change then
		job_status_change(new, old)
	end
	taylormade_common.equip_status(new)
end

function aftercast(spell)
	taylormade_common.debug("Gear debug: aftercast callback; type=" .. tostring(spell.type) .. "; action=" .. tostring(spell.english))
	if job_aftercast then
		job_aftercast(spell)
	end
	taylormade_common.equip_status(player.status)
end

function job_self_command(commandArgs, eventArgs)
	if commandArgs[1] == "warp" then
		send_command('@input /equip ring2 "Warp Ring"')
		-- Allow time for the ring's equip delay before using
		coroutine.schedule(function()
			send_command('@input /item "Warp Ring" <me>')
		end, 11)
	end
end
