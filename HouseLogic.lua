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
		local w = door.Size.X
		-- swing around the left edge (hinge), not panel center
		local open = closed * CFrame.new(-w / 2, 0, 0)
			* CFrame.Angles(0, math.rad(100), 0) * CFrame.new(w / 2, 0, 0)
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

-- ============ Day/night cycle (full day in 4 minutes) ============
local Lighting = game:GetService("Lighting")
local RunService = game:GetService("RunService")
local DAY_SECONDS = 240
RunService.Heartbeat:Connect(function(dt)
	Lighting.ClockTime = (Lighting.ClockTime + dt * 24 / DAY_SECONDS) % 24
end)

-- ============ Sit-down seats on furniture ============
-- Invisible Seats spawned on chairs/sofas/loungers, facing away from the
-- nearest backrest so sitters face the right way.
local BACK_NAMES = { ChairBack = true, SofaBack = true, BedHead = true, LoungeBack = true }
local SEAT_NAMES = { ChairSeat = true, SofaBase = true, LoungeChair = true }
local backs, seats = {}, {}
for _, p in ipairs(workspace:GetDescendants()) do
	if p:IsA("BasePart") then
		if BACK_NAMES[p.Name] then
			table.insert(backs, p)
		elseif SEAT_NAMES[p.Name] then
			table.insert(seats, p)
		end
	end
end
for _, p in ipairs(seats) do
	local seat = Instance.new("Seat")
	seat.Name = "SitHere"
	seat.Anchored = true
	seat.CanCollide = false
	seat.Transparency = 1
	if p.Name == "SofaBase" then
		seat.Size = Vector3.new(p.Size.X * 0.85, 0.5, 2.4)
	else
		seat.Size = Vector3.new(p.Size.X * 0.8, 0.4, p.Size.Z * 0.8)
	end
	local best, bestD = nil, math.huge
	for _, q in ipairs(backs) do
		local d = (q.Position - p.Position).Magnitude
		if d < bestD then
			best, bestD = q, d
		end
	end
	local pos = p.Position + Vector3.new(0, p.Size.Y / 2 + (p.Name == "SofaBase" and 0.85 or 0.4), 0)
	if best then
		local flat = (p.Position - best.Position) * Vector3.new(1, 0, 1)
		seat.CFrame = CFrame.lookAt(pos, pos + flat)
	else
		seat.CFrame = CFrame.new(pos)
	end
	seat.Parent = p.Parent
end

-- ============ Doorbells (click bell -> chime + "guest" sign) ============
for _, door in ipairs(workspace:GetDescendants()) do
	if door:IsA("BasePart") and door.Name == "Door" then
		local bell = Instance.new("Part")
		bell.Name = "Doorbell"
		bell.Shape = Enum.PartType.Ball
		bell.Size = Vector3.new(0.9, 0.9, 0.9)
		bell.Color = Color3.fromRGB(212, 175, 55)
		bell.Material = Enum.Material.Metal
		bell.Anchored = true
		bell.CanCollide = false
		bell.CFrame = door.CFrame * CFrame.new(door.Size.X / 2 + 1.2, 0, -0.9)
		bell.Parent = door.Parent

		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 14
		click.Parent = bell

		local sound = Instance.new("Sound")
		sound.SoundId = "rbxasset://sounds/electronicpingshort.wav"
		sound.Volume = 1
		sound.Parent = bell

		local gui = Instance.new("BillboardGui")
		gui.Size = UDim2.new(0, 280, 0, 70)
		gui.StudsOffset = Vector3.new(0, door.Size.Y / 2 + 2, 0)
		gui.AlwaysOnTop = true
		gui.Enabled = false
		gui.Parent = door
		local label = Instance.new("TextLabel")
		label.Size = UDim2.new(1, 0, 1, 0)
		label.BackgroundColor3 = Color3.new(0, 0, 0)
		label.BackgroundTransparency = 0.4
		label.TextColor3 = Color3.new(1, 1, 1)
		label.TextScaled = true
		label.Font = Enum.Font.GothamBold
		label.Text = "🔔 Ada tamu di pintu!"
		label.Parent = gui

		local debounce = false
		click.MouseClick:Connect(function()
			if debounce then return end
			debounce = true
			sound:Play()
			gui.Enabled = true
			task.delay(3, function()
				gui.Enabled = false
				debounce = false
			end)
		end)
	end
end

print("HouseLogic loaded")
