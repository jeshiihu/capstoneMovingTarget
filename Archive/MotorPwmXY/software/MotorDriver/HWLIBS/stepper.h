/*
 * stepper.h
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#ifndef HWLIBS_STEPPER_H_
#define HWLIBS_STEPPER_H_


#define FPGA_CLK_FREQ_HZ 50000000
#define DUTY_CYCLE 0.9;

#define FULL_STEP 200
#define HALF_STEP 400

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Direction { cw = 0, ccw = 1 };
enum StepMode { full = 0, half = 1 };

/*--------motor functions---------*/

void InitMotor(enum Motor m, INT32U freq);
INT32U Freq2NumCycle(INT32U freq);

void StepMotor(enum Motor m, INT16U step);

void SetDirection(enum Motor m, enum Direction dir);
enum Direction GetDirection(enum Motor m);

void SetStepMode(enum Motor m, enum StepMode mode);
enum StepMode GetStepMode(enum Motor m);

void SetFrequency(enum Motor m, INT32U freq);
INT32U GetFrequency(enum Motor m);

INT32U GetDutyCycle(enum Motor m);
INT16U GetReqSteps(enum Motor m);

INT16U Coord2Steps(enum Motor m, int a);
enum Direction YCoord2Dir(int y);
enum Direction XCoord2Dir(int x);

#endif /* HWLIBS_STEPPER_H_ */