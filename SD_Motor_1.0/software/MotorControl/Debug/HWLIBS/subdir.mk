################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../HWLIBS/alt_16550_uart.c \
../HWLIBS/alt_bridge_manager.c \
../HWLIBS/alt_clock_manager.c \
../HWLIBS/alt_fpga_manager.c \
../HWLIBS/motorConstants.c \
../HWLIBS/pushbtn.c \
../HWLIBS/red_leds.c \
../HWLIBS/stepper.c \
../HWLIBS/uartComm.c 

C_DEPS += \
./HWLIBS/alt_16550_uart.d \
./HWLIBS/alt_bridge_manager.d \
./HWLIBS/alt_clock_manager.d \
./HWLIBS/alt_fpga_manager.d \
./HWLIBS/motorConstants.d \
./HWLIBS/pushbtn.d \
./HWLIBS/red_leds.d \
./HWLIBS/stepper.d \
./HWLIBS/uartComm.d 

OBJS += \
./HWLIBS/alt_16550_uart.o \
./HWLIBS/alt_bridge_manager.o \
./HWLIBS/alt_clock_manager.o \
./HWLIBS/alt_fpga_manager.o \
./HWLIBS/motorConstants.o \
./HWLIBS/pushbtn.o \
./HWLIBS/red_leds.o \
./HWLIBS/stepper.o \
./HWLIBS/uartComm.o 


# Each subdirectory must supply rules for building sources it contributes
HWLIBS/%.o: ../HWLIBS/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\APP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_1.0\software\MotorControl\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="HWLIBS" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


