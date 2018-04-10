################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
S_SRCS += \
../uCOS-II/Ports/os_cpu_a_vfp-d32.s 

C_SRCS += \
../uCOS-II/Ports/os_cpu_c.c 

S_DEPS += \
./uCOS-II/Ports/os_cpu_a_vfp-d32.d 

C_DEPS += \
./uCOS-II/Ports/os_cpu_c.d 

OBJS += \
./uCOS-II/Ports/os_cpu_a_vfp-d32.o \
./uCOS-II/Ports/os_cpu_c.o 


# Each subdirectory must supply rules for building sources it contributes
uCOS-II/Ports/os_cpu_a_vfp-d32.o: ../uCOS-II/Ports/os_cpu_a_vfp-d32.s
	@echo 'Building file: $<'
	@echo 'Invoking: ARM Assembler 5'
	armasm --cpu=Cortex-A9 --no_unaligned_access -g --md --depend_format=unix_escaped --depend="uCOS-II/Ports/os_cpu_a_vfp-d32.d" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

uCOS-II/Ports/%.o: ../uCOS-II/Ports/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\APP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\SD_Motor_3.0\software\MotorControl\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="uCOS-II/Ports" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


