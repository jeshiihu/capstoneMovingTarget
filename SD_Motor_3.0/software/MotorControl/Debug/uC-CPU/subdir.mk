################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../uC-CPU/cpu_core.c 

C_DEPS += \
./uC-CPU/cpu_core.d 

OBJS += \
./uC-CPU/cpu_core.o 


# Each subdirectory must supply rules for building sources it contributes
uC-CPU/%.o: ../uC-CPU/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\APP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="uC-CPU" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


