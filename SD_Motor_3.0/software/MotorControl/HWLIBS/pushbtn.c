/*
 * pushbtn.c
 *
 *  Created on: Mar 13, 2018
 *  Author: Jessica Huynh, jhuynh@ualberta.ca
 */
#include  <os.h>
#include "socal/hps.h"
#include "socal/socal.h"
#include "lib_def.h"
#include "os_cpu.h"
#include  <bsp_int.h>
#include "pushbtn.h"

extern OS_EVENT *SemaphoreReset;
extern OS_EVENT *SemaphoreManualX;
extern OS_EVENT *SemaphoreManualY;

void InitFPGAPushBtnsInterrupt(void)
{
	InitKey3();
	InitKey2();
	InitKey1();
}

/*********************************************************************************************************
 *                                      InitKey3(), InitKey2(), InitKey1()
 *
 * Description : Initializes the pushbuttons and their interrupts
 * 	1. Turn Timer off & turn on CONT mode
 * 	2. Install handler and set priority
 * 	3. Turn Timer on at comp level, enable int at GIC level
 * Arguments   : none.
 * Returns     : none.
 *********************************************************************************************************
 */
void InitKey3(void)
{
	QSYS_KEY3_REG_DIR &= QSYS_KEY_DIR_INPUT;
	QSYS_KEY3_REG_INT_MASK &= QSYS_KEY_IRQ_DISABLE;
	// 72 is source for irq 0 via lwhpsfpga bus, PRIO, cpu target list, ISR
	CPU_BOOLEAN err = BSP_IntVectSet(72u, 1, DEF_BIT_00, ResetBtn_Handler);
	QSYS_KEY3_REG_INT_MASK |= QSYS_KEY_IRQ_ENABLE;
	BSP_IntSrcEn(72u);
}

void InitKey2(void)
{
	QSYS_KEY2_REG_DIR &= QSYS_KEY_DIR_INPUT;
	QSYS_KEY2_REG_INT_MASK &= QSYS_KEY_IRQ_DISABLE;
	CPU_BOOLEAN err = BSP_IntVectSet(73u, 2, DEF_BIT_00, XBtn_Handler);
	QSYS_KEY2_REG_INT_MASK |= QSYS_KEY_IRQ_ENABLE;
	BSP_IntSrcEn(73u);
}

void InitKey1(void)
{
	QSYS_KEY1_REG_DIR &= QSYS_KEY_DIR_INPUT;
	QSYS_KEY1_REG_INT_MASK &= QSYS_KEY_IRQ_DISABLE;
	CPU_BOOLEAN err = BSP_IntVectSet(74u, 3, DEF_BIT_00, YBtn_Handler);
	QSYS_KEY1_REG_INT_MASK |= QSYS_KEY_IRQ_ENABLE;
	BSP_IntSrcEn(74u);
}

/*********************************************************************************************************
 *                                      		ResetBtn_Handler()
 *
 * Description : Posts to Reset task, then clears interrupt
 * Arguments   : CPU_INT32U
 * Returns     : none.
 *********************************************************************************************************
 */
void ResetBtn_Handler(CPU_INT32U cpu_id)
{
	OSSemPost(SemaphoreReset);
	QSYS_KEY3_REG_EDGE_CAP = 1;
}

/*********************************************************************************************************
 *                                         XBtn_Handler() & YBtn_Handler()
 *
 * Description : Posts ManualXMotor & ManualYMotor, and clears the interrupt
 * Arguments   : CPU_INT32U
 * Returns     : none.
 *********************************************************************************************************
 */
void XBtn_Handler(CPU_INT32U cpu_id)
{
    OSSemPost(SemaphoreManualX);
	QSYS_KEY2_REG_EDGE_CAP = 1;
}

void YBtn_Handler(CPU_INT32U cpu_id)
{
	OSSemPost(SemaphoreManualY);
	QSYS_KEY1_REG_EDGE_CAP = 1;
}


