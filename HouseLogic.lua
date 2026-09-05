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

local function baseName(folderName)
	return folderName:gsub("#%d+$", "")
end

-- DataStore persistence (works in published games; silent no-op in Studio
-- unless "Enable Studio Access to API Services" is on)
local store
pcall(function()
	store = game:GetService("DataStoreService"):GetDataStore("HouseGame_v1")
end)

local function loadCash(player)
	if not store then return nil end
	local ok, data = pcall(function()
		return store:GetAsync("cash_" .. player.UserId)
	end)
	return ok and data or nil
end

local function saveCash(player)
	if not store then return end
	local ls = player:FindFirstChild("leaderstats")
	local cash = ls and ls:FindFirstChild("Cash")
	if cash then
		pcall(function()
			store:SetAsync("cash_" .. player.UserId, cash.Value)
		end)
	end
end

Players.PlayerAdded:Connect(function(player)
	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	local cash = Instance.new("IntValue")
	cash.Name = "Cash"
	cash.Value = 200
	cash.Parent = ls
	ls.Parent = player
	local saved = loadCash(player)
	if saved then
		cash.Value = saved
	end
end)

task.spawn(function() -- passive income
	while true do
		task.wait(10)
		for _, player in ipairs(Players:GetPlayers()) do
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if cash then
				cash.Value += 5
			end
		end
	end
end)

task.spawn(function() -- autosave every 60s
	while true do
		task.wait(60)
		for _, player in ipairs(Players:GetPlayers()) do
			saveCash(player)
		end
	end
end)

local function houseFolders()
	local out = {}
	for _, folder in ipairs(workspace:GetChildren()) do
		if folder:IsA("Folder") and PRICES[baseName(folder.Name)] then
			table.insert(out, folder)
		end
	end
	return out
end

-- for-sale signs at each front door
for _, folder in ipairs(houseFolders()) do
	local door = folder:FindFirstChild("Door", true)
	if door and door:IsA("BasePart") then
		local price = PRICES[baseName(folder.Name)]
		local sign = Instance.new("Part")
		sign.Name = "SaleSign"
		sign.Size = Vector3.new(7, 5, 0.4)
		sign.Color = Color3.fromRGB(87, 60, 42)
		sign.Material = Enum.Material.Wood
		sign.Anchored = true
		-- panel faces the same way as the door, offset to its right side
		local base = door.Position + door.CFrame.RightVector
			* (door.Size.X / 2 + 6) + door.CFrame.LookVector * 5
			+ Vector3.new(0, -door.Size.Y / 2 + 4.5, 0)
		sign.CFrame = CFrame.new(base, base + door.CFrame.LookVector)
		local post = Instance.new("Part")
		post.Name = "SaleSignPost"
		post.Size = Vector3.new(0.6, 4.5, 0.6)
		post.Color = Color3.fromRGB(60, 42, 30)
		post.Material = Enum.Material.Wood
		post.Anchored = true
		post.CFrame = sign.CFrame * CFrame.new(0, -4.5, 0)
		post.Parent = folder

		local function makeLabel(gui, name)
			local l = Instance.new("TextLabel")
			l.Name = name
			l.Size = UDim2.new(1, 0, 1, 0)
			l.BackgroundColor3 = Color3.fromRGB(30, 22, 16)
			l.BackgroundTransparency = 0.2
			l.TextColor3 = Color3.new(1, 1, 1)
			l.TextScaled = true
			l.Font = Enum.Font.GothamBold
			l.Parent = gui
			return l
		end
		local gui = Instance.new("SurfaceGui")
		gui.Name = "SignGui"
		gui.Face = Enum.NormalId.Front
		gui.Parent = sign
		local label = makeLabel(gui, "Text")
		local gui2 = Instance.new("SurfaceGui")
		gui2.Name = "SignGuiBack"
		gui2.Face = Enum.NormalId.Back
		gui2.Parent = sign
		local label2 = makeLabel(gui2, "TextBack")

		local function setText(t)
			label.Text = t
			label2.Text = t
		end
		setText(string.format("%s\n$%d\nklik untuk beli",
			baseName(folder.Name), price))

		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 20
		click.Parent = sign

		click.MouseClick:Connect(function(player)
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if not cash then return end
			if folder:GetAttribute("OwnerId") then
				setText(string.format("%s\nmilik %s", baseName(folder.Name),
					folder:GetAttribute("OwnerName")))
				return
			end
			if cash.Value < price then
				setText(string.format("%s\nbutuh $%d (kamu punya $%d)",
					baseName(folder.Name), price, cash.Value))
				task.delay(2, function()
					if not folder:GetAttribute("OwnerId") then
						setText(string.format("%s\n$%d\nklik untuk beli",
							baseName(folder.Name), price))
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
			setText(string.format("%s\nmilik %s 🎉",
				baseName(folder.Name), player.Name))
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

-- ================= saving: leave + shutdown =================
Players.PlayerRemoving:Connect(saveCash)
game:BindToClose(function()
	for _, player in ipairs(Players:GetPlayers()) do
		saveCash(player)
	end
end)

-- ================= courier job: route of house drop-offs =================
-- Depot near spawn -> touch drop pad at each house in order -> route bonus.
local PAID_PER_LEG = 15
-- one stop per complex: first unit of each type
local ROUTE = { "TinyHouse#1", "ZenHouse#1", "AFrame#1", "ModernCube#1", "Dome#1",
	"VillaL#1", "Castle#1", "Mansion#1" }
local jobs = {} -- player -> current stop name

local function makePart(name, size, pos, color)
	local part = Instance.new("Part")
	part.Name = name
	part.Size = size
	part.Color = color
	part.Material = Enum.Material.Wood
	part.Anchored = true
	part.Position = pos
	part.Parent = workspace
	return part
end

local DEPOT_POS = Vector3.new(0, 3.5, 35) -- plaza, near spawn
makePart("CourierDepot", Vector3.new(6, 7, 6), DEPOT_POS,
	Color3.fromRGB(110, 52, 38))

local depotGui = Instance.new("BillboardGui")
depotGui.Size = UDim2.new(0, 340, 0, 100)
depotGui.StudsOffset = Vector3.new(0, 5, 0)
depotGui.AlwaysOnTop = true
depotGui.MaxDistance = 150
depotGui.Parent = workspace.CourierDepot
local depotLabel = Instance.new("TextLabel")
depotLabel.Size = UDim2.new(1, 0, 1, 0)
depotLabel.BackgroundTransparency = 1
depotLabel.TextColor3 = Color3.new(1, 1, 1)
depotLabel.TextStrokeTransparency = 0.2
depotLabel.TextScaled = true
depotLabel.Font = Enum.Font.GothamBold
depotLabel.Text = "📦 KURIR\ndekati kotak & klik untuk mulai/stop ($"
	.. PAID_PER_LEG .. "/antaran)"
depotLabel.Parent = depotGui

-- invisible drop pads in front of every house door
local dropPads = {}
for _, folder in ipairs(houseFolders()) do
	local door = folder:FindFirstChild("Door", true)
	if door and door:IsA("BasePart") then
		local pad = Instance.new("Part")
		pad.Name = "DropPad_" .. folder.Name
		pad.Size = Vector3.new(6, 0.4, 6)
		pad.Transparency = 1
		pad.Anchored = true
		pad.CanCollide = false
		pad.CFrame = door.CFrame * CFrame.new(door.Size.X / 2 + 5,
			-door.Size.Y / 2 + 0.3, -6)
		pad.Parent = folder
		dropPads[folder.Name] = pad
	end
end

local carriedBox = {} -- player -> box part
local function attachBox(player)
	if carriedBox[player] then return end
	local char = player.Character
	local head = char and char:FindFirstChild("Head")
	if not head then return end
	local box = Instance.new("Part")
	box.Name = "CarryBox"
	box.Size = Vector3.new(2.2, 2.2, 2.2)
	box.Color = Color3.fromRGB(170, 130, 80)
	box.CanCollide = false
	box.CFrame = head.CFrame * CFrame.new(0, 2.6, 0)
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = head
	weld.Part1 = box
	weld.Parent = box
	box.Parent = char
	carriedBox[player] = box
end

local function detachBox(player)
	if carriedBox[player] then
		carriedBox[player]:Destroy()
		carriedBox[player] = nil
	end
end

local jobLabel = {} -- player -> TextLabel
local function setJobText(player, text)
	local label = jobLabel[player]
	if not label and player.Parent then
		local gui = Instance.new("BillboardGui")
		gui.Size = UDim2.new(0, 380, 0, 60)
		gui.StudsOffset = Vector3.new(0, 5, 0)
		gui.AlwaysOnTop = true
		gui.Adornee = player.Character and player.Character:FindFirstChild("Head")
		gui.Parent = player.PlayerGui
		label = Instance.new("TextLabel")
		label.Size = UDim2.new(1, 0, 1, 0)
		label.BackgroundTransparency = 1
		label.TextColor3 = Color3.new(1, 1, 0.4)
		label.TextStrokeTransparency = 0.3
		label.TextScaled = true
		label.Font = Enum.Font.GothamBold
		label.Parent = gui
		jobLabel[player] = label
	end
	if label then
		label.Text = text or ""
		label.Parent.Enabled = text ~= nil
		if player.Character then
			label.Parent.Adornee = player.Character:FindFirstChild("Head")
		end
	end
end

local depotClick = Instance.new("ClickDetector")
depotClick.MaxActivationDistance = 16
depotClick.Parent = workspace.CourierDepot
depotClick.MouseClick:Connect(function(player)
	if jobs[player] then
		jobs[player] = nil
		detachBox(player)
		setJobText(player, "Kerja selesai. Uang tetap aman.")
		task.delay(3, function()
			if not jobs[player] then
				setJobText(player, nil)
			end
		end)
		return
	end
	jobs[player] = ROUTE[1]
	attachBox(player)
	setJobText(player, "📦 Antar ke: " .. ROUTE[1])
end)

for houseName, pad in pairs(dropPads) do
	pad.Touched:Connect(function(hit)
		local player = getPlayer(hit)
		if not player or jobs[player] ~= houseName then return end
		local ls = player:FindFirstChild("leaderstats")
		local cash = ls and ls:FindFirstChild("Cash")
		if not cash then return end
		local idx = table.find(ROUTE, houseName)
		local nxt = ROUTE[idx + 1]
		cash.Value += PAID_PER_LEG
		if nxt then
			jobs[player] = nxt
			attachBox(player)
			setJobText(player, "✅ +$" .. PAID_PER_LEG .. " — antar ke: " .. nxt)
		else
			cash.Value += 50 -- full-route bonus
			jobs[player] = nil
			detachBox(player)
			setJobText(player, "🎉 Rute selesai! +$" .. PAID_PER_LEG
				.. " +$50 bonus. Klik depot untuk mulai lagi.")
			task.delay(4, function()
				if not jobs[player] then
					setJobText(player, nil)
				end
			end)
		end
	end)
end

Players.PlayerRemoving:Connect(function(player)
	jobs[player] = nil
	detachBox(player)
	if jobLabel[player] then
		jobLabel[player].Parent:Destroy()
		jobLabel[player] = nil
	end
end)

-- ================= Penthouse elevator (F1 lobby / F2 suite / F3 roof) =====
do
	local folder = workspace:FindFirstChild("Penthouse")
	local cab = folder and folder:FindFirstChild("ElevatorBase", true)
	if cab then
		local FLOORS = { 0.5, 12.5, 24.5 } -- FY of each level
		local BASE_X, BASE_Z = cab.Position.X, cab.Position.Z
		local floorY = 1
		local moving = false

		local function goTo(idx)
			if moving or idx == floorY then return end
			moving = true
			local target = Vector3.new(BASE_X, FLOORS[idx] + 0.25, BASE_Z)
			local dist = math.abs(target.Y - cab.Position.Y)
			TweenService:Create(cab, TweenInfo.new(dist / 12,
				Enum.EasingStyle.Sine, Enum.EasingDirection.InOut),
				{ CFrame = CFrame.new(target) * (cab.CFrame
					- cab.Position) }):Play()
			task.delay(dist / 12 + 0.1, function()
				floorY = idx
				moving = false
			end)
		end

		-- call buttons on shaft jambs, one per floor (F3 sits by the rails)
		local folderPar = cab.Parent
		for fl, fy in ipairs(FLOORS) do
			local btn = Instance.new("Part")
			btn.Name = "ElevatorCall" .. fl
			btn.Size = Vector3.new(0.6, 1.2, 0.6)
			btn.Color = Color3.fromRGB(212, 175, 55)
			btn.Material = Enum.Material.Neon
			btn.Anchored = true
			btn.CFrame = CFrame.new(BASE_X + 2.85 * 1.75, fy + 2.2,
				BASE_Z - 3.5 * 1.75 - 0.5)
			btn.Parent = folderPar
			local click = Instance.new("ClickDetector")
			click.MaxActivationDistance = 16
			click.Parent = btn
			click.MouseClick:Connect(function()
				goTo(fl)
			end)
		end
	end
end

-- ================= gates: swing open on approach, close after =================
local gates = {}
for _, p in ipairs(workspace:GetDescendants()) do
	if p:IsA("BasePart") and p.Name == "Gate" then
		table.insert(gates, p)
	end
end
task.spawn(function()
	while true do
		local chars = {}
		for _, player in ipairs(Players:GetPlayers()) do
			local hrp = player.Character
				and player.Character:FindFirstChild("HumanoidRootPart")
			if hrp then
				table.insert(chars, hrp.Position)
			end
		end
		for _, gate in ipairs(gates) do
			local near = false
			for _, pos in ipairs(chars) do
				if (pos - gate.Position).Magnitude < 12 then
					near = true
					break
				end
			end
			if near ~= gate:GetAttribute("Open") then
				gate:SetAttribute("Open", near)
				local closed = gate:GetAttribute("ClosedCFrame")
				if not closed then
					closed = gate.CFrame
					gate:SetAttribute("ClosedCFrame", closed)
				end
				local w = gate.Size.X
				local target = near
					and closed * CFrame.new(-w / 2, 0, 0)
						* CFrame.Angles(0, math.rad(95), 0)
						* CFrame.new(w / 2, 0, 0)
					or closed
				TweenService:Create(gate, TweenInfo.new(0.4),
					{ CFrame = target }):Play()
			end
		end
		task.wait(0.3)
	end
end)

print("HouseLogic loaded")
