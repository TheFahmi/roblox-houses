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

local function loadData(player)
	if not store then return nil end
	local ok, data = pcall(function()
		return store:GetAsync("cash_" .. player.UserId)
	end)
	return ok and data or nil
end

local function saveData(player)
	if not store then return end
	local ls = player:FindFirstChild("leaderstats")
	local cash = ls and ls:FindFirstChild("Cash")
	local rep = ls and ls:FindFirstChild("Rep")
	if cash then
		local data = {
			c = cash.Value,
			r = rep and rep.Value or 0,
			cars = player:GetAttribute("OwnedCars") or "",
		}
		pcall(function()
			store:SetAsync("cash_" .. player.UserId, data)
		end)
	end
end
local saveCash = saveData -- legacy name used by older blocks

Players.PlayerAdded:Connect(function(player)
	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	local cash = Instance.new("IntValue")
	cash.Name = "Cash"
	cash.Value = 200
	cash.Parent = ls
	local rep = Instance.new("IntValue")
	rep.Name = "Rep"
	rep.Value = 0
	rep.Parent = ls
	ls.Parent = player
	local saved = loadData(player)
	if saved then
		if type(saved) == "number" then
			cash.Value = saved -- legacy save (cash only)
		else
			cash.Value = saved.c or 200
			rep.Value = saved.r or 0
			player:SetAttribute("OwnedCars", saved.cars or "")
		end
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

local pizzaJobs = {} -- pizza deliveries in progress
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

local DEPOT_POS = Vector3.new(0, 45.5, 35) -- plaza, near spawn
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

-- ================= drivable cars (replace static CarBody builds) ==========
local MAKE_CAR = nil -- set by the block below; reused by shop/police
do
	local function buildCar(folder)
		local body = folder:FindFirstChild("CarBody", true)
		local cabin = folder:FindFirstChild("CarCabin", true)
		if not (body and cabin and body:IsA("BasePart")) then
			return
		end

		-- remove static pieces; rebuild as a drivable Model at the same spot
		local color = body.Color
		local bodyCF = body.CFrame
		for _, nm in ipairs({ "CarBody", "CarCabin", "CarGlass", "CarWheel" }) do
			for _, d in ipairs(folder:GetDescendants()) do
				if d:IsA("BasePart") and d.Name == nm then
					d:Destroy()
				end
			end
		end

		local car = Instance.new("Model")
		car.Name = "DrivableCar"

		local chassis = Instance.new("Part")
		chassis.Name = "Chassis"
		chassis.Size = Vector3.new(7.5, 1, 14)
		chassis.Color = color
		chassis.Material = Enum.Material.SmoothPlastic
		chassis.CFrame = bodyCF * CFrame.new(0, 0.4, 0)
		chassis.Parent = car

		local shell = Instance.new("Part")
		shell.Name = "Shell"
		shell.Size = Vector3.new(7.5, 2.2, 14)
		shell.Color = color
		shell.Material = Enum.Material.SmoothPlastic
		shell.CFrame = chassis.CFrame * CFrame.new(0, 1.6, 0)
		shell.CanCollide = false
		shell.Parent = car

		local hood = Instance.new("Part")
		hood.Name = "Hood"
		hood.Size = Vector3.new(7.4, 1.4, 5)
		hood.Color = color
		hood.Material = Enum.Material.SmoothPlastic
		hood.CFrame = chassis.CFrame * CFrame.new(0, 1.3, -4.4)
		hood.CanCollide = false
		hood.Parent = car

		local seat = Instance.new("VehicleSeat")
		seat.Name = "DriveSeat"
		seat.Size = Vector3.new(5, 0.6, 3)
		seat.Color = Color3.fromRGB(25, 25, 28)
		seat.Material = Enum.Material.Fabric
		seat.MaxSpeed = 45
		seat.Torque = 9
		seat.TurnSpeed = 6
		seat.CFrame = chassis.CFrame * CFrame.new(0, 1.45, 1.5)
		seat.Parent = car

		-- windscreen
		local ws = Instance.new("Part")
		ws.Name = "Windscreen"
		ws.Size = Vector3.new(6.8, 2.2, 0.3)
		ws.Color = Color3.fromRGB(200, 225, 240)
		ws.Material = Enum.Material.Glass
		ws.Transparency = 0.45
		ws.CFrame = chassis.CFrame * CFrame.new(0, 3.3, -2.2)
			* CFrame.Angles(math.rad(-18), 0, 0)
		ws.CanCollide = false
		ws.Parent = car
		local hood = Instance.new("WedgePart")
		hood.Name = "Hood"
		hood.Size = Vector3.new(7.4, 1.8, 4.8)
		hood.Color = color
		hood.Material = Enum.Material.SmoothPlastic
		hood.CFrame = chassis.CFrame * CFrame.new(0, 1.9, -4.4)
		hood.Anchored = true
		hood.CanCollide = false
		hood.Parent = car
		local roof = Instance.new("Part")
		roof.Name = "Roof"
		roof.Size = Vector3.new(6.6, 0.5, 6.2)
		roof.Color = color
		roof.Material = Enum.Material.SmoothPlastic
		roof.CFrame = chassis.CFrame * CFrame.new(0, 3.6, 1.4)
		roof.Anchored = true
		roof.CanCollide = false
		roof.Parent = car
		local trunk = Instance.new("WedgePart")
		trunk.Name = "Trunk"
		trunk.Size = Vector3.new(7.4, 1.2, 2.6)
		trunk.Color = color
		trunk.Material = Enum.Material.SmoothPlastic
		trunk.CFrame = chassis.CFrame * CFrame.new(0, 1.5, 6.4)
			* CFrame.Angles(0, math.pi, 0)
		trunk.Anchored = true
		trunk.CanCollide = false
		trunk.Parent = car

		-- wheels on hinge-motors (front steer, rear drive)
		local wheelM, wheelZ = Instance.new("Model", car), {}
		for _, wx in ipairs({ -3.9, 3.9 }) do
			for _, wz in ipairs({ -4.8, 4.8 }) do
				local wheel = Instance.new("Part")
				wheel.Name = "Wheel"
				wheel.Size = Vector3.new(1.2, 3, 3)
				wheel.Color = Color3.fromRGB(35, 35, 38)
				wheel.Material = Enum.Material.SmoothPlastic
				wheel.CFrame = chassis.CFrame * CFrame.new(wx, -0.4, wz)
				wheel.Parent = wheelM
				table.insert(wheelZ, { wheel, wz < 0 })
			end
		end

		car.PrimaryPart = chassis
		car:SetAttribute("Fuel", 100)
		car.Parent = folder

		-- weld wheels via hinge constraints, chassis anchored-free setup
		local function makeHinge(wheel, isFront, wz)
			local att0 = Instance.new("Attachment")
			att0.CFrame = chassis.CFrame:ToObjectSpace(wheel.CFrame)
				* CFrame.Angles(0, isFront and math.rad(90) or 0, 0)
			att0.Parent = chassis
			local att1 = Instance.new("Attachment")
			att1.Parent = wheel
			local hinge = Instance.new("HingeConstraint")
			hinge.Attachment0 = att0
			hinge.Attachment1 = att1
			hinge.Parent = wheel
			return hinge
		end
		local driveHinges = {}
		for _, entry in ipairs(wheelZ) do
			local hinge = makeHinge(entry[1], entry[2])
			if not entry[2] then
				table.insert(driveHinges, hinge)
			end
		end

		-- drive: when a player sits, release anchors and wire throttle
		local function setPhysics(on)
			for _, p in ipairs(car:GetDescendants()) do
				if p:IsA("BasePart") then
					p.Anchored = not on
				end
			end
			if on then
				for _, h in ipairs(driveHinges) do
					h.MotorMaxAcceleration = 40
				end
			else
				for _, h in ipairs(driveHinges) do
					h.MotorMaxAcceleration = 0
					h.AngularVelocity = 0
				end
			end
		end
		setPhysics(false)

		local occupant = nil
		seat:GetPropertyChangedSignal("Occupant"):Connect(function()
			local hum = seat.Occupant
			local player = hum and Players:GetPlayerFromCharacter(hum.Parent)
			if player then
				occupant = player
				setPhysics(true)
				-- throttle loop while driven
				task.spawn(function()
					while occupant == player
						and seat.Occupant == hum do
						local throttle = seat.ThrottleFloat
						local fuel = car:GetAttribute("Fuel")
						if fuel ~= nil and fuel <= 0 then
							for _, h in ipairs(driveHinges) do
								h.AngularVelocity = 0
							end
						else
							if fuel ~= nil then
								car:SetAttribute("Fuel", math.max(0,
									fuel - math.abs(throttle) * 0.15))
							end
							for _, h in ipairs(driveHinges) do
								h.AngularVelocity = -throttle * 18
								h.MotorMaxTorque = 5e4
							end
						end
						task.wait(0.1)
					end
					setPhysics(false)
					occupant = nil
				end)
			end
		end)

		-- respawn car where it was built if abandoned far away / flipped
		task.spawn(function()
			while true do
				task.wait(30)
				if not occupant and car.Parent
					and (chassis.Position - bodyCF.Position).Magnitude > 150 then
					setPhysics(false)
					car:PivotTo(bodyCF * CFrame.new(0, 0.4, 0))
				end
			end
		end)
	end

	for _, folder in ipairs(workspace:GetChildren()) do
		if folder:IsA("Folder") and folder:FindFirstChild("CarBody", true) then
			pcall(buildCar, folder)
		end
	end

	-- parametric factory reused by the car shop / police HQ spawns
	MAKE_CAR = function(cf, color, maxSpeed, name)
		local m = Instance.new("Model")
		m.Name = name or "DrivableCar"
		local ch = Instance.new("Part")
		ch.Name = "Chassis"
		ch.Size = Vector3.new(7.5, 1, 14)
		ch.Color = color
		ch.Material = Enum.Material.SmoothPlastic
		ch.Anchored = true
		ch.CFrame = cf * CFrame.new(0, 0.4, 0)
		ch.Parent = m
		local sh = Instance.new("Part")
		sh.Name = "Shell"
		sh.Size = Vector3.new(7.5, 2.2, 14)
		sh.Color = color
		sh.Material = Enum.Material.SmoothPlastic
		sh.Anchored = true
		sh.CanCollide = false
		sh.CFrame = ch.CFrame * CFrame.new(0, 1.6, 0)
		sh.Parent = m
		local seat = Instance.new("VehicleSeat")
		seat.Name = "DriveSeat"
		seat.Size = Vector3.new(5, 0.6, 3)
		seat.Color = Color3.fromRGB(25, 25, 28)
		seat.MaxSpeed = maxSpeed or 45
		seat.Torque = 9
		seat.TurnSpeed = 6
		seat.Anchored = true
		seat.CFrame = ch.CFrame * CFrame.new(0, 1.45, 1.5)
		seat.Parent = m
		-- sloped hood (front), roof, trunk wedge — real car silhouette
		local hood = Instance.new("WedgePart")
		hood.Size = Vector3.new(7.4, 1.8, 4.8)
		hood.Color = color
		hood.Material = Enum.Material.SmoothPlastic
		hood.Anchored = true
		hood.CanCollide = false
		hood.CFrame = ch.CFrame * CFrame.new(0, 1.9, -4.4)
		hood.Parent = m
		local roof = Instance.new("Part")
		roof.Name = "Roof"
		roof.Size = Vector3.new(6.6, 0.5, 6.2)
		roof.Color = color
		roof.Material = Enum.Material.SmoothPlastic
		roof.Anchored = true
		roof.CanCollide = false
		roof.CFrame = ch.CFrame * CFrame.new(0, 3.6, 1.4)
		roof.Parent = m
		local windshield = Instance.new("Part")
		windshield.Name = "Windscreen"
		windshield.Size = Vector3.new(6.6, 2, 0.3)
		windshield.Color = Color3.fromRGB(200, 225, 240)
		windshield.Material = Enum.Material.Glass
		windshield.Transparency = 0.45
		windshield.Anchored = true
		windshield.CanCollide = false
		windshield.CFrame = ch.CFrame * CFrame.new(0, 2.9, -1.8)
			* CFrame.Angles(math.rad(-22), 0, 0)
		windshield.Parent = m
		local trunk = Instance.new("WedgePart")
		trunk.Size = Vector3.new(7.4, 1.2, 2.6)
		trunk.Color = color
		trunk.Material = Enum.Material.SmoothPlastic
		trunk.Anchored = true
		trunk.CanCollide = false
		trunk.CFrame = ch.CFrame * CFrame.new(0, 1.5, 6.4)
			* CFrame.Angles(0, math.pi, 0)
		trunk.Parent = m
		local wheels = {}
		for _, wx in ipairs({ -3.9, 3.9 }) do
			for _, wz in ipairs({ -4.8, 4.8 }) do
				local wheel = Instance.new("Part")
				wheel.Name = "Wheel"
				wheel.Size = Vector3.new(1.2, 3, 3)
				wheel.Color = Color3.fromRGB(35, 35, 38)
				wheel.CFrame = ch.CFrame * CFrame.new(wx, -0.4, wz)
				wheel.Anchored = true
				wheel.Parent = m
				table.insert(wheels, { wheel, wz < 0 })
			end
		end
		local hinges = {}
		for _, e in ipairs(wheels) do
			local a0 = Instance.new("Attachment")
			a0.CFrame = ch.CFrame:ToObjectSpace(e[1].CFrame)
			a0.Parent = ch
			local a1 = Instance.new("Attachment")
			a1.Parent = e[1]
			local hinge = Instance.new("HingeConstraint")
			hinge.Attachment0 = a0
			hinge.Attachment1 = a1
			hinge.Parent = e[1]
			table.insert(hinges, hinge)
		end
		m.PrimaryPart = ch
		m:SetAttribute("Fuel", 100)
		m:SetAttribute("MaxSpeed", seat.MaxSpeed)
		m.Parent = workspace
		seat:GetPropertyChangedSignal("Occupant"):Connect(function()
			local driven = seat.Occupant ~= nil
			for _, p in ipairs(m:GetDescendants()) do
				if p:IsA("BasePart") then
					p.Anchored = not driven
				end
			end
			if not driven then
				for _, h in ipairs(hinges) do
					h.AngularVelocity = 0
				end
				return
			end
			task.spawn(function()
				while seat.Occupant ~= nil and m.Parent do
					local fuel = m:GetAttribute("Fuel") or 0
					if fuel <= 0 then
						seat.MaxSpeed = 0
						for _, h in ipairs(hinges) do
							h.AngularVelocity = 0
						end
					else
						m:SetAttribute("Fuel",
							math.max(0, fuel - 2))
					end
					task.wait(1)
				end
			end)
		end)
		return m
	end
end

local WORLD_LIFT_Y = 42 -- platform level (level 3)

-- ================= Penthouse elevator (F1 lobby / F2 suite / F3 roof) =====
pcall(function()
	local folder = workspace:FindFirstChild("Penthouse")
	local cab = folder and folder:FindFirstChild("ElevatorBase", true)
	assert(cab, "ElevatorBase not found")
	local FLOORS = { 0.5, 12.5, 24.5 } -- FY of each level (pre-scale)
	local SCALE = 1.75 -- must match generate_houses.py
	local BASE_X, BASE_Z = cab.Position.X, cab.Position.Z
	local floorY = 1
	local moving = false
	local buttons = {}

	local function pulse()
		for _, b in ipairs(buttons) do
			local orig = b.Size
			local t1 = TweenService:Create(b, TweenInfo.new(0.18),
				{ Size = orig * 0.55 })
			t1:Play()
			t1.Completed:Once(function()
				TweenService:Create(b, TweenInfo.new(0.18),
					{ Size = orig }):Play()
			end)
		end
	end

	local function goTo(idx)
		if moving or idx == floorY then return end
		moving = true
		pulse()
		local target = Vector3.new(BASE_X,
			(FLOORS[idx] + 0.25) * SCALE + WORLD_LIFT_Y, BASE_Z)
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

	-- big call buttons on the shaft front, one per floor
	local folderPar = cab.Parent
	for fl, fy in ipairs(FLOORS) do
		local btn = Instance.new("Part")
		btn.Name = "ElevatorCall" .. fl
		btn.Size = Vector3.new(1, 1.6, 1)
		btn.Color = Color3.fromRGB(255, 200, 40)
		btn.Material = Enum.Material.Neon
		btn.Anchored = true
		btn.CFrame = CFrame.new(BASE_X + 2.85 * 1.75,
			(fy + 2.2) * SCALE + WORLD_LIFT_Y, BASE_Z - 3.5 * 1.75 - 0.8)
		btn.Parent = folderPar
		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 25
		click.Parent = btn
		click.MouseClick:Connect(function()
			goTo(fl)
		end)
		table.insert(buttons, btn)
	end

	-- fallback: prompt inside the cab cycles to the next floor
	local prompt = Instance.new("ProximityPrompt")
	prompt.ObjectText = "Lift Penthouse"
	prompt.ActionText = "Naik/Turun"
	prompt.HoldDuration = 0.3
	prompt.MaxActivationDistance = 12
	prompt.Parent = cab
	prompt.Triggered:Connect(function()
		goTo(floorY % #FLOORS + 1)
	end)
	print("Penthouse elevator ready")
end)

-- ================= traffic lights: red/yellow/green cycle =================
local trafficStates = {} -- [idx] = "R"|"Y"|"G"
do
	local groups = {}
	for _, p in ipairs(workspace:GetDescendants()) do
		if p:IsA("BasePart") and p.Name:match("^TLamp_([RYG])(%d+)$") then
			local col, idx = p.Name:match("^TLamp_([RYG])(%d+)$")
			groups[idx] = groups[idx] or { R = {}, Y = {}, G = {} }
			table.insert(groups[idx][col], p)
		end
	end
	local function setLamps(g, state)
		for col, lamps in pairs(g) do
			local on = (col == state) or (state == "RY" and (col == "R"
				or col == "Y"))
			for _, lamp in ipairs(lamps) do
				lamp.Transparency = on and 0 or 0.85
				lamp.Material = on and Enum.Material.Neon
					or Enum.Material.Glass
			end
		end
	end
	task.spawn(function()
		while true do
			for idx, g in pairs(groups) do
				local offset = (tonumber(idx) - 1) * 6
				local t = (os.clock() + offset) % 14
				local state
				if t < 6 then
					state = "G"
				elseif t < 7 then
					state = "Y"
				else
					state = "R"
				end
				trafficStates[idx] = state
				setLamps(g, state)
			end
			task.wait(0.5)
		end
	end)
end

-- ================= police patrol bot: tilang pelanggar lalu lintas ========
pcall(function()
	-- build the patrol car (anchored, rides a fixed waypoint loop)
	local POLICE_WPS = {
		Vector3.new(0, 43.2, 76.5),
		Vector3.new(-164.5, 43.2, 76.5),
		Vector3.new(-164.5, 43.2, 1298.5),
		Vector3.new(393, 43.2, 1298.5),
		Vector3.new(-164.5, 43.2, 1298.5),
		Vector3.new(-164.5, 43.2, 76.5),
	}
	local car = Instance.new("Model")
	car.Name = "PoliceCar"
	local chassis = Instance.new("Part")
	chassis.Name = "Chassis"
	chassis.Size = Vector3.new(7.5, 1, 14)
	chassis.Color = Color3.fromRGB(240, 240, 240)
	chassis.Material = Enum.Material.SmoothPlastic
	chassis.Anchored = true
	chassis.CFrame = CFrame.new(POLICE_WPS[1])
	chassis.Parent = car
	local shell = Instance.new("Part")
	shell.Name = "Shell"
	shell.Size = Vector3.new(7.5, 2.2, 14)
	shell.Color = Color3.fromRGB(240, 240, 245)
	shell.Material = Enum.Material.SmoothPlastic
	shell.Anchored = true
	shell.CanCollide = false
	shell.CFrame = chassis.CFrame * CFrame.new(0, 1.6, 0)
	shell.Parent = car
	local stripe = Instance.new("Part")
	stripe.Name = "Stripe"
	stripe.Size = Vector3.new(7.6, 1.4, 8)
	stripe.Color = Color3.fromRGB(25, 25, 28)
	stripe.Material = Enum.Material.SmoothPlastic
	stripe.Anchored = true
	stripe.CanCollide = false
	stripe.CFrame = chassis.CFrame * CFrame.new(0, 1.6, 2)
	stripe.Parent = car
	local hood = Instance.new("WedgePart")
	hood.Name = "Hood"
	hood.Size = Vector3.new(7.4, 1.8, 4.8)
	hood.Color = Color3.fromRGB(240, 240, 245)
	hood.Material = Enum.Material.SmoothPlastic
	hood.Anchored = true
	hood.CanCollide = false
	hood.CFrame = chassis.CFrame * CFrame.new(0, 1.9, -4.4)
	hood.Parent = car
	local roof = Instance.new("Part")
	roof.Name = "Roof"
	roof.Size = Vector3.new(6.6, 0.5, 6.2)
	roof.Color = Color3.fromRGB(240, 240, 245)
	roof.Material = Enum.Material.SmoothPlastic
	roof.Anchored = true
	roof.CanCollide = false
	roof.CFrame = chassis.CFrame * CFrame.new(0, 3.6, 1.4)
	roof.Parent = car
	local barR = Instance.new("Part")
	barR.Name = "PoliceBarR"
	barR.Size = Vector3.new(1.4, 0.8, 2.6)
	barR.Color = Color3.fromRGB(255, 40, 40)
	barR.Material = Enum.Material.Neon
	barR.Anchored = true
	barR.CanCollide = false
	barR.CFrame = chassis.CFrame * CFrame.new(-1, 3.2, 0)
	barR.Parent = car
	local barB = Instance.new("Part")
	barB.Name = "PoliceBarB"
	barB.Size = Vector3.new(1.4, 0.8, 2.6)
	barB.Color = Color3.fromRGB(40, 60, 255)
	barB.Material = Enum.Material.Neon
	barB.Anchored = true
	barB.CanCollide = false
	barB.CFrame = chassis.CFrame * CFrame.new(1, 3.2, 0)
	barB.Parent = car
	local tag = Instance.new("BillboardGui")
	tag.Size = UDim2.new(0, 140, 0, 40)
	tag.StudsOffset = Vector3.new(0, 4.4, 0)
	tag.AlwaysOnTop = true
	tag.MaxDistance = 180
	tag.Parent = shell
	local tagL = Instance.new("TextLabel")
	tagL.Size = UDim2.new(1, 0, 1, 0)
	tagL.BackgroundTransparency = 0.35
	tagL.BackgroundColor3 = Color3.new(0, 0, 0)
	tagL.TextColor3 = Color3.fromRGB(120, 180, 255)
	tagL.TextScaled = true
	tagL.Font = Enum.Font.GothamBold
	tagL.Text = "POLISI"
	tagL.Parent = tag
	car.PrimaryPart = chassis
	car.Parent = workspace

	-- light bar flash
	task.spawn(function()
		while true do
			local on = (os.clock() % 0.8) < 0.4
			barR.Transparency = on and 0 or 0.6
			barB.Transparency = on and 0.6 or 0
			task.wait(0.2)
		end
	end)

	-- patrol: tween between waypoints at fixed speed (ping-pong)
	task.spawn(function()
		local SPEED = 32
		local i, dir = 1, 1
		while true do
			local ni = i + dir
			if ni < 1 or ni > #POLICE_WPS then
				dir = -dir
				ni = i + dir
			end
			local a, b = POLICE_WPS[i], POLICE_WPS[ni]
			local dist = (b - a).Magnitude
			chassis.CFrame = CFrame.lookAt(a, Vector3.new(b.X, a.Y, b.Z))
			shell.CFrame = chassis.CFrame * CFrame.new(0, 1.6, 0)
			stripe.CFrame = chassis.CFrame * CFrame.new(0, 1.6, 2)
			hood.CFrame = chassis.CFrame * CFrame.new(0, 1.9, -4.4)
			roof.CFrame = chassis.CFrame * CFrame.new(0, 3.6, 1.4)
			barR.CFrame = chassis.CFrame * CFrame.new(-1, 3.2, 0)
			barB.CFrame = chassis.CFrame * CFrame.new(1, 3.2, 0)
			local dest = CFrame.lookAt(b,
				Vector3.new(b.X, b.Y, b.Z + (b.Z - a.Z)))
			local t = TweenService:Create(chassis,
				TweenInfo.new(dist / SPEED, Enum.EasingStyle.Linear),
				{ CFrame = dest })
			t:Play()
			t.Completed:Wait()
			shell.CFrame = dest * CFrame.new(0, 1.6, 0)
			stripe.CFrame = dest * CFrame.new(0, 1.6, 2)
			hood.CFrame = dest * CFrame.new(0, 1.9, -4.4)
			roof.CFrame = dest * CFrame.new(0, 3.6, 1.4)
			barR.CFrame = dest * CFrame.new(-1, 3.2, 0)
			barB.CFrame = dest * CFrame.new(1, 3.2, 0)
			i = ni
		end
	end)

	-- enforcement: speeding near patrol & running the red light
	local fines = {} -- player -> os.clock() of last fine
	local function tilang(player, amount, reason)
		local now = os.clock()
		if fines[player] and now - fines[player] < 20 then return end
		fines[player] = now
		local ls = player:FindFirstChild("leaderstats")
		local cash = ls and ls:FindFirstChild("Cash")
		if cash then
			cash.Value = math.max(0, cash.Value - amount)
		end
		local vrep = ls and ls:FindFirstChild("Rep")
		if vrep then
			vrep.Value = math.max(0, vrep.Value - 1)
		end
		local gui = Instance.new("BillboardGui")
		gui.Size = UDim2.new(0, 320, 0, 70)
		gui.StudsOffset = Vector3.new(0, 5.4, 0)
		gui.AlwaysOnTop = true
		gui.Parent = shell
		local l = Instance.new("TextLabel")
		l.Size = UDim2.new(1, 0, 1, 0)
		l.BackgroundColor3 = Color3.fromRGB(120, 20, 20)
		l.BackgroundTransparency = 0.2
		l.TextColor3 = Color3.new(1, 1, 1)
		l.TextScaled = true
		l.Font = Enum.Font.GothamBold
		l.Text = "TILANG! " .. reason .. " — denda $" .. amount
		l.Parent = gui
		task.delay(4, function()
			gui:Destroy()
		end)
	end

	task.spawn(function()
		while true do
			task.wait(0.4)
			for _, p in ipairs(workspace:GetDescendants()) do
				if p:IsA("VehicleSeat") and p.Occupant then
					local player = Players:GetPlayerFromCharacter(
						p.Occupant.Parent)
					local hrp = p.Occupant.Parent
						and p.Occupant.Parent:FindFirstChild(
							"HumanoidRootPart")
					if player and hrp
						and (chassis.Position - hrp.Position).Magnitude
							< 90 then
						local speed = hrp.AssemblyLinearVelocity.Magnitude
						if speed > 42 then
							tilang(player, 150, "Ngebut")
						end
						local lightDist = (hrp.Position
							- Vector3.new(-164.5, 47, 76.5)).Magnitude
						if lightDist < 55 and trafficStates[1] == "R"
							and speed > 6 then
							tilang(player, 200, "Lampu merah")
						end
					end
				end
			end
		end
	end)
end)

-- ================= CITY: shops, jobs, interiors, NPCs =====================
pcall(function()
	local CityFolder = workspace:FindFirstChild("CityBlock")

	-- helper: heal + effects
	local function heal(player, full)
		local char = player.Character
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if hum then
			hum.Health = full and hum.MaxHealth
				or math.min(hum.MaxHealth, hum.Health + 25)
		end
	end

	local function carryItem(player, color, seconds)
		local char = player.Character
		local head = char and char:FindFirstChild("Head")
		if not head then return end
		local item = Instance.new("Part")
		item.Size = Vector3.new(1.6, 1.6, 1.6)
		item.Color = color
		item.CanCollide = false
		item.CFrame = head.CFrame * CFrame.new(0, 2.4, 0)
		local weld = Instance.new("WeldConstraint")
		weld.Part0 = head
		weld.Part1 = item
		weld.Parent = item
		item.Parent = char
		task.delay(seconds or 3, function()
			item:Destroy()
		end)
	end

	local function pay(player, amount)
		local ls = player:FindFirstChild("leaderstats")
		local cash = ls and ls:FindFirstChild("Cash")
		if not cash or cash.Value < amount then
			return false
		end
		cash.Value -= amount
		return true
	end

	-- ---------- car shop ----------
	local CAR_MODELS = {
		{ "Kota", 800, 40, Color3.fromRGB(120, 180, 220) },
		{ "Truk", 1500, 35, Color3.fromRGB(90, 90, 96) },
		{ "Sport", 2500, 60, Color3.fromRGB(220, 50, 50) },
		{ "SUV", 3000, 45, Color3.fromRGB(60, 90, 60) },
		{ "Mewah", 5000, 55, Color3.fromRGB(212, 175, 55) },
	}
	local spawnedCar = {} -- player -> model
	local function despawnOwned(player)
		if spawnedCar[player] then
			spawnedCar[player]:Destroy()
			spawnedCar[player] = nil
		end
	end
	Players.PlayerRemoving:Connect(despawnOwned)

	local function ownsCar(player, id)
		local owned = player:GetAttribute("OwnedCars") or ""
		return ("," .. owned .. ","):find("," .. id .. ",") ~= nil
	end
	local function addOwnedCar(player, id)
		local owned = player:GetAttribute("OwnedCars") or ""
		player:SetAttribute("OwnedCars", owned .. "," .. id)
		saveData(player)
	end

	local shopPadA = CityFolder and CityFolder:FindFirstChild("ShopPad-6")
	local shopPadB = CityFolder and CityFolder:FindFirstChild("ShopPad6")
	for i, def in ipairs(CAR_MODELS) do
		local pad = Instance.new("Part")
		pad.Name = "CarBuyPad" .. i
		pad.Size = Vector3.new(2.6, 1.4, 0.6)
		pad.Color = Color3.fromRGB(255, 200, 40)
		pad.Material = Enum.Material.Neon
		pad.Anchored = true
		pad.CFrame = CFrame.new(60, 4.6, -22)
			* CFrame.new(-6 + (i - 1) * 3, 0, 0)
		pad.Parent = CityFolder
		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 18
		click.Parent = pad
		click.MouseClick:Connect(function(player)
			local id, price, spd, col = def[1], def[2], def[3], def[4]
			if not ownsCar(player, id) then
				if not pay(player, price) then return end
				addOwnedCar(player, id)
			end
			despawnOwned(player)
			local padCF = (i % 2 == 0) and shopPadA or shopPadB
			local base = padCF and padCF.CFrame
				or CFrame.new(60, 0.5, -18)
			spawnedCar[player] = MAKE_CAR(base * CFrame.new(0, 0.3, 0),
				col, spd, "Car_" .. player.Name)
		end)
	end

	-- ---------- cafe & grocery ----------
	local FOODS = {
		{ "CafeCounter", "Nasi Goreng", 15, Color3.fromRGB(230, 160, 60) },
		{ "CafeCounter", "Burger", 20, Color3.fromRGB(190, 120, 60) },
		{ "CafeCounter", "Kopi", 10, Color3.fromRGB(90, 55, 30) },
		{ "GroceryCounter", "Snack", 8, Color3.fromRGB(240, 200, 60) },
		{ "GroceryCounter", "Soda", 10, Color3.fromRGB(220, 60, 60) },
	}
	for _, def in ipairs(FOODS) do
		local counter = CityFolder and CityFolder:FindFirstChild(def[1])
		if counter then
			local pad = Instance.new("Part")
			pad.Size = Vector3.new(1.8, 1, 0.5)
			pad.Color = Color3.fromRGB(255, 200, 40)
			pad.Material = Enum.Material.Neon
			pad.Anchored = true
			pad.CFrame = counter.CFrame * CFrame.new(0, 2.6, 0)
			pad.Parent = counter.Parent
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = def[2] .. " ($" .. def[3] .. ")"
			prompt.ObjectText = "Makanan"
			prompt.HoldDuration = 0.3
			prompt.Parent = pad
			prompt.Triggered:Connect(function(player)
				if not pay(player, def[3]) then return end
				carryItem(player, def[4], 3)
				task.delay(3, function()
					if def[2] == "Kopi" then
						local hum = player.Character
							and player.Character:FindFirstChildOfClass(
								"Humanoid")
						if hum then
							hum.WalkSpeed = 22
							task.delay(30, function()
								if hum.Parent then
									hum.WalkSpeed = 16
								end
							end)
						end
					else
						heal(player, true)
					end
				end)
			end)
		end
	end

	-- ---------- hospital ----------
	local hospDesk = CityFolder and CityFolder:FindFirstChild("HospDesk")
	if hospDesk then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Berobat ($50)"
		prompt.ObjectText = "Rumah Sakit"
		prompt.HoldDuration = 0.3
		prompt.Parent = hospDesk
		prompt.Triggered:Connect(function(player)
			if pay(player, 50) then
				heal(player, true)
			end
		end)
	end

	-- ---------- pizza job ----------
	local pizzaCounter = CityFolder and CityFolder:FindFirstChild(
		"PizzaCounter")
	if pizzaCounter then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Antar Pizza"
		prompt.ObjectText = "Pizza Kota ($40/antar)"
		prompt.HoldDuration = 0.3
		prompt.Parent = pizzaCounter
		prompt.Triggered:Connect(function(player)
			if jobs[player] then return end
			if pizzaJobs[player] then return end
			local names = {}
			for houseName in pairs(dropPads) do
				table.insert(names, houseName)
			end
			if #names == 0 then return end
			local target = names[math.random(#names)]
			pizzaJobs[player] = { target = target, left = 5, earned = 0 }
			carryItem(player, Color3.fromRGB(200, 170, 110), 600)
			setJobText(player, "Antar pizza ke: " .. target)
		end)
	end

	-- ---------- bus at the depot ----------
	local depotPart = workspace:FindFirstChild("CourierDepot")
	if depotPart then
		local bus = Instance.new("Model")
		bus.Name = "CityBus"
		local ch = Instance.new("Part")
		ch.Size = Vector3.new(9, 43.2, 30)
		ch.Color = Color3.fromRGB(70, 130, 200)
		ch.Anchored = true
		ch.CFrame = CFrame.new(30, 43.6, 76.5)
		ch.Parent = bus
		local sh = Instance.new("Part")
		sh.Size = Vector3.new(9, 4, 30)
		sh.Color = Color3.fromRGB(70, 130, 200)
		sh.Anchored = true
		sh.CanCollide = false
		sh.CFrame = ch.CFrame * CFrame.new(0, 2.6, 0)
		sh.Parent = bus
		local seat = Instance.new("VehicleSeat")
		seat.Size = Vector3.new(4, 0.6, 3)
		seat.MaxSpeed = 32
		seat.Torque = 12
		seat.TurnSpeed = 4
		seat.Anchored = true
		seat.CFrame = ch.CFrame * CFrame.new(0, 1.2, -12)
		seat.Parent = bus
		for row = 0, 2 do
			for side = -1, 1, 2 do
				local s = Instance.new("Seat")
				s.Size = Vector3.new(2.6, 0.5, 2.6)
				s.Color = Color3.fromRGB(60, 60, 70)
				s.Anchored = true
				s.CFrame = ch.CFrame * CFrame.new(side * 2.4, 1.2,
					-4 + row * 5)
				s.Parent = bus
			end
		end
		bus.PrimaryPart = ch
		bus.Parent = workspace
		seat:GetPropertyChangedSignal("Occupant"):Connect(function()
			local driven = seat.Occupant ~= nil
			for _, p in ipairs(bus:GetDescendants()) do
				if p:IsA("BasePart") then
					p.Anchored = not driven
				end
			end
		end)
	end

	-- ---------- player police duty ----------
	local hqDesk = CityFolder and CityFolder:FindFirstChild("HQDesk")
	local hqPad = CityFolder and CityFolder:FindFirstChild("HQGaragePad")
	local dutyTag = {}
	local dutyCar = {}
	local function setDuty(player, on)
		local char = player.Character
		local head = char and char:FindFirstChild("Head")
		if on then
			onDuty[player] = true
			if head then
				local gui = Instance.new("BillboardGui")
				gui.Name = "DutyTag"
				gui.Size = UDim2.new(0, 120, 0, 34)
				gui.StudsOffset = Vector3.new(0, 2.2, 0)
				gui.AlwaysOnTop = true
				gui.Parent = head
				local l = Instance.new("TextLabel")
				l.Size = UDim2.new(1, 0, 1, 0)
				l.BackgroundTransparency = 0.3
				l.BackgroundColor3 = Color3.fromRGB(30, 40, 90)
				l.TextColor3 = Color3.new(1, 1, 1)
				l.TextScaled = true
				l.Font = Enum.Font.GothamBold
				l.Text = "POLISI"
				l.Parent = gui
				dutyTag[player] = gui
			end
			if hqPad and MAKE_CAR then
				dutyCar[player] = MAKE_CAR(hqPad.CFrame
					* CFrame.new(0, 0.3, 0),
					Color3.fromRGB(240, 240, 245), 55,
					"PoliceCar_" .. player.Name)
			end
			local tool = Instance.new("Tool")
			tool.Name = "Tilang"
			tool.RequiresHandle = true
			local handle = Instance.new("Part")
			handle.Name = "Handle"
			handle.Size = Vector3.new(0.6, 1.6, 0.4)
			handle.Color = Color3.fromRGB(120, 20, 20)
			handle.Parent = tool
			tool.Parent = player.Backpack
			tool.Activated:Connect(function()
				local myHRP = player.Character
					and player.Character:FindFirstChild(
						"HumanoidRootPart")
				if not myHRP then return end
				for _, other in ipairs(Players:GetPlayers()) do
					local skip = other == player or not other.Character
					if not skip then
						local oHRP = other.Character:FindFirstChild(
							"HumanoidRootPart")
						if oHRP and (oHRP.Position
							- myHRP.Position).Magnitude < 25 then
						local ls = other:FindFirstChild("leaderstats")
						local cash = ls and ls:FindFirstChild("Cash")
						if cash then
							cash.Value = math.max(0, cash.Value - 120)
							local myLs = player:FindFirstChild("leaderstats")
							local myCash = myLs
								and myLs:FindFirstChild("Cash")
							if myCash then
								myCash.Value += 40
							end
							local vrep = ls:FindFirstChild("Rep")
							if vrep then
								vrep.Value = math.max(0, vrep.Value - 1)
							end
						end
						break
					end
					end
				end
			end)
			tool.Parent = player.Character or player:WaitForChild("Backpack")
		else
			onDuty[player] = nil
			if dutyTag[player] then
				dutyTag[player]:Destroy()
				dutyTag[player] = nil
			end
			if dutyCar[player] then
				dutyCar[player]:Destroy()
				dutyCar[player] = nil
			end
			local bp = player:FindFirstChild("Backpack")
			local t = bp and bp:FindFirstChild("Tilang")
			if t then t:Destroy() end
			local ct = player.Character
			and player.Character:FindFirstChild("Tilang")
			if ct then ct:Destroy() end
		end
	end
	if hqDesk then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Jadilah Polisi"
		prompt.ObjectText = "Kantor Polisi"
		prompt.HoldDuration = 0.5
		prompt.Parent = hqDesk
		prompt.Triggered:Connect(function(player)
			setDuty(player, not onDuty[player])
			prompt.ActionText = onDuty[player] and "Lepas seragam"
				or "Jadilah Polisi"
		end)
	end
	Players.PlayerRemoving:Connect(function(player)
		setDuty(player, false)
		despawnOwned(player)
	end)

	-- ---------- interiors: sleep / TV / shower / light switch ----------
	for _, folder in ipairs(workspace:GetChildren()) do
		if folder:IsA("Folder") and folder.Name ~= "Shared"
			and folder.Name ~= "CityBlock" then
		-- light switch near the front door
		local door = folder:FindFirstChild("Door", true)
		if door then
			local switch = Instance.new("Part")
			switch.Name = "LightSwitch"
			switch.Size = Vector3.new(0.4, 1, 0.5)
			switch.Color = Color3.fromRGB(240, 240, 240)
			switch.Anchored = true
			switch.CFrame = door.CFrame * CFrame.new(
				door.Size.X / 2 + 2.2, 2.5, 3)
			switch.Parent = folder
			local light = Instance.new("PointLight")
			light.Brightness = 0.6
			light.Range = 45
			light.Color = Color3.fromRGB(255, 230, 180)
			light.Enabled = false
			light.Parent = switch
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = "Saklar Lampu"
			prompt.HoldDuration = 0.2
			prompt.Parent = switch
			prompt.Triggered:Connect(function(player)
				light.Enabled = not light.Enabled
			end)
		end
		-- per-floor ceiling light follows the switch
		for _, p in ipairs(folder:GetDescendants()) do
			if p:IsA("BasePart") and (p.Name == "LightSwitch") then
				local pl = p:FindFirstChildOfClass("PointLight")
				if pl then
					local conn
					conn = pl:GetPropertyChangedSignal("Enabled")
						:Connect(function()
							for _, sib in ipairs(
								folder:GetDescendants()) do
								if sib:IsA("PointLight")
									and sib ~= pl then
									sib.Enabled = pl.Enabled
								end
							end
						end)
				end
			end
		end
		-- sleep on beds (owner only)
		for _, p in ipairs(folder:GetDescendants()) do
			if p:IsA("BasePart") and p.Name == "BedBase" then
				local prompt = Instance.new("ProximityPrompt")
				prompt.ActionText = "Tidur"
				prompt.ObjectText = "Kasur"
				prompt.HoldDuration = 0.4
				prompt.Parent = p
				prompt.Triggered:Connect(function(player)
					if folder:GetAttribute("OwnerId")
						and folder:GetAttribute("OwnerId")
							~= player.UserId then
						return
					end
					local char = player.Character
					local hrp = char and char:FindFirstChild(
						"HumanoidRootPart")
					local hum = char
						and char:FindFirstChildOfClass("Humanoid")
					if not hrp or not hum then return end
					local oldCF = hrp.CFrame
					hrp.CFrame = p.CFrame * CFrame.new(0, 3, 0)
						* CFrame.Angles(math.rad(-90), 0, 0)
					hrp.Anchored = true
					local gui = Instance.new("ScreenGui")
					gui.Name = "SleepFade"
					gui.Parent = player:WaitForChild("PlayerGui", 3)
					local fade = Instance.new("Frame")
					fade.Size = UDim2.new(1, 0, 1, 0)
					fade.BackgroundColor3 = Color3.new(0, 0, 0)
					fade.BackgroundTransparency = 1
					fade.Parent = gui
					TweenService:Create(fade, TweenInfo.new(0.8),
						{ BackgroundTransparency = 0.25 }):Play()
					heal(player, true)
					task.delay(4, function()
						hrp.Anchored = false
						hrp.CFrame = oldCF
						TweenService:Create(fade, TweenInfo.new(0.5),
							{ BackgroundTransparency = 1 }):Play()
						task.delay(0.6, function()
							gui:Destroy()
						end)
					end)
				end)
			end
			-- TV channels
			if p:IsA("BasePart") and p.Name == "TV" then
				local channels = {
					{ "Berita", Color3.fromRGB(60, 90, 160) },
					{ "Olahraga", Color3.fromRGB(50, 150, 70) },
					{ "Film", Color3.fromRGB(160, 40, 40) },
					{ "Kartun", Color3.fromRGB(240, 180, 40) },
					{ "Musik", Color3.fromRGB(140, 60, 180) },
				}
				local chIdx = 0
				local panel = p.Parent and p.Parent:FindFirstChild("TVPanel")
				local prompt = Instance.new("ProximityPrompt")
				prompt.ActionText = "Ganti Channel"
				prompt.ObjectText = "TV"
				prompt.HoldDuration = 0.2
				prompt.Parent = p
				prompt.Triggered:Connect(function(player)
					if folder:GetAttribute("OwnerId")
						and folder:GetAttribute("OwnerId")
							~= player.UserId then
						return
					end
					chIdx = chIdx % #channels + 1
					if panel then
						panel.Color = channels[chIdx][2]
					end
					prompt.ActionText = "Channel: "
						.. channels[chIdx][1]
				end)
			end
			-- shower
			if p:IsA("BasePart") and p.Name == "Shower" then
				local prompt = Instance.new("ProximityPrompt")
				prompt.ActionText = "Mandi"
				prompt.HoldDuration = 0.3
				prompt.Parent = p
				prompt.Triggered:Connect(function(player)
					if folder:GetAttribute("OwnerId")
						and folder:GetAttribute("OwnerId")
							~= player.UserId then
						return
					end
					heal(player, false)
					local p2 = Instance.new("ParticleEmitter")
					p2.Texture = "rbxasset://textures/particles/sparkles_main.dds"
					p2.Rate = 40
					p2.Lifetime = NumberRange.new(0.5)
					p2.Speed = NumberRange.new(6)
					p2.Color = ColorSequence.new(Color3.fromRGB(160,
						210, 255))
					p2.Parent = p
					task.delay(3, function()
						p2.Enabled = false
					end)
				end)
			end
		end
		end
	end

	-- ---------- NPC dialogs ----------
	local CITY_CENTERS = {
		{ Vector3.new(105, 3, -31.5), { "Selamat datang di Toko Mobil!",
			"Mau beli mobil? Klik tombol kuning di counter." } },
		{ Vector3.new(183.75, 3, -31.5), { "Kopi kami paling enak!",
			"Kopi bikin kamu lari cepat 30 detik loh." } },
		{ Vector3.new(259, 3, -31.5), { "Banyak snack murah hari ini!",
			"Semuanya di bawah $10." } },
		{ Vector3.new(105, 3, 42), { "Yang sakit? Sini saya bantu.",
			"Berobat cuma $50." } },
		{ Vector3.new(183.75, 3, 42), { "Hukum harus ditegakkan!",
			"Jadi polisi lewat pad seragam di samping." } },
		{ Vector3.new(259, 3, 42), { "Pizza panas dari tanur!",
			"Kerja antar pizza, gajinya besar." } },
	}
	for _, p in ipairs(workspace:GetDescendants()) do
		if p:IsA("BasePart") and p.Name == "NPCTorso" then
			local best, bestD = nil, math.huge
			for _, c in ipairs(CITY_CENTERS) do
				local d = (Vector3.new(p.Position.X, 3, p.Position.Z)
					- c[1]).Magnitude
				if d < bestD then
					best, bestD = c, d
				end
			end
			if best then
				local lines = best[2]
				local i = 0
				local prompt = Instance.new("ProximityPrompt")
				prompt.ActionText = "Bicara"
				prompt.ObjectText = "Warga"
				prompt.HoldDuration = 0.2
				prompt.Parent = p
				local gui = Instance.new("BillboardGui")
				gui.Size = UDim2.new(0, 240, 0, 50)
				gui.StudsOffset = Vector3.new(0, 3.4, 0)
				gui.AlwaysOnTop = true
				gui.Enabled = false
				gui.Parent = p
				local l = Instance.new("TextLabel")
				l.Size = UDim2.new(1, 0, 1, 0)
				l.BackgroundColor3 = Color3.new(0, 0, 0)
				l.BackgroundTransparency = 0.4
				l.TextColor3 = Color3.new(1, 1, 1)
				l.TextScaled = true
				l.Font = Enum.Font.Gotham
				l.Parent = gui
				prompt.Triggered:Connect(function()
					i = i % #lines + 1
					l.Text = lines[i]
					gui.Enabled = true
					task.delay(4, function()
						gui.Enabled = false
					end)
				end)
			end
		end
	end

	-- ---------- gas station: refuel ----------
	local function findCar(player)
		local char = player.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart")
		if not hrp then return nil end
		local best, bestD = nil, 25
		for _, m in ipairs(workspace:GetDescendants()) do
			if m:IsA("Model")
				and (m.Name:match("^Car_") or m.Name == "DrivableCar")
				and m:GetAttribute("Fuel") ~= nil then
				local pp = m.PrimaryPart
					or m:FindFirstChildWhichIsA("BasePart")
				if pp then
					local d = (pp.Position - hrp.Position).Magnitude
					if d < bestD then
						best, bestD = m, d
					end
				end
			end
		end
		return best
	end
	if CityFolder then
		for _, pump in ipairs(CityFolder:GetChildren()) do
			if pump.Name == "GasPump" then
				local prompt = Instance.new("ProximityPrompt")
				prompt.ActionText = "Isi Bensin ($25)"
				prompt.ObjectText = "Pom Bensin"
				prompt.HoldDuration = 0.4
				prompt.Parent = pump
				prompt.Triggered:Connect(function(player)
					local carModel = findCar(player)
					if not carModel then return end
					if not pay(player, 25) then return end
					carModel:SetAttribute("Fuel", 100)
					local seat = carModel:FindFirstChildWhichIsA(
						"VehicleSeat", true)
					if seat then
						seat.MaxSpeed = carModel:GetAttribute(
							"MaxSpeed") or seat.MaxSpeed
					end
				end)
			end
		end
	end

	-- ---------- workshop: repair ----------
	local wPad = CityFolder and CityFolder:FindFirstChild("WorkshopPad")
	if wPad then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Perbaiki Mobil ($50)"
		prompt.ObjectText = "Bengkel"
		prompt.HoldDuration = 0.4
		prompt.Parent = wPad
		prompt.Triggered:Connect(function(player)
			local carModel = findCar(player)
			if not carModel then return end
			if not pay(player, 50) then return end
			carModel:SetAttribute("Fuel", 100)
			local seat = carModel:FindFirstChildWhichIsA("VehicleSeat",
				true)
			if seat then
				seat.MaxSpeed = carModel:GetAttribute("MaxSpeed")
					or 45
			end
			carModel:PivotTo(wPad.CFrame * CFrame.new(0, 1.4, 0)
				* CFrame.Angles(0, math.rad(90), 0))
		end)
	end

	-- ---------- bank: salary ----------
	local atm = CityFolder and CityFolder:FindFirstChild("BankATM")
	if atm then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Klaim Gaji ($100 / 5 menit)"
		prompt.ObjectText = "Bank Kota"
		prompt.HoldDuration = 0.4
		prompt.Parent = atm
		local lastClaim = {}
		prompt.Triggered:Connect(function(player)
			local now = os.clock()
			if lastClaim[player] and now - lastClaim[player] < 300 then
				return
			end
			lastClaim[player] = now
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if cash then
				cash.Value += 100
			end
		end)
	end

	-- ---------- hotel: paid sleep ----------
	local hotelDesk = CityFolder and CityFolder:FindFirstChild("HotelDesk")
	if hotelDesk then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Menginap ($30)"
		prompt.ObjectText = "Hotel Kota"
		prompt.HoldDuration = 0.4
		prompt.Parent = hotelDesk
		prompt.Triggered:Connect(function(player)
			if not pay(player, 30) then return end
			heal(player, true)
			local char = player.Character
			local hum = char and char:FindFirstChildOfClass("Humanoid")
			if hum then
				hum.WalkSpeed = 0
				task.wait(2)
				if hum.Parent then
					hum.WalkSpeed = 16
				end
			end
		end)
	end

	-- ---------- underground station elevator ----------
	local cab2 = workspace:FindFirstChild("LiftCab", true)
	if cab2 then
		local stops = { 3.75, 42 }
		local floorY = 1
		local moving = false
		local walls = {}
		for _, p in ipairs(cab2.Parent:GetChildren()) do
			if p.Name == "LiftCabWall" then
				table.insert(walls, p)
			end
		end
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Naik ke Kota"
		prompt.ObjectText = "Lift Stasiun"
		prompt.HoldDuration = 0.3
		prompt.Parent = cab2
		prompt.Triggered:Connect(function()
			if moving then return end
			moving = true
			local nxt = floorY == 1 and 2 or 1
			local delta = Vector3.new(0, stops[nxt] - stops[floorY], 0)
			local dur = math.abs(delta.Y) / 14
			TweenService:Create(cab2, TweenInfo.new(dur),
				{ CFrame = cab2.CFrame + delta }):Play()
			for _, w in ipairs(walls) do
				TweenService:Create(w, TweenInfo.new(dur),
					{ CFrame = w.CFrame + delta }):Play()
			end
			prompt.ActionText = nxt == 2 and "Turun ke Stasiun"
				or "Naik ke Kota"
			task.delay(dur + 0.1, function()
				floorY = nxt
				moving = false
			end)
		end)
	end

	-- ---------- music scaffold ----------
	local MUSIC_ID = "" -- isi asset ID musik sendiri (mis. "rbxassetid://...")
	if MUSIC_ID ~= "" then
		local s = Instance.new("Sound")
		s.SoundId = MUSIC_ID
		s.Looped = true
		s.Volume = 0.4
		s.Parent = workspace.SpawnLocation or workspace
		s:Play()
	end
end)

-- ================= delivery rep + streetlight night mode =================
pcall(function()
	-- Rep for courier legs (pizza rep is handled in its own handler below)
	for houseName, pad in pairs(dropPads) do
		pad.Touched:Connect(function(hit)
			local player = getPlayer(hit)
			if not player or jobs[player] ~= houseName then return end
			local ls = player:FindFirstChild("leaderstats")
			local rep = ls and ls:FindFirstChild("Rep")
			if rep then
				rep.Value += 2
			end
		end)
	end

	-- pizza deliveries via the same drop pads
	for houseName, pad in pairs(dropPads) do
		pad.Touched:Connect(function(hit)
			local player = getPlayer(hit)
			if not player then return end
			local pj = pizzaJobs[player]
			if not pj or pj.target ~= houseName then return end
			local ls = player:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if not cash then return end
			cash.Value += 40
			local rep = ls and ls:FindFirstChild("Rep")
			if rep then
				rep.Value += 2
			end
			pj.left -= 1
			if pj.left <= 0 then
				cash.Value += 150
				pizzaJobs[player] = nil
				detachBox(player)
				setJobText(player,
					"Semua pizza terkirim! +$150 bonus")
				task.delay(4, function()
					if not pizzaJobs[player] then
						setJobText(player, nil)
					end
				end)
			else
				local names = {}
				for hn in pairs(dropPads) do
					table.insert(names, hn)
				end
				pj.target = names[math.random(#names)]
				setJobText(player,
					"+$40 — antar ke: " .. pj.target)
			end
		end)
	end

	-- streetlights: on at night, off at day
	local bulbs = {}
	for _, p in ipairs(workspace:GetDescendants()) do
		if p:IsA("BasePart") and p.Name == "StreetLightBulb" then
			local light = Instance.new("PointLight")
			light.Brightness = 1.4
			light.Range = 34
			light.Color = Color3.fromRGB(255, 225, 160)
			light.Enabled = false
			light.Parent = p
			table.insert(bulbs, { p, light })
		end
	end
	task.spawn(function()
		while true do
			local hour = Lighting.ClockTime
			local night = hour < 6 or hour > 18
			for _, entry in ipairs(bulbs) do
				entry[1].Material = night and Enum.Material.Neon
					or Enum.Material.Glass
				entry[2].Enabled = night
			end
			task.wait(2)
		end
	end)
end)

-- ================= metro: moving train between 4 stations ================
local metroInfo = { at = 1, phase = "dwell", eta = 6, target = 2 }
pcall(function()
	local trainParts = {}
	for _, p in ipairs(workspace:GetDescendants()) do
		if p:IsA("BasePart") and p.Name:match("^Train") then
			table.insert(trainParts, p)
		end
	end

	local STOPS = {
		{ "Selatan", -323.75 },
		{ "Plaza", -26.25 },
		{ "Timur", 253.75 },
		{ "Utara", 551.25 },
	}
	local SPEED = 34
	local DWELL = 8

	local function trainX()
		for _, p in ipairs(trainParts) do
			if p.Name == "TrainCar" then
				return p.CFrame.X
			end
		end
	end

	local moving = false
	local function goToStop(idx, departBoard)
		if moving then return end
		moving = true
		local delta = Vector3.new(STOPS[idx][2] - trainX(), 0, 0)
		local dur = math.abs(delta.X) / SPEED
		metroInfo.phase = "moving"
		metroInfo.target = idx
		metroInfo.eta = dur
		metroInfo.etaAt = os.clock() + dur
		for _, p in ipairs(trainParts) do
			TweenService:Create(p, TweenInfo.new(dur,
				Enum.EasingStyle.Linear),
				{ CFrame = p.CFrame + delta }):Play()
		end
		task.delay(dur + 0.1, function()
			moving = false
			metroInfo.at = idx
			metroInfo.phase = "dwell"
			metroInfo.eta = DWELL
			metroInfo.etaAt = os.clock() + DWELL
			-- arrival chime at the station
			local chime = Instance.new("Sound")
			chime.SoundId = "rbxasset://sounds/electronicpingshort.wav"
			chime.Volume = 1
			chime.Parent = workspace
			chime:Play()
			task.delay(2, function() chime:Destroy() end)
		end)
	end

	-- call buttons on every station platform wall
	for si, stop in ipairs(STOPS) do
		local btn = Instance.new("Part")
		btn.Name = "MetroCall" .. si
		btn.Size = Vector3.new(1.4, 1.4, 0.5)
		btn.Color = Color3.fromRGB(255, 200, 40)
		btn.Material = Enum.Material.Neon
		btn.Anchored = true
		btn.CFrame = CFrame.new(stop[2] - 17.5, 6.5, -8.5)
		btn.Parent = workspace
		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = 30
		click.Parent = btn
		click.MouseClick:Connect(function()
			if metroInfo.at == si and metroInfo.phase == "dwell" then
				return
			end
			-- if moving toward si already, ignore; else queue jump:
			if metroInfo.phase == "dwell" then
				metroInfo.eta = 0.1
				metroInfo.etaAt = os.clock() + 0.1
			else
				metroInfo.target = si
			end
		end)
	end

	-- departure boards (one per station)
	local boards = {}
	for si, stop in ipairs(STOPS) do
		local board = Instance.new("Part")
		board.Name = "MetroBoard" .. si
		board.Size = Vector3.new(10, 4, 0.4)
		board.Color = Color3.fromRGB(20, 24, 30)
		board.Anchored = true
		board.CFrame = CFrame.new(stop[2] - 26, 12, -12.5)
		board.Parent = workspace
		local gui = Instance.new("SurfaceGui")
		gui.Face = Enum.NormalId.Front
		gui.Parent = board
		local l = Instance.new("TextLabel")
		l.Size = UDim2.new(1, 0, 1, 0)
		l.BackgroundColor3 = Color3.fromRGB(8, 10, 14)
		l.TextColor3 = Color3.fromRGB(120, 220, 120)
		l.TextScaled = true
		l.Font = Enum.Font.Code
		l.Text = "..."
		l.Parent = gui
		boards[si] = l
	end

	-- tickets: kiosks sell, departure consumes (ride requires a ticket)
	local function hasTicket(player)
		return player:GetAttribute("MetroTicket") ~= nil
	end

	for si, stop in ipairs(STOPS) do
		local kiosk = workspace:FindFirstChild("MKiosk_" .. STOPS[si][1],
			true)
		if kiosk then
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = "Beli Tiket ($5)"
			prompt.ObjectText = "Kios Tiket"
			prompt.HoldDuration = 0.3
			prompt.Parent = kiosk
			prompt.Triggered:Connect(function(player)
				local ls = player:FindFirstChild("leaderstats")
				local cash = ls and ls:FindFirstChild("Cash")
				if not cash or cash.Value < 5 then return end
				cash.Value -= 5
				player:SetAttribute("MetroTicket", 1)
			end)
		end
	end

	-- shuttle loop with boarding phase + ticket check
	local playerSeatWatch = function()
		-- returns seated riders on the train
		local riders = {}
		for _, p in ipairs(workspace:GetDescendants()) do
			if p:IsA("Seat") and p.Name == "TrainSeat"
				and p.Occupant then
				local pl = Players:GetPlayerFromCharacter(
					p.Occupant.Parent)
				if pl then
					table.insert(riders, { pl, p })
				end
			end
		end
		return riders
	end

	task.spawn(function()
		local i, dir = 1, 1
		while true do
			-- DWELL: boarding
			metroInfo.at = i
			metroInfo.phase = "dwell"
			metroInfo.eta = DWELL
			metroInfo.etaAt = os.clock() + DWELL
			local left = DWELL
			while left > 0 do
				task.wait(0.5)
				left = metroInfo.etaAt - os.clock()
			end
			-- ticket check at departure
			for _, rider in ipairs(playerSeatWatch()) do
				local pl, seat = rider[1], rider[2]
				if not hasTicket(pl) then
					local hum = pl.Character
						and pl.Character:FindFirstChildOfClass(
							"Humanoid")
					if hum then
						hum.Jump = true
					end
					local gui = Instance.new("BillboardGui")
					gui.Size = UDim2.new(0, 240, 0, 50)
					gui.StudsOffset = Vector3.new(0, 3, 0)
					gui.AlwaysOnTop = true
					gui.Parent = seat
					local l = Instance.new("TextLabel")
					l.Size = UDim2.new(1, 0, 1, 0)
					l.BackgroundColor3 = Color3.fromRGB(120, 20, 20)
					l.TextColor3 = Color3.new(1, 1, 1)
					l.TextScaled = true
					l.Font = Enum.Font.GothamBold
					l.Text = "Tidak punya tiket!"
					l.Parent = gui
					task.delay(3, function() gui:Destroy() end)
				else
					pl:SetAttribute("MetroTicket", nil)
				end
			end
			-- MOVE
			local nxt = i + dir
			if nxt < 1 or nxt > #STOPS then
				dir = -dir
				nxt = i + dir
			end
			metroInfo.phase = "moving"
			metroInfo.target = nxt
			local delta = Vector3.new(STOPS[nxt][2] - STOPS[i][2], 0, 0)
			local dur = math.abs(delta.X) / SPEED
			metroInfo.eta = dur
			metroInfo.etaAt = os.clock() + dur
			for _, p in ipairs(trainParts) do
				TweenService:Create(p, TweenInfo.new(dur,
					Enum.EasingStyle.Linear),
					{ CFrame = p.CFrame + delta }):Play()
			end
			task.wait(dur + 0.1)
			i = nxt
		end
	end)

	-- boards + call buttons update every 0.5s
	task.spawn(function()
		while true do
			for si, stop in ipairs(STOPS) do
				local l = boards[si]
				if l then
					local txt
					if metroInfo.phase == "dwell"
						and metroInfo.at == si then
						txt = string.format(
							"STASIUN %s
KERETA DI PERON — berangkat %ds",
							stop[1],
							math.max(0, math.ceil(
								metroInfo.etaAt - os.clock())))
					elseif metroInfo.phase == "moving"
						and metroInfo.target == si then
						txt = string.format(
							"STASIUN %s
KERETA MENDEKAT — tiba %ds",
							stop[1],
							math.max(0, math.ceil(
								metroInfo.etaAt - os.clock())))
					else
						txt = string.format(
							"STASIUN %s
Kereta sedang di: %s",
							stop[1], STOPS[metroInfo.at][1])
					end
					if l.Text ~= txt then
						l.Text = txt
					end
				end
			end
			-- live eta countdown while dwelling
			if metroInfo.phase == "dwell" then
				metroInfo.eta = math.max(0,
					metroInfo.etaAt - os.clock())
			end
			task.wait(0.5)
		end
	end)
end)

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
