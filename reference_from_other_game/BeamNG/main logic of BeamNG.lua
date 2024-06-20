local sharedFunctions = {}

sharedFunctions.selectShiftPoints = function(gearIndex)
    -- 根据侵略性在高/低范围之间进行插值
    local aggression = min(max((smoothedValues.drivingAggression - 0.2) / 0.8, 0), 1)
    local aggressionCoef = min(max(aggression * aggression, 0), 1) -- 侵略性成为换挡 AV 的偏置
    local shiftPoint = shiftPoints[gearIndex]
    shiftBehavior.shiftDownAV = shiftPoint.lowShiftDownAV + (shiftPoint.highShiftDownAV - shiftPoint.lowShiftDownAV) * aggressionCoef
    shiftBehavior.shiftUpAV = shiftPoint.lowShiftUpAV + (shiftPoint.highShiftUpAV - shiftPoint.lowShiftUpAV) * aggressionCoef
    controlLogicModule.shiftBehavior = shiftBehavior
end

local function updateWheelSlip(dt)
    local overallWheelSlip = 0
    local wheelSlipCount = 0
    local hasGroundContact = false
    local hasPressureWheels = false

    for _, wi in pairs(wheels.wheels) do
        if wi.isPropulsed and not wi.isBroken then
            hasPressureWheels = hasPressureWheels or wi.wheelSection == "pressureWheels"
            if wi.contactMaterialID1 >= 0 and wi.contactDepth == 0 then
                overallWheelSlip = overallWheelSlip + wi.slipEnergy
                wheelSlipCount = wheelSlipCount + 1
            end
            hasGroundContact = wi.contactMaterialID1 >= 0 or hasGroundContact
        end
        handBrakeHandling.smartParkingBrakeSlip = handBrakeHandling.smartParkingBrakeSlip + wi.slipEnergy
    end

    local groundContactCoef = smoother.groundContactSmoother:getUncapped(hasGroundContact and 1 or 0, dt)
    overallWheelSlip = smoother.wheelSlipShiftUp:get(overallWheelSlip, dt)
    local averagePropulsedWheelSlip = wheelSlipCount > 0 and overallWheelSlip / wheelSlipCount or 0
    handBrakeHandling.smartParkingBrakeSlip = handBrakeHandling.smartParkingBrakeSlip / wheels.wheelCount

    shiftPreventionData.wheelSlipShiftDown = true

    if (averagePropulsedWheelSlip > shiftPreventionData.wheelSlipDownThreshold or groundContactCoef < 1) then
        shiftPreventionData.wheelSlipShiftDown = false
    end

    shiftPreventionData.wheelSlipShiftUp = groundContactCoef >= 1 and averagePropulsedWheelSlip < shiftPreventionData.wheelSlipUpThreshold

    if not hasPressureWheels then
        shiftPreventionData.wheelSlipShiftDown = true
        shiftPreventionData.wheelSlipShiftUp = true
    end

    controlLogicModule.shiftPreventionData = shiftPreventionData

    --print(string.format("%d / %d slip, groundcontact: %s -> canShiftDown: %s", averagePropulsedWheelSlip, shiftPreventionData.wheelSlipDownThreshold, groundContactCoef, shiftPreventionData.wheelSlipShiftDown))
end


local function updateAggression(dt)
    local throttle = (gearboxHandling.isArcadeSwitched and inputValues.brake or inputValues.throttle) or 0 --read our actual throttle input value, depending on which input is currently used for throttle
  
    if gearboxHandling.useSmartAggressionCalculation then --use the new smart aggression logic for newer cars and all manuals
      if throttle <= 0 then
        timer.aggressionHoldOffThrottleTimer = max(timer.aggressionHoldOffThrottleTimer - dt, 0)
      else
        timer.aggressionHoldOffThrottleTimer = timerConstants.aggressionHoldOffThrottleDelay
      end
  
      local usesKeyboard = input.state.throttle.filter == FILTER_KBD or input.state.throttle.filter == FILTER_KBD2
      local brakeUse = M.brake > 0.25
      local aggression
      local sportModeAdjust = (controlLogicModule.isSportModeActive and 0.5 or 0)
  
      if usesKeyboard then
        aggression = brakeUse and smoothedValues.drivingAggression or throttle * 1.333
        aggression = electrics.values.wheelspeed < 1 and 0.75 or aggression
        aggression = smoother.aggressionKey:get(max(aggression, sportModeAdjust), dt)
        smoother.aggressionAxis:set(aggression) --keep the other smoother in sync
      else
        local throttleHold = throttle <= 0 and electrics.values.wheelspeed > 2 and (timer.aggressionHoldOffThrottleTimer > 0 or controlLogicModule.isSportModeActive)
        local holdAggression = brakeUse or throttleHold
        local dThrottle = min(max((throttle - lastAggressionThrottle) / dt, 1), 20)
        aggression = holdAggression and smoothedValues.drivingAggression or throttle * 1.333 * dThrottle
        aggression = electrics.values.wheelspeed < 1 and 0.0 or aggression
        aggression = smoother.aggressionAxis:get(max(aggression, sportModeAdjust), dt)
        smoother.aggressionKey:set(aggression) --keep the other smoother in sync
      end
      smoothedValues.drivingAggression = min(aggression, 1) --previous smoother outputs max out at 1.333 to give some headroom, but now we cap them to 1 for the rest of the code
    else --use old logic for old manuals
      smoothedValues.drivingAggression = smoothedValues.throttle
    end
  
    smoothedValues.drivingAggression = aggressionOverride or smoothedValues.drivingAggression
    M.drivingAggression = smoothedValues.drivingAggression
  
    lastAggressionThrottle = throttle
  end


local function calculateOptimalLoadShiftPoints(shiftDownRPMOffsetCoef)
    local torqueCurve = engine.torqueData.curves[engine.torqueData.finalCurveName].torque
    for k, v in pairs(gearbox.gearRatios) do
      local shiftUpRPM = nil
      local shiftDownRPM = nil
      if v ~= 0 then
        local currentGearRatio = v
        local nextGearRatio = gearbox.gearRatios[k + sign(k)] or 0
        local previousGearRatio = gearbox.gearRatios[k - sign(k)] or 0
  
        for i = 100, engine.maxRPM - 100, 50 do
          local currentWheelTorque = torqueCurve[i] * currentGearRatio
          local nextGearRPM = min(max(floor(i * (nextGearRatio / currentGearRatio)), 1), engine.maxRPM)
          local previousGearRPM = min(max(floor(i * (previousGearRatio / currentGearRatio)), 1), engine.maxRPM)
          local nextWheelTorque = torqueCurve[nextGearRPM] * nextGearRatio
          local previousWheelTorque = torqueCurve[previousGearRPM] * previousGearRatio
  
          if currentWheelTorque * sign(currentGearRatio) < nextWheelTorque * sign(currentGearRatio) and not shiftUpRPM and currentWheelTorque * currentGearRatio > 0 and currentGearRatio * nextGearRatio > 0 then
            shiftUpRPM = i
          end
  
          if previousWheelTorque * sign(currentGearRatio) > currentWheelTorque * 1.05 * sign(currentGearRatio) and previousGearRPM < engine.maxRPM * 0.9 and currentWheelTorque * currentGearRatio > 0 and currentGearRatio * previousGearRatio > 0 then
            shiftDownRPM = i
          end
        end
  
        if shiftDownRPM and shiftPoints[k - sign(k)] and shiftPoints[k - sign(k)].highShiftUpAV > 0 then
          local offsetCoef = shiftDownRPMOffsetCoef * (currentGearRatio / previousGearRatio)
          shiftDownRPM = min(shiftDownRPM, max(floor(shiftPoints[k - sign(k)].highShiftUpAV / previousGearRatio * currentGearRatio * offsetCoef * constants.avToRPM), (engine.idleRPM or 0) * 1.05))
        end
      end
  
      --limit upshift RPM to something slightly below the max rpm to avoid interference with the rev limiter
      local maxShiftUpRPM = min(engine.maxRPM * 0.98, engine.maxRPM - 100)
      shiftPoints[k].highShiftUpAV = min((shiftUpRPM or maxShiftUpRPM), maxShiftUpRPM) * constants.rpmToAV
      shiftPoints[k].highShiftDownAV = (shiftDownRPM or 0) * constants.rpmToAV
  
      --print(string.format("Gear %d: Up: %d, Down: %d", k, shiftPoints[k].highShiftUpAV * constants.avToRPM, shiftPoints[k].highShiftDownAV * constants.avToRPM))
    end
  end