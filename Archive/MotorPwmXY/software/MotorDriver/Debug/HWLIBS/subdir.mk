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
../HWLIBS/stepper.c 

C_DEPS += \
./HWLIBS/alt_16550_uart.d \
./HWLIBS/alt_bridge_manager.d \
./HWLIBS/alt_clock_manager.d \
./HWLIBS/alt_fpga_manager.d \
./HWLIBS/motorConstants.d \
./HWLIBS/stepper.d 

OBJS += \
./HWLIBS/alt_16550_uart.o \
./HWLIBS/alt_bridge_manager.o \
./HWLIBS/alt_clock_manager.o \
./HWLIBS/alt_fpga_manager.o \
./HWLIBS/motorConstants.o \
./HWLIBS/stepper.o 


# Each subdirectory must supply rules for building sources it contributes
HWLIBS/%.o: ../HWLIBS/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\APP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="HWLIBS" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


