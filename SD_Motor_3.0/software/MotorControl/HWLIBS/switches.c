/*
 * switches.c
 *
 *  Created on: Mar 29, 2018
 *      Author: jhuynh
 */
#include "socal/hps.h"
#include "socal/socal.h"
#include "lib_def.h"
#include "os_cpu.h"
#include  <os.h>
#include "switches.h"

/*********************************************************************************************************
 *                                           GetPosNegSwitch()
 * Description : Retrieves the first switch (from the right)
 * 		- Up = positive
 * 		- Down = negative
 * Arguments   : none.
 * Returns     : int -1/1
 *********************************************************************************************************
 */
int GetPosNegSwitch(void)
{
    INT32U currSwitch = alt_read_word(SW_BASE);
    if(currSwitch != 0) return 1; // up = positive
    return -1; // down = neg
}
