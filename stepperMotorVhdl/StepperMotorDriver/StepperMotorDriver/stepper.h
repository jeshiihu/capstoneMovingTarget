//
//  stepper.h
//  StepperMotorDriver
//
//  Created by Jessica Huynh on 2018-02-20.
//  Copyright © 2018 Jessica Huynh. All rights reserved.
//

#ifndef stepper_h
#define stepper_h

#include <stdio.h>
#include "common.h"

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Direction
{
    cw = 0,
    ccw = 1
};

enum State
{
    off, on, rotating
};

//////////////////////////////////////////////////////////////////
//Initialize the motor
static enum Direction _direction;
static enum State _motorState;
static int32_t _rpm;

void InitMotor(void);

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Direction dir);
enum Direction GetDirection(void);

void SetRPM(int32_t rpm);
int32_t GetRPM(void);

//////////////////////////////////////////////////////////////////
// Motor Control
enum boolean StartMotor(void);
void StopMotor(void);

#endif /* stepper_h */
