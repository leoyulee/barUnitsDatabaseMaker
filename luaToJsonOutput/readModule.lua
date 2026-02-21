Spring = {
	GetModOptions = function()
		return {
			commanderbuildersrange = 1000,
			commanderbuildersbuildpower = 400,
			assistdronesbuildpowermultiplier = 1,
			pushresistant = false,
		}
	end;
	Utilities = {
		Gametype = {
			IsRaptors = function() return false end;
			IsScavengers = function() return false end;
		};
	};
}

local source = debug.getinfo(1).source
-- Remove the leading '@' if present (common on Unix/Linux)
source = source:gsub("^@", "")
-- Extract the directory part (OS-dependent regex might be needed)
local dir = source:match("(.*/)[^/]+$") or source:match("(.+\\)[^%\\]+$")

package.path = dir.. "/?.lua" --package.path .. ";../?.lua"

local json = require("json")
local args = {...}

local success, my_table = pcall(require,args[1])
if success then
	for _, t in pairs(my_table) do
		local success2,json_string = pcall(json.encode,t)
		if success2 then
			print(json_string) -- This output can be captured by the Python script
		else
			print(json_string)
		end
	end
else
	print(my_table)
	return
end

