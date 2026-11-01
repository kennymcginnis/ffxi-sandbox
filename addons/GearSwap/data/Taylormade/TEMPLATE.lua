include("organizer-lib")
include("common")

-- GearSwap requires the core 'sets' variable to initialize the file.
-- Do not delete this line.
sets = {}

-- Add the gear you want this job to use. Leave unneeded slots out.
sets.default = {
	-- main = "Item Name",
	-- sub = "Item Name",
	-- range = "Item Name",
	-- ammo = "Item Name",
	-- head = "Item Name",
	-- body = "Item Name",
	-- hands = "Item Name",
	-- legs = "Item Name",
	-- feet = "Item Name",
	-- neck = "Item Name",
	-- waist = "Item Name",
	-- left_ear = "Item Name",
	-- right_ear = "Item Name",
	-- left_ring = "Item Name",
	-- right_ring = "Item Name",
	-- back = "Item Name",
}

sets.idle = set_combine(sets.default, {
	left_ring = "Shneddick Ring",
})

function get_sets()
	taylormade_common.setup()
end
