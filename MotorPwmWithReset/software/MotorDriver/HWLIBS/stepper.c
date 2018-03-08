/*
 * stepper.c
 *
 *  Created on: Feb 22, 2018
 *      Author: kgchin
 */

#include <os.h>
#include <hps.h>
#include <socal.h>

#include "stepper.h"

//////////////////////////////////////////////////////////////////
//Initialize & control the motor
void InitMotor(INT32U freq)
{
    // convert freq (pps) to n, n = fin/fout, and set
	INT32U numCycles = Freq2NumCycle(freq);
    alt_write_word(CYCLE_BASE, numCycles);

    // calculate the duty cycle, and set
    INT32U duty = numCycles*0.99;
    alt_write_word(DUTY_BASE, duty);
}

INT32U Freq2NumCycle(INT32U freq)
{
    return FPGA_CLK_FREQ_HZ/freq;
}

void StepMotor(INT16U steps)
{
    alt_write_hword(STEP_BASE, steps);
}

//////////////////////////////////////////////////////////////////
// Getters and Setters
void SetDirection(enum Direction dir)
{
    alt_write_byte(DIR_BASE, (INT8U)dir);
}

enum Direction GetDirection(void)
{
    return (enum Direction)alt_read_byte(DIR_BASE);
}

void SetStepMode(enum StepMode mode)
{
	alt_write_byte(STEPMODE_BASE, (INT8U)mode);
}

enum StepMode GetStepMode(void)
{
    return (enum StepMode)alt_read_byte(STEPMODE_BASE);
}

void SetFrequency(INT32U freq)
{
	INT32U numCycles = Freq2NumCycle(freq);
    alt_write_word(CYCLE_BASE, numCycles);

    // calculate the duty cycle, and set
    INT32U duty = numCycles*0.9;
    alt_write_word(DUTY_BASE, duty);
}

INT32U GetFrequency(void)
{
	INT32U cycle = alt_read_word(CYCLE_BASE);
    return FPGA_CLK_FREQ_HZ/cycle;
}

INT32U GetDutyCycle(void)
{
    return alt_read_word(DUTY_BASE);
}

INT16U GetReqSteps(void)
{
    return alt_read_hword(STEP_BASE);
}

/*---positioning functions with no acceleration----*/

void BottomToCenter(){
	/* 856 steps are needed to move  16.51 cm.
	*  16.51cm/4cm per rev = 4.1275 revolutions.
	*  4.1275 revs * 200 steps (full step) = 856 steps
	*/

}

/* 50 steps are required to move 1cm. This is calculated from the following:
* 1 Pulley has 20 teeth; Each tooth is separated by 2mm.
* Assuming 50% contact (timing belt to pulley) that is 10 teeth.
* 10 teeth * 2mm = 2cm in half a revolution.
* 1 revolution is therefore 4cm.
* 1 Revolution has 200 steps (full step) so 1cm is 1/4 of a revolution (50 steps)
*/
INT16U YCoord2Steps(int y)
{
    if (y == 0)
    	return 0;

    if(y < 0) y = y*-1;
    if(GetStepMode() == full)
    	return y/0.02;
    else
    	return y/0.01;
}

/* This function determines the correct direction given a y.
* If y is negative, the board should be moving downwards; done
* by rotating the motor clockwise. If y is positive, board
* should move upwards and thus counterclockwise.
*/
enum Direction YCoord2Dir(int y)
{
    if (y<0) return cw;
    return ccw;
}