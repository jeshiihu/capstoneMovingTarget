/*
 * uartComm.h
 *
 *  Created on: Mar 24, 2018
 *      Author: kgchin & twmathie & jhuynh
 */

#ifndef HWLIBS_UARTCOMM_H_
#define HWLIBS_UARTCOMM_H_

void initUART(void);
void Uart_ISR_Handler(CPU_INT32U cpu_id);

#endif /* HWLIBS_UARTCOMM_H_ */
