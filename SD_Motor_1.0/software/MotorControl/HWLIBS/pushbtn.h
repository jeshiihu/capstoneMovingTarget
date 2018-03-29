/*
 * pushbtn.h
 *
 *  Created on: Mar 13, 2018
 *      Author: jhuynh
 */

#ifndef HWLIBS_PUSHBTN_H_
#define HWLIBS_PUSHBTN_H_

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define KEY3_BASE 0x00001000
#define KEY3_ADDR FPGA_TO_HPS_LW_ADDR(KEY3_BASE)

#define 	QSYS_KEY3_BASE 				( ALT_LWFPGASLVS_ADDR  + KEY3_BASE)
#define 	QSYS_KEY3_REG_DIR			(*(( CPU_REG32 *) (QSYS_KEY3_BASE + 0x4)))
#define		QSYS_KEY3_REG_INT_MASK		(*(( CPU_REG32 *) (QSYS_KEY3_BASE + 0x8)))
#define		QSYS_KEY3_REG_EDGE_CAP		(*(( CPU_REG32 *) (QSYS_KEY3_BASE + 0xC)))

#define		QSYS_KEY3_DIR_INPUT			0
#define		QSYS_KEY3_DIR_OUTPUT		1

#define		QSYS_KEY3_IRQ_ENABLE		1
#define		QSYS_KEY3_IRQ_DISABLE		0

void InitFPGAPushBtnInterrupt(void);
void FPGA_PushBtnISR_Handler(CPU_INT32U cpu_id);

extern void FPGA_LEDS_Off(void);
extern void FPGA_LEDS_On(void);

#endif /* HWLIBS_PUSHBTN_H_ */
