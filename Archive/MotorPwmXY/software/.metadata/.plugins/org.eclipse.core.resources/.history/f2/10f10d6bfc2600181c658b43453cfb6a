/*
 * motorConstants.h
 *
 *  Created on: Mar 10, 2018
 *      Author: jhuynh
 */

#ifndef HWLIBS_MOTORCONSTANTS_H_
#define HWLIBS_MOTORCONSTANTS_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

////////////////////////////////////////////////////////
/*
 * Y Stepper Motor Addresses
 */
#define STEP_ADDR_Y 0x00000200 // number of steps
#define STEP_BASE_Y FPGA_TO_HPS_LW_ADDR(STEP_ADDR_Y)

#define DIR_ADDR_Y 0x00000300 // number of periods
#define DIR_BASE_Y FPGA_TO_HPS_LW_ADDR(DIR_ADDR_Y)

#define PERIOD_ADDR_Y 0x00000400 // number of pulses
#define PERIOD_BASE_Y FPGA_TO_HPS_LW_ADDR(PERIOD_ADDR_Y)

#define DUTY_ADDR_Y 0x00000500 // direction
#define DUTY_BASE_Y FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_Y)

////////////////////////////////////////////////////////
/*
 * X Stepper Motor Addresses
 */
#define STEP_ADDR_X 0x00000700 // number of steps
#define STEP_BASE_X FPGA_TO_HPS_LW_ADDR(STEP_ADDR_X)

#define DIR_ADDR_X 0x00000800 // number of periods
#define DIR_BASE_X FPGA_TO_HPS_LW_ADDR(DIR_ADDR_X)

#define PERIOD_ADDR_X 0x00001000 // number of pulses
#define PERIOD_BASE_X FPGA_TO_HPS_LW_ADDR(PERIOD_ADDR_X)

#define DUTY_ADDR_X 0x00001100 // direction
#define DUTY_BASE_X FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_X)

////////////////////////////////////////////////////////
////////////////////////////////////////////////////////
#define FPGA_CLK_FREQ_HZ 50000000
#define DUTY_CYCLE 0.9;

#define FULL_STEP 200

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Motor { motorX = 0, motorY = 1 };
enum Direction { cw = 0, ccw = 1 };

void* GetMotorStepBaseAddr   (enum Motor motor);
void* GetMotorDirBaseAddr    (enum Motor motor);
void* GetMotorPeriodBaseAddr (enum Motor motor);
void* GetMotorDutyBaseAddr   (enum Motor motor);

#endif /* HWLIBS_MOTORCONSTANTS_H_ */
