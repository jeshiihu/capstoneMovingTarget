################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../BSP/OS/bsp_os.c 

C_DEPS += \
./BSP/OS/bsp_os.d 

OBJS += \
./BSP/OS/bsp_os.o 


# Each subdirectory must supply rules for building sources it contributes
BSP/OS/%.o: ../BSP/OS/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\APP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmWithReset\software\MotorDriver\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="BSP/OS" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


