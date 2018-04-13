/*
 * motorConstants.c
 *
 *  Created on: Mar 10, 2018
 *      Author: jhuynh
 */
#include <hps.h>

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))
#include "motorConstants.h"

/*********************************************************************************************************
 *                                           GetMotor___BaseAddr() Functions
 * Description : Returns the appropriate address for the specified motor
 * Arguments   : enum Motor
 * Returns     : void* address
 * Notes       : Adding more motor types should add logic to all functions
 *********************************************************************************************************
 */
void* GetMotorStepBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)STEP_BASE_X;

	return (void*)STEP_BASE_Y;
}

void* GetMotorDirBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)DIR_BASE_X;

	return (void*)DIR_BASE_Y;
}

void* GetMotorPeriodBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)PERIOD_BASE_X;

	return (void*)PERIOD_BASE_Y;
}

void* GetMotorDutyBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)DUTY_BASE_X;

	return (void*)DUTY_BASE_Y;
}

