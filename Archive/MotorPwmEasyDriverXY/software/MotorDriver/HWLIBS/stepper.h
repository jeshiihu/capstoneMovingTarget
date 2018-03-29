/*
 * stepper.h
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#ifndef HWLIBS_STEPPER_H_
#define HWLIBS_STEPPER_H_

//////////////////////////////////////////////////////////////////
//Control the motor and helpers
void InitMotor(enum Motor motor, INT32U freq);
void SetPeriodDuty(enum Motor motor, INT32U freq);
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
