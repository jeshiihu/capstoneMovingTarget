/*
 * pushbtn.c
 *
 *  Created on: Mar 13, 2018
 *      Author: jhuynh
 */
#include "socal/hps.h"
#include "socal/socal.h"
#include "lib_def.h"
#include "os_cpu.h"
#include  <os.h>

#include "pushbtn.h"

extern OS_EVENT *SemaphoreReset;

void InitFPGAPushBtnInterrupt(void)
{
	// This version will use the PIO component implemented on the Qsys Design
	// Turn Timer off & Turn on CONT mode
	QSYS_KEY3_REG_DIR &= QSYS_KEY3_DIR_INPUT;
	QSYS_KEY3_REG_INT_MASK &= QSYS_KEY3_IRQ_DISABLE;

	//Install handler and set prio
	// 72 is source for irq 0 via lwhpsfpga bus, PRIO, cpu target list, ISR
	CPU_BOOLEAN err = BSP_IntVectSet(72u, 1, DEF_BIT_00, FPGA_PushBtnISR_Handler);

	// Turn on Timer IRQs at component level,
	// Start Timer, Enable INT at GIC level
	QSYS_KEY3_REG_INT_MASK |= QSYS_KEY3_IRQ_ENABLE;
	BSP_IntSrcEn(72u);
}

void FPGA_PushBtnISR_Handler(CPU_INT32U cpu_id)
{
	OSSemPost(SemaphoreReset);

	FPGA_LEDS_On();
	OSTimeDlyHMSM(0, 0, 0, 500);
	FPGA_LEDS_Off();

	// Clear interrupt
	QSYS_KEY3_REG_EDGE_CAP = 1;
}



