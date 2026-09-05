-- HouseLogic: doors + ownership locks, house buying, seats, doorbells, day/night
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

-- ================= economy + house ownership =================
local PRICES = {
	TinyHouse = 500, ZenHouse = 800, AFrame = 1200, ModernCube = 2000,
	Dome = 2500, VillaL = 3000, Castle = 5000, Mansion = 8000,
}

Players.PlayerAdded:Connect(function(player)
	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	local cash = Instance.new("IntValue")
	cash.Name = "Cash"
	cash.Value = 200
	cash.Parent = ls
	ls.Parent = player
end)

task.spawn(function() -- passive income
	while true do
		task.wait(10)
		for _, player in ipairs(Players:GetPlayers()) do
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if cash then
				cash.Value += 15
			end
		end
	end
end)

local function houseFolders()
	local out = {}
	for _, folder in ipairs(workspace:GetChildren()) do
		if folder:IsA("Folder") and PRICES[folder.Name] then
			table.insert(out, folder)
		end
	end
	return out
end

-- for-sale signs at each front door
for _, folder in ipairs(houseFolders()) do
	local door = folder:FindFirstChild("Door", true)
	if door and door:IsA("BasePart") then
		local price = PRICES[folder.Name]
		local sign = Instance.new("Part")
		sign.Name = "SaleSign"
		sign.Size = Vector3.new(0.6, 5, 0.6)
		sign.Color = Color3.fromRGB(87, 60, 42)
		sign.Material = Enum.Material.Wood
		sign.Anchored = true
		sign.CFrame = door.CFrame * CFrame.new(door.Size.X / 2 + 4, 1.5, 5)
		sign.Parent = folder

		local gui = Instance.new("BillboardGui")
		gui.Name = "SignGui"
		gui.Size = UDim2.new(0, 380, 0, 130)
		gui.StudsOffset = Vector3.new(0, 3.6, 0)
		gui.AlwaysOnTop = true
		gui.MaxDistance = 150
		gui.Parent = sign
		local label = Instance.new("TextLabel")
		label.Name = "Text"
		label.Size = UDim2.new(1, 0, 1, 0)
		label.BackgroundColor3 = Color3.new(0, 0, 0)
		label.BackgroundTransparency = 0.35
		label.TextColor3 = Color3.new(1, 1, 1)
		label.TextScaled = true
		label.Font = Enum.Font.GothamBold
		label.Text = string.format("🏠 %s\n$%d — klik untuk beli!", folder.Name, price)
		label.Parent = gui

		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 20
		click.Parent = sign

		click.MouseClick:Connect(function(player)
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if not cash then return end
			if folder:GetAttribute("OwnerId") then
				label.Text = string.format("🏠 %s\nmilik %s", folder.Name,
					folder:GetAttribute("OwnerName"))
				return
			end
			if cash.Value < price then
				label.Text = string.format("🏠 %s\nbutuh $%d (kamu punya $%d)",
					folder.Name, price, cash.Value)
				task.delay(2, function()
					if not folder:GetAttribute("OwnerId") then
						label.Text = string.format("🏠 %s\n$%d — klik untuk beli!",
							folder.Name, price)
					end
				end)
				return
			end
			cash.Value -= price
			folder:SetAttribute("OwnerId", player.UserId)
			folder:SetAttribute("OwnerName", player.Name)
			for _, d in ipairs(folder:GetDescendants()) do
				if d:IsA("BasePart") and d.Name == "Door" then
					d:SetAttribute("OwnerId", player.UserId)
				end
			end
			label.Text = string.format("🏠 %s\nmilik %s 🎉", folder.Name, player.Name)
		end)
	end
end

-- ================= doors: swing on touch, owner-only lock =================
local function getHumanoid(hit)
	local char = hit.Parent
	if not char then return nil end
	local hum = char:FindFirstChildOfClass("Humanoid")
	if not hum then
		hum = char.Parent and char.Parent:FindFirstChildOfClass("Humanoid")
	end
	return hum
end

local function getPlayer(hit)
	return Players:GetPlayerFromCharacter(hit.Parent)
		or (hit.Parent and Players:GetPlayerFromCharacter(hit.Parent.Parent))
end

for _, door in ipairs(workspace:GetDescendants()) do
	if door:IsA("BasePart") and door.Name == "Door" then
		door.CanCollide = false
		local closed = door.CFrame
		local origColor = door.Color
		local w = door.Size.X
		local open = closed * CFrame.new(-w / 2, 0, 0)
			* CFrame.Angles(0, math.rad(100), 0) * CFrame.new(w / 2, 0, 0)
		local debounce = false
		door.Touched:Connect(function(hit)
			if debounce then return end
			local player = getPlayer(hit)
			if door:GetAttribute("Locked") and player
				and player.UserId ~= door:GetAttribute("OwnerId") then
				return -- locked doors stay shut for strangers
			end
			local hum = getHumanoid(hit)
			if hum and hum.Health > 0 then
				debounce = true
				door.CanCollide = false
				TweenService:Create(door, TweenInfo.new(0.5), { CFrame = open }):Play()
				task.delay(3, function()
					if not door:GetAttribute("Locked") then
						TweenService:Create(door, TweenInfo.new(0.5), { CFrame = closed }):Play()
					end
					task.wait(0.5)
					debounce = false
				end)
			end
		end)

		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 12
		click.Parent = door
		click.MouseClick:Connect(function(player)
			if player.UserId ~= door:GetAttribute("OwnerId") then return end
			local locked = not door:GetAttribute("Locked")
			door:SetAttribute("Locked", locked)
			door.CanCollide = locked
			door.Color = locked and Color3.fromRGB(130, 35, 35) or origColor
		end)
	end
end

-- ================= day/night cycle (full day in 4 minutes) =================
local DAY_SECONDS = 240
RunService.Heartbeat:Connect(function(dt)
	Lighting.ClockTime = (Lighting.ClockTime + dt * 24 / DAY_SECONDS) % 24
end)

-- ================= sit-down seats on furniture =================
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

-- ================= doorbells (click bell -> chime + "guest" sign) =================
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
