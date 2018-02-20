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
    _direction = cw;
    _rpm = 0;
}

void SetDirection(enum Direction dir)
{
    _direction = dir;
}

enum Direction GetDirection()
{
    return _direction;
}

void SetRPM(int32_t rpm)
{   // ensure that rpm is always 0 or more
    if(rpm < 0) rpm = 0;
    _rpm = rpm;
}

int32_t GetRPM(void)
{
    return _rpm;
}

enum boolean StartMotor()
{
    // convert rpm to freq
    // calc period_count & pulse count
    return false;
}

void StopMotor(void)
{
    _rpm = 0;
    // convert and send;
}


