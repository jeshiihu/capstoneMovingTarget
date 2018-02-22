//
//  main.c
//  StepperMotorDriver
//
//  Created by Jessica Huynh on 2018-02-20.
//  Copyright © 2018 Jessica Huynh. All rights reserved.
//

#include <stdio.h>
#include "stepper.h"


void PrintParameters(void);

int main(int argc, const char * argv[]) {
    // insert code here...
    printf("Hello, World!\n");
    
    InitMotor();
    PrintParameters();
    
    SetDirection(ccw);
    PrintParameters();
    
    SetPulses(5);
    PrintParameters();
    
    SetPulses(-5);
    PrintParameters();
    
    SetDirection(cw);
    SetPulses(300);
    PrintParameters();
    
    return 0;
}

void PrintParameters()
{
    printf("\r\n=============== Current Settings ===============\r\n");

    if(GetDirection() == cw)
        printf("Direction: %s\r\n", "Clockwise");
    else
        printf("Direction: %s\r\n", "Counter Clockwise");

    printf("Pulses: %d\r\n", GetPulses());
}

