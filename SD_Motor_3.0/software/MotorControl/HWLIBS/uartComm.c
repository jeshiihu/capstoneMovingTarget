/*
 * uartComm.c
 *
 *  Created on: Mar 24, 2018
 *      Author: kgchin & twmathie
 */
#include "lib_def.h"
#include  <bsp_int.h>
#include  <os.h>

#include "alt_16550_uart.h"
#include "uartComm.h"

extern OS_EVENT *UartQueue;
struct ALT_16550_HANDLE_s uartHandle;

/*
*********************************************************************************************************
*                                               InitUART()
*
* Description : initializes the uart controller on the HPS. UART0 is used, with baudrate 115200.
* 				The FIFO buffer is also initialized to receive more than one character from the pi.
* Arguments   : none.
* Returns     : none.
*
*********************************************************************************************************
*/
void initUART(void)
{
	ALT_STATUS_CODE status =  alt_16550_baudrate_set(&uartHandle, ALT_16550_BAUDRATE_115200); // ALT_CLK_L4_SP clock
	status =  alt_16550_init(ALT_16550_DEVICE_SOCFPGA_UART0,NULL,NULL,&uartHandle);

	status =  alt_16550_enable(&uartHandle);
	status =  alt_16550_fifo_enable(&uartHandle);
	//Install handler and set prio
	CPU_BOOLEAN err = BSP_IntVectSet(194u, 4, DEF_BIT_00, Uart_ISR_Handler);

	status = alt_16550_fifo_clear_rx(&uartHandle);
	status = alt_16550_fifo_trigger_set_rx(&uartHandle, ALT_16550_FIFO_TRIGGER_RX_QUARTER_FULL);
	status = alt_16550_int_disable_tx(&uartHandle);
	status = alt_16550_int_enable_rx(&uartHandle);

	BSP_IntSrcEn(194u);
}

/*
*********************************************************************************************************
*                                               Uart_ISR_Handler()
* Description : Interrupt handler, that reads from the fifo buffer and posts to the queue
* Arguments   : char *buffer ; a pointer place the contents into
* Returns     : none.
*********************************************************************************************************
*/
void Uart_ISR_Handler(CPU_INT32U cpu_id)
{
	char buffer[16];
	alt_16550_fifo_read(&uartHandle, buffer, 16);
	INT8U err = OSQPost(UartQueue, (void*)buffer);
}
