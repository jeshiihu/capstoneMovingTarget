/*
 * motorConstants.c
 *
 *  Created on: Mar 10, 2018
 *      Author: jhuynh
 *      Contains the motor constants and addresses assigned for our components
 *      Functions: Gets the appropriate
 */
#include <hps.h>

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))
#include "motorConstants.h"

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

