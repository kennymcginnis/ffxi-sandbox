_addon.name = "bridge"
_addon.author = "Jim & I"
_addon.version = "9.1 Universal"

require("sets")
local socket = require("socket")
local texts = require("texts")
local res = require("resources")

local port = 62650
local leader_name = "Taylormade"
local modes = { "Loose", "Normal", "Strict", "Planning", "Audit", "Off" }
local current_mode_index = 2
local last_poll_time = os.clock()
local is_transitioning_job = false

-- TRANSLATOR CONFIG
local translator_enabled = true
local user_lang = "EN"

-- FFXI Native Color Palette (True Game Colors & Window 1 Primary Routing)
local native_chat_modes = {
	tell = 204, -- Tell Magenta / Purple
	party = 205, -- Party Blue
	linkshell = 206, -- Linkshell 1 Green
	linkshell2 = 213, -- Linkshell 2 Coral
	say = 208, -- Say Yellow
	shout = 160, -- Shout Red / Orange
	custom = 207, -- Default Soft Cyan Echo
}

-- SILENT TRUST PROBE ENGINE
local silent_query_active = false
local silent_query_start_time = 0
local query_collected_modes = {}
local query_assist_target = ""

-- HUD DISPLAY
local mode_hud = texts.new()
mode_hud:font("Noto Sans Mono", "Consolas", "Courier New")
mode_hud:size(10)
mode_hud:pos(1800, 0)
mode_hud:bg_alpha(150)
mode_hud:bg_visible(true)

local function is_party_leader()
	local player = windower.ffxi.get_player()
	if not player then
		return false
	end
	return player.name:lower() == leader_name:lower()
end

local function update_hud_display()
	local trans_status = translator_enabled and (user_lang == "EN" and "[TR: EN->JA]" or "[TR: JA->EN]") or "[TR: OFF]"
	if is_party_leader() then
		mode_hud:visible(true)
		local mode_name = modes[current_mode_index]
		mode_hud:text(string.format(" Mode: %s | %s ", mode_name, trans_status))
		if mode_name == "Loose" then
			mode_hud:color(135, 206, 250)
		elseif mode_name == "Normal" then
			mode_hud:color(50, 205, 50)
		elseif mode_name == "Strict" then
			mode_hud:color(255, 215, 0)
		elseif mode_name == "Planning" then
			mode_hud:color(218, 112, 214)
		elseif mode_name == "Audit" then
			mode_hud:color(255, 140, 0)
		elseif mode_name == "Off" then
			mode_hud:color(255, 69, 0)
		end
	else
		mode_hud:visible(true)
		mode_hud:text(string.format(" %s ", trans_status))
		if user_lang == "EN" then
			mode_hud:color(0, 229, 255)
		else
			mode_hud:color(50, 205, 50)
		end
	end
end

local function trigger_silent_trust_query()
	if is_transitioning_job then
		return
	end
	silent_query_active = true
	silent_query_start_time = os.clock()
	query_collected_modes = {}
	query_assist_target = ""
	windower.send_command("trust status")
end

local function simple_json_encode(val)
	local t = type(val)
	if t == "string" then
		return '"' .. val:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n") .. '"'
	elseif t == "number" or t == "boolean" then
		return tostring(val)
	elseif t == "table" then
		if val[1] ~= nil then
			local parts = {}
			for _, v in ipairs(val) do
				table.insert(parts, simple_json_encode(v))
			end
			return "[" .. table.concat(parts, ",") .. "]"
		else
			local parts = {}
			for k, v in pairs(val) do
				table.insert(parts, string.format('"%s":%s', k, simple_json_encode(v)))
			end
			return "{" .. table.concat(parts, ",") .. "}"
		end
	else
		return "null"
	end
end

local function get_game_context()
	local info = windower.ffxi.get_info()
	local zone_id = info and info.zone or 0
	local zone_name = (res.zones[zone_id] and res.zones[zone_id].en) or "Unknown Zone"

	local target_mob = windower.ffxi.get_mob_by_target("t")
	local target_name = target_mob and target_mob.name or "None"

	local party_jobs = {}
	local party = windower.ffxi.get_party()
	if party then
		for i = 0, 5 do
			local member = party["p" .. i]
			if member and member.mob then
				local main_job = member.mob.main_job or "Unknown"
				table.insert(party_jobs, member.name .. " (" .. main_job .. ")")
			end
		end
	end

	return {
		zone = zone_name,
		target = target_name,
		party = party_jobs,
	}
end

-- UNIFIED NON-BLOCKING SOCKET DISPATCHER
local function communicate_with_server(payload_table, callback)
	local client = socket.tcp()
	client:settimeout(0.04)
	local success, err = client:connect("127.0.0.1", port)
	if success or err == "already connected" then
		client:send(simple_json_encode(payload_table) .. "\n")
		if callback then
			client:settimeout(0.25)
		end
		local response = client:receive("*l")
		client:close()
		if response and response ~= "" and callback then
			callback(response)
		end
	else
		client:close()
	end
end

local function handle_unified_poll_response(response_str)
	local server_lang = response_str:match('"user_lang"%s*:%s*"([^"]-)"')
	if server_lang and server_lang ~= user_lang then
		user_lang = server_lang
		update_hud_display()
	end

	local query_trust = response_str:match('"query_trust"%s*:%s*true')
	if query_trust and not is_transitioning_job then
		trigger_silent_trust_query()
	end

	local cmds_block = response_str:match('"commands"%s*:%s*%[(.-)%]')
	if cmds_block then
		for cmd in cmds_block:gmatch('"([^"]+)"') do
			local final_cmd = cmd
			if final_cmd:sub(1, 2) == "//" then
				final_cmd = final_cmd:sub(3)
			end
			final_cmd = final_cmd:gsub("^%s*", ""):gsub("%s*$", "")
			if final_cmd:sub(1, 1) == "/" then
				windower.chat.input(final_cmd)
			else
				windower.add_to_chat(207, "[Bridge Debug] Running: " .. final_cmd)
				windower.send_command(final_cmd)
			end
		end
	end

	local trans_block = response_str:match('"translations"%s*:%s*%[(.-)%]')
	if trans_block and trans_block ~= "" then
		for item_str in trans_block:gmatch("%{.-%}") do
			local dir = item_str:match('"direction"%s*:%s*"([^"]-)"')
			local trans = item_str:match('"translated_text"%s*:%s*"([^"]-)"')
			local alert = item_str:match('"tactical_alert"%s*:%s*"([^"]-)"')
			local sender = item_str:match('"sender"%s*:%s*"([^"]-)"')
			local chan = item_str:match('"channel"%s*:%s*"([^"]-)"') or "party"
			local tell_target = item_str:match('"tell_target"%s*:%s*"([^"]-)"')

			if trans and trans ~= "" then
				if dir == "INCOMING" then
					local lang_tag = (user_lang == "EN") and "[JP->EN]" or "[EN->JP]"
					local chat_mode = native_chat_modes[chan] or native_chat_modes.custom

					windower.add_to_chat(chat_mode, string.format("%s (%s): %s", lang_tag, sender or "Party", trans))
					if alert and alert ~= "null" and alert ~= "" then
						windower.add_to_chat(167, string.format("⚡ [TACTICAL ALERT]: %s", alert))
					end
				elseif dir == "OUTGOING" then
					local prefix = "/p "
					if chan == "tell" and tell_target and tell_target ~= "" then
						prefix = "/t " .. tell_target .. " "
					elseif chan == "linkshell" then
						prefix = "/l "
					elseif chan == "linkshell2" then
						prefix = "/l2 "
					elseif chan == "say" then
						prefix = "/s "
					elseif chan == "shout" then
						prefix = "/sh "
					end
					windower.chat.input(windower.to_shift_jis(prefix .. trans))
				end
			end
		end
	end
end

-- INCOMING CHAT HOOK
windower.register_event("chat message", function(message, sender, mode, gm)
	if not translator_enabled then
		return
	end
	local player = windower.ffxi.get_player()
	if not player or sender == player.name then
		return
	end

	local chan = nil
	if mode == 1 then
		chan = "shout"
	elseif mode == 2 then
		chan = "shout"
	elseif mode == 3 then
		chan = "tell"
	elseif mode == 4 then
		chan = "party"
	elseif mode == 5 then
		chan = "linkshell"
	elseif mode == 27 then
		chan = "linkshell2"
	elseif mode == 26 then
		chan = "say"
	end

	if not chan then
		return
	end

	local ctx = get_game_context()
	communicate_with_server({
		type = "TRANSLATE_MESSAGE",
		direction = "INCOMING",
		sender = sender,
		recipient = player.name,
		message = message,
		channel = chan,
		zone = ctx.zone,
		target = ctx.target,
		party_jobs = ctx.party,
	})
end)

windower.register_event("incoming text", function(original, modified, mode)
	if silent_query_active and original:find("^Trust:%s+") then
		local m_name, m_val = original:match("^Trust:%s*([%w_]+):%s*([%w_]+)")
		if m_name and m_val then
			query_collected_modes[m_name] = m_val
			return true
		end
		local assist = original:match("^Trust:%s*Assisting%s+([%w_]+)")
		if assist then
			query_assist_target = assist
			return true
		end
		return true
	end
end)

windower.register_event("outgoing text", function(original, modified)
	local player = windower.ffxi.get_player()
	if not player or is_transitioning_job then
		return
	end

	local trust_mode, trust_val = original:match("^/?/?trust%s+set%s+([%a%d_]+)%s+([%a%d_]+)")
	if trust_mode and trust_val then
		communicate_with_server({
			type = "TRUST_SYNC",
			character = player.name,
			mode_name = trust_mode,
			mode_val = trust_val,
		})
	end
end)

-- UNIFIED PRERENDER POLLING (Clean 0.5s cadence, zero socket buildup)
windower.register_event("prerender", function()
	local now = os.clock()
	local player = windower.ffxi.get_player()
	if not player or is_transitioning_job or not player.main_job then
		return
	end

	if silent_query_active and (now - silent_query_start_time >= 1.0) then
		silent_query_active = false
		if next(query_collected_modes) ~= nil or query_assist_target ~= "" then
			communicate_with_server({
				type = "TRUST_FULL_STATUS",
				character = player.name,
				modes = query_collected_modes,
				assist_target = query_assist_target,
			})
		end
	end

	if now - last_poll_time >= 0.5 then
		last_poll_time = now
		communicate_with_server({
			type = "UNIFIED_POLL",
			my_name = player.name,
			my_job = player.main_job,
		}, handle_unified_poll_response)
	end
end)

-- COMMAND HOOKS
windower.register_event("addon command", function(...)
	local args = { ... }
	if #args == 0 then
		windower.add_to_chat(207, "[Bridge] //tr <msg> | //trt <target> <msg> | //trl <msg> | //tr swap | //bridge lock")
		return
	end

	local first = args[1]:lower()

	if first == "lock" then
		communicate_with_server({ type = "LOCK_SCREEN" })
		windower.add_to_chat(207, "[Bridge] Transparent Screen Lock engaged.")
		return
	elseif first == "swap" or first == "lang" then
		user_lang = (user_lang == "EN") and "JA" or "EN"
		update_hud_display()
		communicate_with_server({ type = "LANG_SWAP", user_lang = user_lang })
		windower.add_to_chat(207, "[Bridge] Mode swapped: " .. (user_lang == "EN" and "English Speaker" or "日本語話者"))
		return
	elseif first == "toggle" then
		translator_enabled = not translator_enabled
		update_hud_display()
		windower.add_to_chat(207, "[Bridge] Translator: " .. (translator_enabled and "ON" or "OFF"))
		return
	end

	local chan = "party"
	local tell_target = nil

	if first == "t" or first == "tell" then
		chan = "tell"
		table.remove(args, 1)
		tell_target = table.remove(args, 1)
	elseif first == "l" or first == "ls" or first == "linkshell" then
		chan = "linkshell"
		table.remove(args, 1)
	elseif first == "l2" or first == "ls2" or first == "linkshell2" then
		chan = "linkshell2"
		table.remove(args, 1)
	elseif first == "s" or first == "say" then
		chan = "say"
		table.remove(args, 1)
	elseif first == "sh" or first == "shout" then
		chan = "shout"
		table.remove(args, 1)
	elseif first == "p" or first == "party" or first == "tr" or first == "translate" then
		table.remove(args, 1)
	end

	local raw_msg = table.concat(args, " ")
	if raw_msg == "" then
		return
	end

	local player = windower.ffxi.get_player()
	local ctx = get_game_context()
	communicate_with_server({
		type = "TRANSLATE_MESSAGE",
		direction = "OUTGOING",
		sender = player and player.name or "Unknown",
		recipient = player and player.name or "Unknown",
		message = raw_msg,
		channel = chan,
		tell_target = tell_target,
		zone = ctx.zone,
		target = ctx.target,
		party_jobs = ctx.party,
	})
end)

windower.register_event("job change", function(main_job_id, sub_job_id)
	is_transitioning_job = true
	silent_query_active = false
	windower.send_command("lua u Trusts")
	coroutine.schedule(function()
		windower.send_command("lua l Trusts")
	end, 7.0)
	coroutine.schedule(function()
		is_transitioning_job = false
		trigger_silent_trust_query()
	end, 10.5)
end)

windower.register_event("zone change", function(new_zone_id, old_zone_id)
	coroutine.schedule(function()
		trigger_silent_trust_query()
	end, 4.0)
end)

windower.register_event("load", function()
	update_hud_display()
	windower.send_command("alias tr lua c bridge tr")
	windower.send_command("alias trt lua c bridge t")
	windower.send_command("alias trl lua c bridge l")
	windower.send_command("alias trl2 lua c bridge l2")
	windower.send_command("alias trs lua c bridge s")
	windower.send_command("alias trsh lua c bridge sh")
	windower.send_command("alias lock lua c bridge lock")
	coroutine.schedule(function()
		trigger_silent_trust_query()
	end, 4.0)
	windower.add_to_chat(207, "[Bridge] Unified v9.1 loaded! Commands: //tr, //trt, //trl, //lock")
end)

windower.register_event("unload", function()
	mode_hud:visible(false)
	windower.send_command("unalias tr")
	windower.send_command("unalias trt")
	windower.send_command("unalias trl")
	windower.send_command("unalias trl2")
	windower.send_command("unalias trs")
	windower.send_command("unalias trsh")
	windower.send_command("unalias lock")
end)
