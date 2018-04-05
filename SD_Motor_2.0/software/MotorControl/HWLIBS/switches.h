/*
 * switches.h
 *
 *  Created on: Mar 29, 2018
 *      Author: jhuynh
 */

#ifndef HWLIBS_SWITCHES_H_
#define HWLIBS_SWITCHES_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define SW_ADD 	 0x00001400
#define SW_BASE  FPGA_TO_HPS_LW_ADDR(SW_ADD)

int GetPosNegSwitch(void);

#endif /* HWLIBS_SWITCHES_H_ */
