/*
 * stepper.h
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#ifndef HWLIBS_STEPPER_H_
#define HWLIBS_STEPPER_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define STEP_ADDR 0x00000200 // number of steps
#define STEP_BASE FPGA_TO_HPS_LW_ADDR(STEP_ADDR)

#define CYCLE_ADDR 0x00000300 // number of periods
#define CYCLE_BASE FPGA_TO_HPS_LW_ADDR(CYCLE_ADDR)

#define DUTY_ADDR 0x00000400 // number of pulses
#define DUTY_BASE FPGA_TO_HPS_LW_ADDR(DUTY_ADDR)

#define DIR_ADDR 0x00000500 // direction
#define DIR_BASE FPGA_TO_HPS_LW_ADDR(DIR_ADDR)

#define STEPMODE_ADDR 0x00000600 // direction
#define STEPMODE_BASE FPGA_TO_HPS_LW_ADDR(STEPMODE_ADDR)

#define FPGA_CLK_FREQ_HZ 50000000
#define FULL_STEP 200
#define HALF_STEP 400

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Direction { cw = 0, ccw = 1 };
enum StepMode { full = 0, half = 1 };

//////////////////////////////////////////////////////////////////
//Control the motor and helpers
void InitMotor(INT32U freq);
INT32U Freq2NumCycle(INT32U freq);

void StepMotor(INT16U step);

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Direction dir);
enum Direction GetDirection(void);

void SetStepMode(enum StepMode mode);
enum StepMode GetStepMode(void);

void SetFrequency(INT32U freq);
INT32U GetFrequency(void);

INT32U GetDutyCycle(void);
INT16U GetReqSteps(void);

INT16U YCoord2Steps(int y);
enum Direction YCoord2Dir(int y);

#endif /* HWLIBS_STEPPER_H_ */
