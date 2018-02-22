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

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define CYCLE_ADDR 0x00000200 // number of periods
#define CYCLE_BASE FPGA_TO_HPS_LW_ADDR(CYCLE_ADDR)
#define DUTY_ADDR 0x00000300 // number of pulses
#define DUTY_BASE FPGA_TO_HPS_LW_ADDR(DUTY_ADDR)
#define DIR_ADDR 0x00000400 // direction
#define DIR_BASE FPGA_TO_HPS_LW_ADDR(DIR_ADDR)
#define STEP_ADDR 0x00000500 // number of steps
#define STEP_BASE FPGA_TO_HPS_LW_ADDR(REQ_ADDR)

#define FPGA_CLK_FREQ_HZ 50000000

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Direction { cw = 0, ccw = 1 };

//////////////////////////////////////////////////////////////////
//Control the motor and helpers
void InitMotor(uint32_t freq);
uint16_t Freq2NumCycle(uint32_t freq);

void StepMotor(uint16_t step);

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Direction dir);
enum Direction GetDirection(void);

void SetFrequency(uint32_t freq);
uint16_t GetFrequency(void);

uint16_t GetDutyCycle(void);
uint16_t GetReqSteps(void);

#endif /* stepper_h */
