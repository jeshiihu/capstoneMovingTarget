/*
 * stepper.h
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#ifndef HWLIBS_STEPPER_H_
#define HWLIBS_STEPPER_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

////////////////////////////////////////////////////////
/*
 * Y Stepper Motor Addresses
 */
#define STEP_ADDR_Y 0x00000200 // number of steps
#define STEP_BASE_Y FPGA_TO_HPS_LW_ADDR(STEP_ADDR_Y)

#define DIR_ADDR_Y 0x00000300 // number of periods
#define DIR_BASE_Y FPGA_TO_HPS_LW_ADDR(DIR_ADDR_Y)

// TODO enable

#define PERIOD_ADDR_Y 0x00000500 // number of pulses
#define PERIOD_BASE_Y FPGA_TO_HPS_LW_ADDR(PERIOD_ADDR_Y)

#define DUTY_ADDR_Y 0x00000600 // direction
#define DUTY_BASE_Y FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_Y)

////////////////////////////////////////////////////////
/*
 * X Stepper Motor Addresses
 */
#define STEP_ADDR_X 0x00000700 // number of steps
#define STEP_BASE_X FPGA_TO_HPS_LW_ADDR(STEP_ADDR_X)

#define DIR_ADDR_X 0x00000800 // number of periods
#define DIR_BASE_X FPGA_TO_HPS_LW_ADDR(DIR_ADDR_X)

// TODO enable

#define PERIOD_ADDR_X 0x00001000 // number of pulses
#define PERIOD_BASE_X FPGA_TO_HPS_LW_ADDR(PERIOD_ADDR_X)

#define DUTY_ADDR_X 0x00001100 // direction
#define DUTY_BASE_X FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_X)

////////////////////////////////////////////////////////
////////////////////////////////////////////////////////
#define FPGA_CLK_FREQ_HZ 50000000
#define DUTY_CYCLE 0.9;

#define FULL_STEP 200
#define HALF_STEP 400

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Motor { motorX = 0, motorY = 1 };
enum Direction { cw = 0, ccw = 1 };
enum StepMode { full = 0, half = 1 };

//////////////////////////////////////////////////////////////////
//Control the motor and helpers
void InitMotor(enum Motor motor, INT32U freq);
INT32U Freq2NumCycle(INT32U freq);

void StepMotor(enum Motor motor, INT16U step);

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Motor motor, enum Direction dir);
enum Direction GetDirection(enum Motor motor);

void SetFrequency(enum Motor motor, INT32U freq);
INT32U GetFrequency(enum Motor motor);

INT32U GetDutyCycle(enum Motor motor);
INT16U GetReqSteps(enum Motor motor);

INT16U XYCoord2Steps(int y);
enum Direction YCoord2Dir(int y);
enum Direction XCoord2Dir(int y);

#endif /* HWLIBS_STEPPER_H_ */
