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
#include <stdlib.h>

#include "uartComm.h"
#include "pushbtn.h"
#include "motorConstants.h"
#include "stepper.h"

// Compute absolute address of any slave component attached to lightweight bridge
// base is address of component in QSYS window
// This computation only works for slave components attached to the lightweight bridge
// base should be ranged checked from 0x0 - 0x1fffff

#define FPGA_TO_HPS_LW_ADDR(base)  ((void *) (((char *)  (ALT_LWFPGASLVS_ADDR))+ (base)))

#define APP_TASK_PRIO 5
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

/*
 *********************************************************************************************************
 *                                      LOCAL FUNCTION PROTOTYPES
 *********************************************************************************************************
 */

static  void  AppTaskStart              (void        *p_arg);

static  void  UartListenerTask 			(void 		 *p_arg);
// may need reset flag, that uart will check
static  void  ResetTask                 (void 		 *p_arg);
static  void  MoveReverseSteps          (enum Motor   motor);

static  void  RunMotorXTask       		(void        *p_arg);
static  void  RunMotorYTask       		(void        *p_arg);

//static  void  TestSeqeuence             (void                  );
static  void  MoveDistCm				(enum Motor m, int dist);

/*
 *********************************************************************************************************
 *                                      Semiphores, Queues, and Interrupts
 *********************************************************************************************************
 */
OS_EVENT *SemaphoreReset;
OS_EVENT *SemaphoreMotorX;
OS_EVENT *SemaphoreMotorY;

#define MAX_NBR_MSGS 255
OS_EVENT *UartXQueue;
OS_EVENT *UartYQueue;
void *MsgStorageX[MAX_NBR_MSGS];
void *MsgStorageY[MAX_NBR_MSGS];

/*
 *********************************************************************************************************
 *                                               main()
 *
 * Description : Entry point for C code.
 *
 * Arguments   : none.
 *
 * Returns     : none.
 *
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

    /*Semaphore and Message Queue Creation*/
    SemaphoreReset = OSSemCreate(0);
    SemaphoreMotorX = OSSemCreate(0);
    SemaphoreMotorY = OSSemCreate(0);
    UartXQueue = OSQCreate(MsgStorageX, MAX_NBR_MSGS);
    UartYQueue = OSQCreate(MsgStorageY, MAX_NBR_MSGS);

    os_err = OSTaskCreateExt((void (*)(void *)) AppTaskStart,   /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&AppTaskStartStk[TASK_STACK_SIZE - 1],
                             (INT8U           ) APP_TASK_PRIO,
                             (INT16U          ) APP_TASK_PRIO,  // reuse prio for ID
                             (OS_STK        * )&AppTaskStartStk[0],
                             (INT32U          ) TASK_STACK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

    if (os_err != OS_ERR_NONE) {
        ; /* Handle error. */
    }


    os_err = OSTaskCreateExt((void (*)(void *)) RunMotorXTask,   /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&RunMotorXTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U           ) APP_TASK_PRIO+1,
                             (INT16U          ) APP_TASK_PRIO+1,  // reuse prio for ID
                             (OS_STK        * )&RunMotorXTaskStk[0],
                             (INT32U          ) TASK_STACK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

    if (os_err != OS_ERR_NONE) {
        ; /* Handle error. */
    }

    os_err = OSTaskCreateExt((void (*)(void *)) RunMotorYTask,   /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&RunMotorYTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U           ) APP_TASK_PRIO+2,
                             (INT16U          ) APP_TASK_PRIO+2,  // reuse prio for ID
                             (OS_STK        * )&RunMotorYTaskStk[0],
                             (INT32U          ) TASK_STACK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

    if (os_err != OS_ERR_NONE) {
        ; /* Handle error. */
    }

    os_err = OSTaskCreateExt((void (*)(void *)) UartListenerTask,   /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&UartListenerTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U           ) APP_TASK_PRIO+3,
                             (INT16U          ) APP_TASK_PRIO+3,  // reuse prio for ID
                             (OS_STK        * )&UartListenerTaskStk[0],
                             (INT32U          ) TASK_STACK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

    if (os_err != OS_ERR_NONE) {
        ; /* Handle error. */
    }

    os_err = OSTaskCreateExt((void (*)(void *)) ResetTask,   /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&ResetTaskStk[TASK_STACK_SIZE - 1],
                             (INT8U           ) APP_TASK_PRIO+4,
                             (INT16U          ) APP_TASK_PRIO+4,  // reuse prio for ID
                             (OS_STK        * )&ResetTaskStk[0],
                             (INT32U          ) TASK_STACK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

    if (os_err != OS_ERR_NONE) {
        ; /* Handle error. */
    }



    CPU_IntEn();
    OSStart();
}

/*
 *********************************************************************************************************
 *                                           App_TaskStart()
 *
 * Description : Startup task example code.
 *
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 *
 * Returns     : none.
 *
 * Created by  : main().
 *
 * Notes       : (1) The ticker MUST be initialised AFTER multitasking has started.
 *********************************************************************************************************
 */

static  void  AppTaskStart (void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                       /* Configure and enable OS tick interrupt.              */
    InitFPGAPushBtnInterrupt();

    for(;;) {
        BSP_WatchDog_Reset();                                   /* Reset the watchdog.                                  */
        OSTimeDlyHMSM(0, 0, 0, 500);
        BSP_LED_On();
        OSTimeDlyHMSM(0, 0, 0, 500);
        BSP_LED_Off();
    }
}

/*
 *********************************************************************************************************
 *                                           UartListenerTask()
 *
 * Description : Highest priority task that will stop both motors and reset position to center
 *
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       :
 *********************************************************************************************************
 */
static void UartListenerTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                /* Configure and enable OS tick interrupt.              */
    BSP_WatchDog_Reset();                                /* Reset the watchdog.           */

	char buffer[16];

	initUART();

	INT8U err;
	OSSemPend(SemaphoreMotorX, 0 , &err);
	OSSemPend(SemaphoreMotorY, 0 , &err);

	for(;;){

		readFIFO(buffer);
		printf("current buffer contents: %s \n",buffer);

		int commaIndex = 0;
		for(int i = 0; i < strlen(buffer); i++)
		{
			if(buffer[i] == ',')
			{
				commaIndex = i;
				break;
			}
		}

		if(commaIndex == 0 || commaIndex == (strlen(buffer) - 1))
			continue;

		char xCoord[commaIndex+1];
		memcpy(xCoord, &buffer[0], commaIndex);
		xCoord[commaIndex] = '\0';
		int x = atoi(xCoord);

		char yCoord[strlen(buffer) - commaIndex];
		memcpy(yCoord, &buffer[commaIndex+1], strlen(buffer) - commaIndex - 1);
		yCoord[strlen(buffer) - commaIndex] = '\0';
		int y = atoi(yCoord);

		err = OSQPost(UartXQueue, (void *)x);
		err = OSQPost(UartYQueue, (void *)y);

		OSSemPend(SemaphoreMotorX, 0 , &err);
		OSSemPend(SemaphoreMotorY, 0 , &err);
        OSTimeDlyHMSM(0, 0, 0, 500);
	}
}

/*
 *********************************************************************************************************
 *                                           ResetTask()
 *
 * Description : Highest priority task that will stop both motors and reset position to center
 *
 * Arguments   : p_arg       Argument passed by 'OSTaskCreate()'.
 * Returns     : none.
 * Created by  : main().
 * Notes       :
 *********************************************************************************************************
 */
static void ResetTask(void *p_arg)
{
    BSP_OS_TmrTickInit(OS_TICKS_PER_SEC);                /* Configure and enable OS tick interrupt.              */
    BSP_WatchDog_Reset();                                /* Reset the watchdog.                                  */
    int counter = 0;
    INT8U err;
    for(;;)
    {	// SemaphoreReset should == -1 at this pend
//        OSSemPend(SemaphoreReset, 0 , &err);
//        OSSchedLock(); // no multithreading or context switching
//        counter = counter + 1;
//		printf("=======(%d) In Reset task=======\n", counter);
//
//        MoveReverseSteps(motorX);
//		printf("reversing motor X\n");
//        MoveReverseSteps(motorY);
//		printf("reversing motor Y\n");
//		printf("Done reset task\n\n\n");
		OSTimeDlyHMSM(0, 0, 3, 0);
//		OSSchedUnlock();
    }
}

static void MoveReverseSteps(enum Motor motor)
{
    INT16U currStep = GetCurrSteps(motor);    INT32U currFreq = 1000;
    enum Direction currDir = GetDirection(motor);
    StepMotor(motor, 0);
	OSTimeDlyHMSM(0, 0, 3, 0);

    enum Direction revDir = cw;
    if(currDir == cw)
    	revDir = ccw;

    SetDirection(motor, revDir);
    int currDist = Steps2Distance(currStep, revDir);
	printf("Reverse: %d cm\n", currDist);
    StepMotor(motor, currStep);
}

/*
 *********************************************************************************************************
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
    MoveDistCm(motorX, 16);
    OSTimeDlyHMSM(0, 0, 0, 500);
    OSSemPost(SemaphoreMotorX);

    INT8U err;
    for(;;)
    {
        SetFrequency(motorX, currFreq);
		void *xCoord = OSQPend(UartXQueue, 0, &err);
		int dist = xCoord;
		printf("X Coord: %d\n", dist);
		// Move that distance then return after timeout
    	MoveDistCm(motorX, dist);
        OSTimeDlyHMSM(0, 0, 5, 0);
        SetFrequency(motorX, 150);
        MoveDistCm(motorX, dist*(-1));
        OSSemPost(SemaphoreMotorX);
    }
}

/*
 *********************************************************************************************************
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

    INT32U currFreq = 1000;
    InitMotor(motorY, currFreq);
    MoveDistCm(motorY, 16);
    OSTimeDlyHMSM(0, 0, 0, 500);
    OSSemPost(SemaphoreMotorY);

    currFreq = 800;
    INT8U err;
    for(;;)
    {
		SetFrequency(motorY, currFreq);
    	void *yCoord = OSQPend(UartYQueue, 0, &err);
		int dist = yCoord;
		printf("Y Coord: %d\n", dist);
		// Move that distance then return after timeout
    	MoveDistCm(motorY, dist);
        OSTimeDlyHMSM(0, 0, 5, 0);
		SetFrequency(motorY, 150);
        MoveDistCm(motorY, dist*(-1));
        OSSemPost(SemaphoreMotorY);
    }
}

static void MoveDistCm(enum Motor m, int dist)
{	/* Ensures that the motors are not driven at a distance
	 * that is greater what is possible */
	if(dist > 16) dist = 16;
	if(dist < -16) dist = -16;

	enum Direction dir = cw;
	if(m == motorY)
	{ dir = YCoord2Dir(dist);}
	else
	{ dir = XCoord2Dir(dist);}

	SetDirection(m, dir);
	INT16U steps = XYCoord2Steps(dist);
    StepMotor(m, steps);
}
