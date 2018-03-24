/*
 * uartComm.c
 *
 *  Created on: Mar 24, 2018
 *      Author: kgchin & twmathie
 */

#include "alt_16550_uart.h"

struct ALT_16550_HANDLE_s uartHandle;

/*
*********************************************************************************************************
*                                               InitUART()
*
* Description : initializes the uart controller on the HPS. UART0 is used, with baudrate 115200.
* 				The FIFO buffer is also initialized to receive more than one character from the pi.
*
* Arguments   : none.
* Returns     : none.
*
*********************************************************************************************************
*/
void initUART()
{
	ALT_STATUS_CODE status;
	status =  alt_16550_baudrate_set(&uartHandle, ALT_16550_BAUDRATE_115200); // ALT_CLK_L4_SP clock
	status =  alt_16550_init(ALT_16550_DEVICE_SOCFPGA_UART0,NULL,NULL,&uartHandle);
	status =  alt_16550_enable(&uartHandle);
	status =  alt_16550_fifo_enable(&uartHandle);
	status  = alt_16550_fifo_clear_rx(&uartHandle);
	status =  alt_16550_fifo_trigger_set_rx(&uartHandle, ALT_16550_FIFO_TRIGGER_RX_ANY);
	status =  alt_16550_int_enable_rx(&uartHandle);

}

/*
*********************************************************************************************************
*                                               readFIFO()
* Description : This is a wrapper around the fifo_read function available from altera. It simply copies the
* 				contents of the fifo buffer into the provided address.
*
* Arguments   : char *buffer ; a pointer place the contents into
* Returns     : none.
*
*********************************************************************************************************
*/

void readFIFO(char *buffer)
{
	alt_16550_fifo_read(&uartHandle, buffer, 16);

}
