//
//  stepper.c
//  StepperMotorDriver
//
//  Created by Jessica Huynh on 2018-02-20.
//  Copyright © 2018 Jessica Huynh. All rights reserved.
//

#include "stepper.h"

//////////////////////////////////////////////////////////////////
//Initialize & control the motor
void InitMotor(uint32_t freq)
{
    // convert freq (pps) to n, n = fin/fout, and set
    uint16_t numCycles = Freq2NumCycle(freq);
    alt_write_hword(CYCLE_BASE, numCycles);
    
    // calculate the duty cycle, and set
    uint16_t duty = numCycles*0.5;
    alt_write_hword(DUTY_BASE, duty);
}

uint16_t Freq2NumCycle(uint32_t freq)
{
    return FPGA_CLK_FREQ_HZ/freq;
}

void StepMotor(uint16_t steps)
{
    alt_write_hword(STEP_BASE, steps);
}

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Direction dir)
{
    alt_write_byte(DIR_BASE, (uint8_t)dir);
}

enum Direction GetDirection(void)
{
    return (enum Direction)alt_read_byte(DIR_BASE);
}

void SetFrequency(uint32_t freq)
{
    uint16_t numCycles = Freq2NumCycle(freq);
    alt_write_hword(CYCLE_BASE, numCycles);
}

uint16_t GetFrequency(void)
{
    uint16_t cycle = alt_read_hword(CYCLE_BASE);
    return FPGA_CLK_FREQ_HZ/cycle;
}

uint16_t GetDutyCycle(void)
{
    return alt_read_hword(DUTY_BASE);
}

uint16_t GetReqSteps(void)
{
    return alt_read_hword(STEP_BASE)
}
