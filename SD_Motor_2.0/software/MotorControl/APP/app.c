/*
 *********************************************************************************************************
 *                                            EXAMPLE CODE
 *
 *                          (c) Copyright 2009-2014; Micrium, Inc.; Weston, FL
 *
 *               All rights reserved.  Protected by international copyright laws.
 *
 *               Please feel free to use any application code labeled as 'EXAMPLE CODE' in
 *               your application products.  Example code may be used as is, in whole or in
 *               part, or may be used as a reference only.
 *
 *               Please help us continue to provide the Embedded community with the finest
 *               software available.  Your honesty is greatly appreciated.
 *
 *               You can contact us at www.micrium.com.
 *********************************************************************************************************
 */

/*
 *********************************************************************************************************
 *
 *                                          APPLICATION CODE
 *
 *                                            CYCLONE V SOC
 *
 * Filename      : app.c
 * Version       : V1.00
 * Programmer(s) : JBL
 * Modifications    : Nancy Minderman nancy.minderman@ualberta.ca, Brendan Bruner bbruner@ualberta.ca
 *                   Changes to this project include scatter file changes and BSP changes for port from
 *                   Cyclone V dev kit board to DE1-SoC
 *
 * Mods from Template: Jessica Huynh jhuynh@ualberta.ca
 * 					   Kelly Chin kgchin28@ualberta.ca
 *
 * 					   Changes from the template: Run Motor Task, Stepper drivers
 * 					   distance (cm) to steps & dir
 *
 *********************************************************************************************************
 * Note(s)       : none.
 *********************************************************************************************************
 */


/*
 *********************************************************************************************************
 *                                            INCLUDE FILES
 *********************************************************************************************************
 */

#include  <app_cfg.h>
#include  <lib_mem.h>

#include  <bsp.h>
#include  <bsp_int.h>
#include  <bsp_os.h>
#include  <cpu_cache.h>

#include  <cpu.h>
#include  <cpu_core.h>

#include  <os.h>
#include  <hps.h>
#include  <socal.h>
#include  <hwlib.h>
#include  <string.h> // memcpy
#include  <stdlib.h>

#include <alt_bridge_manager.h>

#include "lcd.h"
#include "uartComm.h"
#include "red_leds.h"
#include "switches.h"
#include "motorConstants.h"
#include "pushbtn.h"
#include "stepper.h"


// Compute absolute address of any slave component attached to lightweight bridge
// base is address of component in QSYS window
// This computation only works for slave components attached to the lightweight bridge
// base should be ranged checked from 0x0 - 0x1fffff

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define APP_TASK_PRIO 	   5
#define X_TASK_PRIO 	   6
#define Y_TASK_PRIO 	   7
#define RESET_TASK_PRIO    8
#define MANUAL_X_TASK_PRIO 9
#define MANUAL_Y_TASK_PRIO 10
#define UART_TASK_PRIO 	   11
#define LCD_TASK_PRIO      12

#define TASK_STACK_SIZE 4096

/*
 *********************************************************************************************************
 *                                       LOCAL GLOBAL VARIABLES
 *********************************************************************************************************
 */

CPU_STK AppTaskStartStk[TASK_STACK_SIZE];
CPU_STK RunMotorXTaskStk[TASK_STACK_SIZE];
CPU_STK RunMotorYTaskStk[TASK_STACK_SIZE];
CPU_STK UartListenerTaskStk[TASK_STACK_SIZE];
CPU_STK ResetTaskStk[TASK_STACK_SIZE];
CPU_STK ManualXTaskStk[TASK_STACK_SIZE];
CPU_STK ManualYTaskStk[TASK_STACK_SIZE];
CPU_STK LcdWriteTaskStk[TASK_STACK_SIZE];

/*
 *********************************************************************************************************
 *                                      LOCAL FUNCTION PROTOTYPES
 *********************************************************************************************************
 */

static  void  AppTaskStart              (void        *p_arg);
static  void  ResetTask					(void 	     *p_arg);
static  void  ManualXTask               (void        *p_arg);
static  void  ManualYTask               (void        *p_arg);

static  void  UartListenerTask 			(void 		 *p_arg);

static  void  RunMotorXTask       		(void        *p_arg);
static  void  RunMotorYTask       		(void        *p_arg);

static  void  LcdWriteTask       		(void        *p_arg);

/*
 *********************************************************************************************************
 *                                      Semiphores, Queues, and Interrupts
 *********************************************************************************************************
 */

OS_EVENT *SemaphoreUartReset; // posted by Reset, pend by Uart

OS_EVENT *SemaphoreReset;   // posted by Key3, pend by ResetTask
OS_EVENT *SemaphoreManualX; // posted by Key2, pend by MoveMotorX
OS_EVENT *SemaphoreManualY; // posted by Key1, pend by MoveMotorY

OS_EVENT *SemaphoreMotorX; // post pend b/w uart and motor x tasks
OS_EVENT *SemaphoreMotorY; // post pend b/w uart and motor y tasks

#define MAX_NBR_MSGS 16
OS_EVENT *UartQueue; // unparsed from interrupt
void *MsgStorageUart[MAX_NBR_MSGS];

OS_EVENT *UartXQueue; // from parsed to motor X
OS_EVENT *UartYQueue; // from parsed to motor Y
void *MsgStorageX[MAX_NBR_MSGS];
void *MsgStorageY[MAX_NBR_MSGS];

OS_EVENT *LcdMsgQueue;
void *MsgStorageLcd[MAX_NBR_MSGS];

/*********************************************************************************************************
 *                                               main()
 *
 * Description : Entry point for C code.
 * Arguments   : none.
 * Returns     : none.
 * Note(s)     : (1) It is assumed that your code will call main() once you have performed all necessary
 *                   initialisation.
 *********************************************************************************************************
 */

int main ()
{
    INT8U os_err;
    BSP_WatchDog_Reset();                                       /* Reset the watchdog as soon as possible.              */

    /* Scatter loading is complete. Now the caches can be activated.*/
    BSP_BranchPredictorEn();                                    /* Enable branch prediction.                            */
    BSP_L2C310Config();                                         /* Configure the L2 cache controller.                   */
    BSP_CachesEn();                                             /* Enable L1 I&D caches + L2 unified cache.             */

    CPU_Init();
    Mem_Init();
    BSP_Init();
    OSInit();
    InitLCD();

    /*Semaphore and Message Queue Creation*/
    SemaphoreReset 	 = OSSemCreate(0);
    SemaphoreUartReset = OSSemCreate(0);
    SemaphoreManualX = OSSemCreate(0);
    SemaphoreManualY = OSSemCreate(0);
    SemaphoreMotorX  = OSSemCreate(0);
    SemaphoreMotorY  = OSSemCreate(0);

    LcdMsgQueue = OSQCreate(MsgStorageLcd, MAX_NBR_MSGS);
    UartQueue  = OSQCreate(MsgStorageUart, MAX_NBR_MSGS);
    UartXQueue = OSQCreate(MsgStorageX, MAX_NBR_MSGS);
    UartYQueue = OSQCreate(MsgStorageY, MAX_NBR_MSGS);

    /////////////////////////////////////////////////////////////////////////////////
    // Create the AppTaskStart
    os_err = OSTaskCreateExt((void (*)(void *)) AppTaskStart,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&AppTaskStartStk[TASK_STACK_SIZE - 1],
                             (INT8U) APP_TASK_PRIO,(INT16U) APP_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&AppTaskStartStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the RunMotorXTask
    os_err = OSTaskCreateExt((void (*)(void *)) RunMotorXTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&RunMotorXTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) X_TASK_PRIO,(INT16U) X_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&RunMotorXTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the RunMotorYTask
    os_err = OSTaskCreateExt((void (*)(void *)) RunMotorYTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&RunMotorYTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) Y_TASK_PRIO,(INT16U) Y_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&RunMotorYTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the ResetTask
    os_err = OSTaskCreateExt((void (*)(void *)) ResetTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&ResetTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) RESET_TASK_PRIO,(INT16U) RESET_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&ResetTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the ResetTask
    os_err = OSTaskCreateExt((void (*)(void *)) ManualXTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&ManualXTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) MANUAL_X_TASK_PRIO,(INT16U) MANUAL_X_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&ManualXTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the ResetTask
    os_err = OSTaskCreateExt((void (*)(void *)) ManualYTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&ManualYTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) MANUAL_Y_TASK_PRIO,(INT16U) MANUAL_Y_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&ManualYTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the UartTask
    os_err = OSTaskCreateExt((void (*)(void *)) UartListenerTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&UartListenerTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) UART_TASK_PRIO,(INT16U) UART_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&UartListenerTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    /////////////////////////////////////////////////////////////////////////////////
    // Create the LCD Task
    os_err = OSTaskCreateExt((void (*)(void *)) LcdWriteTask,   /* Create the start task.                               */
                             (void*) 0, (OS_STK* )&LcdWriteTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U) LCD_TASK_PRIO,(INT16U) LCD_TASK_PRIO,  // reuse prio for ID
                             (OS_STK*)&LcdWriteTaskStk[0],(INT32U) TASK_STACK_SIZE,(void*)0,
                             (INT16U)(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));
    if (os_err != OS_ERR_NONE) {; /* Handle error. */}

    CPU_IntEn();
    OSStart();
}

/*********************************************************************************************************
 *                                           App_TaskStart()
 * Description : Startup task example code.
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       : (1) The ticker MUST be initialised AFTER multitasking has started.
 *********************************************************************************************************
 */
static  void  AppTaskStart (void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */

    ALT_BRIDGE_t lw_bridge = ALT_BRIDGE_LWH2F;
    ALT_STATUS_CODE err = alt_bridge_init(lw_bridge, NULL,NULL);

    InitFPGAPushBtnsInterrupt();
    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
        OSTimeDlyHMSM(0, 0, 1, 0);
    }
}

/**********************************************************************************************************
 *                                           ResetTask()
 *
 * Description : Task that will stop both motors and reset position to center (manual)
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       :
 *********************************************************************************************************
 */
static void ResetTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */
    char lcdBuf[50] = "Please press Key 3 twice to begin\n";
    INT8U err = OSQPost(LcdMsgQueue, (void*)lcdBuf);

    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
        OSSemPend(SemaphoreReset, 0, &err);
        char lcd[50] = "State: In Reset\n";
        INT8U err = OSQPost(LcdMsgQueue, (void*)lcd);

        // stop motors where they are
        MoveDistCm(motorX, 0);
        MoveDistCm(motorY, 0);

        OSSemPend(SemaphoreReset, 0, &err); // wait to press and begin listen
        OSSemPost(SemaphoreUartReset);
    }
}

/**********************************************************************************************************
 *                                        ManualXTask() & ManualYTask()
 *
 * Description : These two tasks manually move the motors via pushbuttons
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       :
 *********************************************************************************************************
 */
static void ManualXTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */
    INT8U err;

    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
        OSSemPend(SemaphoreManualX, 0, &err);
        MoveDistCm(motorX, 2*GetPosNegSwitch());
    }
}

static void ManualYTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */
    INT8U err;

    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
        OSSemPend(SemaphoreManualY, 0, &err);
        MoveDistCm(motorY, 2*GetPosNegSwitch());
    }
}

/**********************************************************************************************************
 *                                           UartListenerTask()
 *
 * Description : Task that will listen to UART-USB and send coords to motors
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       :
 *********************************************************************************************************
 */
static void UartListenerTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                /* Configure and enable OS tick interrupt.              */
    char xCoord[8];
    char yCoord[8];

	initUART();

	INT8U err;
	OSSemPend(SemaphoreMotorX, 0 , &err);
	OSSemPend(SemaphoreMotorY, 0 , &err);

	for(;;)
	{
	    BSP_WatchDog_Reset();                   /* Reset the watchdog.                                  */
	    OSSemPend(SemaphoreUartReset, 0, &err); //waits for reset to be done
		char lcd[50] = "State: Waiting for Uart Coords\n";
	    INT8U err = OSQPost(LcdMsgQueue, (void*)lcd);

	    void* buf = OSQPend(UartQueue, 0, &err);
		char* msg = (char*)buf;
		OSQFlush(UartQueue);

		int commaIndex = 0;
		for(int i = 0; i < strlen(msg); i++)
		{
			if(msg[i] == ',')
			{
				commaIndex = i;
				break;
			}
		}

		if(commaIndex == 0 || commaIndex == (strlen(msg) - 1))
		{
			char invalid[50] = "State: Invalid Message\n";
		    INT8U err = OSQPost(LcdMsgQueue, (void*)invalid);
			continue;
		}

		memcpy(xCoord, &msg[0], commaIndex);
		xCoord[commaIndex] = '\0';
		int x = atoi(xCoord);

		memcpy(yCoord, &msg[commaIndex+1], strlen(msg) - commaIndex - 1);
		yCoord[strlen(msg) - commaIndex] = '\0';
		int y = atoi(yCoord);

		if(x > 16 || y > 16 || x < -16 || y < -16)
		{
			char inv[50] = "State: Out of Bounds\n";
		    INT8U err = OSQPost(LcdMsgQueue, (void*)inv);
		    continue;
		}

		char lcdBuf[50] = "State: Moving motors";
	    err = OSQPost(LcdMsgQueue, (void*)lcdBuf);

		err = OSQPost(UartXQueue, (void *)x);
		err = OSQPost(UartYQueue, (void *)y);

		OSSemPend(SemaphoreMotorX, 0 , &err);
		OSSemPend(SemaphoreMotorY, 0 , &err);
    	BSP_LED_Off();
        OSTimeDlyHMSM(0, 0, 0, 500);
	}
}

/*********************************************************************************************************
 *                                           RunMotorXTask()
 * Description : Run Stepper motor X
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       : (1) The ticker MUST be initialised AFTER multitasking has started.
 *********************************************************************************************************
 */
static  void  RunMotorXTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                /* Configure and enable OS tick interrupt.              */
    BSP_WatchDog_Reset();                                /* Reset the watchdog.                                  */

    INT32U currFreq = 1000;
    InitMotor(motorX, currFreq);
    MoveDistCm(motorX, 0);
    OSTimeDlyHMSM(0, 0, 0, 500);
    MoveDistCm(motorX, 16);
    OSTimeDlyHMSM(0, 0, 0, 500);
    OSSemPost(SemaphoreMotorX);

    INT8U err;
    for(;;)
    {
        SetFrequency(motorX, currFreq);
		void *xCoord = OSQPend(UartXQueue, 0, &err);
		int dist = xCoord;
		// Move that distance then return after timeout
    	MoveDistCm(motorX, dist);
        OSTimeDlyHMSM(0, 0, 5, 0);
        SetFrequency(motorX, 150);
        MoveDistCm(motorX, dist*(-1));
        OSSemPost(SemaphoreMotorX);
    }
}

/*********************************************************************************************************
 *                                           RunMotorYTask()
 * Description : Run Stepper motor y
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       : (1) The ticker MUST be initialised AFTER multitasking has started.
 *********************************************************************************************************
 */
static  void  RunMotorYTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                /* Configure and enable OS tick interrupt.              */
    BSP_WatchDog_Reset();                                /* Reset the watchdog.                                  */

    INT32U currFreq = 900;
    InitMotor(motorY, currFreq);
    MoveDistCm(motorY, 0);
    OSTimeDlyHMSM(0, 0, 0, 500);
    MoveDistCm(motorY, 16);
    OSTimeDlyHMSM(0, 0, 0, 500);
    OSSemPost(SemaphoreMotorY);

    INT8U err;
    for(;;)
    {
		SetFrequency(motorY, currFreq);
    	void *yCoord = OSQPend(UartYQueue, 0, &err);
		int dist = yCoord;
		// Move that distance then return after timeout
    	MoveDistCm(motorY, dist);
        OSTimeDlyHMSM(0, 0, 5, 0);
		SetFrequency(motorY, 150);
        MoveDistCm(motorY, dist*(-1));
        OSSemPost(SemaphoreMotorY);
    }
}

/*********************************************************************************************************
 *                                           LcdWriteTask()
 * Description : Write to the LCD, lowest priority task
 * Arguments   : p_arg, Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       : (1) The ticker MUST be initialised AFTER multitasking has started.
 *********************************************************************************************************
 */
static void LcdWriteTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */
    INT8U err;
	ClearLCD();
	PrintStringLCD("Initializing LCD\n");

    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
    	char *buf = OSQPend(LcdMsgQueue, 0, &err);
    	ClearLCD();

    	PrintStringLCD(buf);
    }
}
