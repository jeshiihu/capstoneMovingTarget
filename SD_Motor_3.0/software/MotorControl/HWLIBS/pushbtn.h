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

#define KEY2_BASE 0x00001200
#define KEY2_ADDR FPGA_TO_HPS_LW_ADDR(KEY2_BASE)
#define 	QSYS_KEY2_BASE 				( ALT_LWFPGASLVS_ADDR  + KEY2_BASE)
#define 	QSYS_KEY2_REG_DIR			(*(( CPU_REG32 *) (QSYS_KEY2_BASE + 0x4)))
#define		QSYS_KEY2_REG_INT_MASK		(*(( CPU_REG32 *) (QSYS_KEY2_BASE + 0x8)))
#define		QSYS_KEY2_REG_EDGE_CAP		(*(( CPU_REG32 *) (QSYS_KEY2_BASE + 0xC)))

#define KEY1_BASE 0x00001300
#define KEY1_ADDR FPGA_TO_HPS_LW_ADDR(KEY1_BASE)
#define 	QSYS_KEY1_BASE 				( ALT_LWFPGASLVS_ADDR  + KEY1_BASE)
#define 	QSYS_KEY1_REG_DIR			(*(( CPU_REG32 *) (QSYS_KEY1_BASE + 0x4)))
#define		QSYS_KEY1_REG_INT_MASK		(*(( CPU_REG32 *) (QSYS_KEY1_BASE + 0x8)))
#define		QSYS_KEY1_REG_EDGE_CAP		(*(( CPU_REG32 *) (QSYS_KEY1_BASE + 0xC)))

#define		QSYS_KEY_DIR_INPUT			0
#define		QSYS_KEY_DIR_OUTPUT			1

#define		QSYS_KEY_IRQ_ENABLE			1
#define		QSYS_KEY_IRQ_DISABLE		0

void InitFPGAPushBtnsInterrupt(void);
void InitKey3(void);
void InitKey2(void);
void InitKey1(void);

void ResetBtn_Handler(CPU_INT32U cpu_id);
void XBtn_Handler(CPU_INT32U cpu_id);
void YBtn_Handler(CPU_INT32U cpu_id);

extern void FPGA_LEDS_Off(void);
extern void FPGA_LEDS_On(void);

#endif /* HWLIBS_PUSHBTN_H_ */
