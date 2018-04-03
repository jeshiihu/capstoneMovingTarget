/*
 * motorConstants.c
 *
 *  Created on: Mar 10, 2018
 *      Author: jhuynh
 */
#include <hps.h>
#include "motorConstants.h"

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))


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

void* GetMotorCycleBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)CYCLE_BASE_X;

	return (void*)CYCLE_BASE_Y;
}

void* GetMotorDutyBaseAddr(enum Motor motor)
{
	if(motor == motorX)
		return (void*)DUTY_BASE_X;

	return (void*)DUTY_BASE_Y;
}

void* GetMotorStepModeBaseAddr(enum Motor motor){
	if (motor == motorX)
		return (void*)STEPMODE_BASE_X;

	return (void*)STEPMODE_BASE_Y;
}