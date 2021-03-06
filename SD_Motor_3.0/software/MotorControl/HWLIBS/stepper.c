/*
 * stepper.c
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#include <os.h>
#include <hps.h>
#include <socal.h>

#include "motorConstants.h"
#include "stepper.h"

//////////////////////////////////////////////////////////////////
/*
 *********************************************************************************************************
 *                                           InitMotor(INT32U freq)
 * Description : Initialize the motor with a set frequency (pps)
 * Arguments   : frequency of the motor in pps
 * Returns     : none.
 * Notes       :
 *********************************************************************************************************
 */
void InitMotor(enum Motor motor, INT32U freq)
{
	SetPeriodDuty(motor, freq);
}

void SetPeriodDuty(enum Motor motor, INT32U freq)
{
//     convert freq (pps) to n, n = fin/fout, and set
	INT32U numCycles = Freq2NumCycle(freq);
	alt_write_word(GetMotorPeriodBaseAddr(motor), numCycles);

    // calculate the duty cycle, and set
    INT32U duty = numCycles*DUTY_CYCLE;
	alt_write_word(GetMotorDutyBaseAddr(motor), duty);
}

//////////////////////////////////////////////////////////////////
/*
 *********************************************************************************************************
 *                                           Freq2NumCycle(INT32U freq)
 * Description : Frequency divider calculation for the board (FPGA is 50MHz)
 * Arguments   : PPS frequency
 * Returns     : none.
 * Notes       :
 *********************************************************************************************************
 */
INT32U Freq2NumCycle(INT32U freq)
{
    return FPGA_CLK_FREQ_HZ/freq;
}

//////////////////////////////////////////////////////////////////
/*
 *********************************************************************************************************
 *                                           StepMotor(INT16U steps)
 * Description : Send steps to the motor
 * Arguments   : number of steps
 * Returns     : none.
 * Notes       :
 *********************************************************************************************************
 */
void StepMotor(enum Motor motor, INT16U steps)
{
	alt_write_hword(GetMotorStepBaseAddr(motor), steps);
}

//////////////////////////////////////////////////////////////////
// Sets the direction (0 or 1)
void SetDirection(enum Motor motor, enum Direction dir)
{
	alt_write_byte(GetMotorDirBaseAddr(motor), (INT8U)dir);
}

// Gets the direction (0 cw or 1 ccw) to enum direction
enum Direction GetDirection(enum Motor motor)
{
	return (enum Direction)alt_read_byte(GetMotorDirBaseAddr(motor));
}

// Set Frequency. This will also set the duty (0.9)
void SetFrequency(enum Motor motor, INT32U freq)
{
	SetPeriodDuty(motor, freq);
}

// Get the cycle from the addr and then convert to freq (pps)
INT32U GetFrequency(enum Motor motor)
{
	INT32U cycle = alt_read_word(GetMotorPeriodBaseAddr(motor));
    return FPGA_CLK_FREQ_HZ/cycle;
}

// Get the duty cycle
INT32U GetDutyCycle(enum Motor motor)
{
	return alt_read_word(GetMotorDutyBaseAddr(motor));
}

// Get the steps that were set to the motor
INT16U GetCurrSteps(enum Motor motor)
{
	return alt_read_hword(GetMotorStepBaseAddr(motor));
}

/* 50 steps are required to move 1cm. This is calculated from the following:
* 1 Pulley has 20 teeth; Each tooth is separated by 2mm.
* Assuming 50% contact (timing belt to pulley) that is 10 teeth.
* 10 teeth * 2mm = 2cm in half a revolution.
* 1 revolution is therefore 4cm.
* 1 Revolution has 200 steps (full step) so 1cm is 1/4 of a revolution (50 steps)
*/
INT16U XYCoord2Steps(int y)
{
    if (y == 0) return 0;

    if(y < 0) y = y*-1;
    return y/0.02;
}

int Steps2Distance(INT16U steps, enum Direction dir)
{
    if(dir == ccw)
    	return steps*0.02;

    return steps*(-0.02);
}


/* This function determines the correct direction given a y.
* If y is negative, the board should be moving downwards; done
* by rotating the motor clockwise. If y is positive, board
* should move upwards and thus counterclockwise.
*/
enum Direction YCoord2Dir(int y)
{
    if (y>0) return ccw;
    return cw;
}

enum Direction XCoord2Dir(int x)
{
    if (x>0) return ccw;
    return cw;
}

void MoveDistCm(enum Motor m, int dist)
{	/* Ensures that the motors are not driven at a distance
	 * that is greater what is possible */
	if(dist > 16) dist = 16;
	if(dist < -16) dist = -16;

	enum Direction dir = cw;
	if(m == motorY)
	{ dir = YCoord2Dir(dist);}
	else
	{ dir = XCoord2Dir(dist);}

	SetDirection(m, dir);
	INT16U steps = XYCoord2Steps(dist);
    StepMotor(m, steps);
}
