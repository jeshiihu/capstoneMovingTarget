/*
 * motorConstants.h
 *
 *  Created on: Mar 10, 2018
 *      Author: jhuynh
 */

#ifndef HWLIBS_MOTORCONSTANTS_H_
#define HWLIBS_MOTORCONSTANTS_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

/*-----------Y Addresses-----------*/

#define STEP_ADDR_Y 0x00000700
#define STEP_BASE_Y FPGA_TO_HPS_LW_ADDR(STEP_ADDR_Y)

#define CYCLE_ADDR_Y 0x00000800
#define CYCLE_BASE_Y FPGA_TO_HPS_LW_ADDR(CYCLE_ADDR_Y)

#define DUTY_ADDR_Y 0x00000900
#define DUTY_BASE_Y FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_Y)

#define DIR_ADDR_Y 0x00001000
#define DIR_BASE_Y FPGA_TO_HPS_LW_ADDR(DIR_ADDR_Y)

#define STEPMODE_ADDR_Y 0x00001100
#define STEPMODE_BASE_Y FPGA_TO_HPS_LW_ADDR(STEPMODE_ADDR_Y)

/*-----------X Addresses-----------*/

#define STEP_ADDR_X 0x00000200
#define STEP_BASE_X FPGA_TO_HPS_LW_ADDR(STEP_ADDR_X)

#define CYCLE_ADDR_X 0x00000300
#define CYCLE_BASE_X FPGA_TO_HPS_LW_ADDR(CYCLE_ADDR_X)

#define DUTY_ADDR_X 0x00000400
#define DUTY_BASE_X FPGA_TO_HPS_LW_ADDR(DUTY_ADDR_X)

#define DIR_ADDR_X 0x00000500
#define DIR_BASE_X FPGA_TO_HPS_LW_ADDR(DIR_ADDR_X)

#define STEPMODE_ADDR_X 0x00000600
#define STEPMODE_BASE_X FPGA_TO_HPS_LW_ADDR(STEPMODE_ADDR_X)


/*-----------------------------------------------------*/

// Specifies CW (clockwise) and CCW counter clockwise direction
enum Motor { motorX = 0, motorY = 1 };

void* GetMotorStepBaseAddr   (enum Motor motor);
void* GetMotorDirBaseAddr    (enum Motor motor);
void* GetMotorCycleBaseAddr (enum Motor motor);
void* GetMotorDutyBaseAddr   (enum Motor motor);
void* GetMotorStepModeBaseAddr   (enum Motor motor);

#endif /* HWLIBS_MOTORCONSTANTS_H_ */