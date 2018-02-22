//
//  stepper.c
//  StepperMotorDriver
//
//  Created by Jessica Huynh on 2018-02-20.
//  Copyright © 2018 Jessica Huynh. All rights reserved.
//

#include "stepper.h"

void InitMotor(void)
{
    _motorState = on;
    _direction = cw;
    _pulses = 0;
}

void SetDirection(enum Direction dir)
{
    _direction = dir;
}

enum Direction GetDirection()
{
    return _direction;
}

void SetPulses(int32_t pulses)
{   // ensure that rpm is always between 0 and MAX
    if(pulses < 0) pulses = 0;
    _pulses = pulses;
}

int32_t GetPulses(void)
{
    return _pulses;
}

void SetStepType(enum StepType type)
{
    _step = type;
}

enum StepType GetStepType(void)
{
    return _step;
}

void DriveMotor()
{
    _motorState = rotating;
    // step motors
}

