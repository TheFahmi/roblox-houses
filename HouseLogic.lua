-- HouseLogic: door open/close, light toggle, house info BillboardGui
local TweenService = game:GetService("TweenService")

local function getHumanoid(hit)
	local char = hit.Parent
	if not char then return nil end
	local hum = char:FindFirstChildOfClass("Humanoid")
	if not hum then
		hum = char.Parent and char.Parent:FindFirstChildOfClass("Humanoid")
	end
	return hum
end

-- All doors auto-swing open on proximity touch, close after 3s
for _, door in ipairs(workspace:GetDescendants()) do
	if door:IsA("BasePart") and door.Name == "Door" then
		door.CanCollide = false -- walk-through glass door, swing visual only
		local closed = door.CFrame
		local open = closed * CFrame.Angles(0, math.rad(100), 0)
		local debounce = false
		door.Touched:Connect(function(hit)
			if debounce then return end
			local hum = getHumanoid(hit)
			if hum and hum.Health > 0 then
				debounce = true
				door.CanCollide = false
				TweenService:Create(door, TweenInfo.new(0.5), {CFrame = open}):Play()
				task.delay(3, function()
					TweenService:Create(door, TweenInfo.new(0.5), {CFrame = closed}):Play()
					task.wait(0.5)
					debounce = false
				end)
			end
		end)
	end
end

-- Neon bulbs pulse softly (ambience)
local bulbs = {}
for _, p in ipairs(workspace:GetDescendants()) do
	if p:IsA("BasePart") and p.Material == Enum.Material.Neon and p.Name ~= "TVPanel" then
		table.insert(bulbs, p)
	end
end

task.spawn(function()
	while true do
		local t = os.clock() % 2
		for _, b in ipairs(bulbs) do
			b.Transparency = t < 1 and 0 or 0.15
		end
		task.wait(1)
	end
end)

print("HouseLogic loaded")
