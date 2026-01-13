Spring = {GetModOptions = function() return {
	commanderbuildersrange = 1000,
	commanderbuildersbuildpower = 400,
	assistdronesbuildpowermultiplier = 1,
	pushresistant = false,
} end}

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
	_,my_table = next(my_table)
else
	print("None")
	return
end

local success2,json_string = pcall(json.encode,my_table)
if success2 then
	print(json_string) -- This output can be captured by the Python script
else
	print("None")
end