################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../uC-LIBS/lib_ascii.c \
../uC-LIBS/lib_math.c \
../uC-LIBS/lib_mem.c \
../uC-LIBS/lib_str.c 

C_DEPS += \
./uC-LIBS/lib_ascii.d \
./uC-LIBS/lib_math.d \
./uC-LIBS/lib_mem.d \
./uC-LIBS/lib_str.d 

OBJS += \
./uC-LIBS/lib_ascii.o \
./uC-LIBS/lib_math.o \
./uC-LIBS/lib_mem.o \
./uC-LIBS/lib_str.o 


# Each subdirectory must supply rules for building sources it contributes
uC-LIBS/%.o: ../uC-LIBS/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM C Compiler 5'
	armcc --cpu=Cortex-A9 --no_unaligned_access -Dsoc_cv_av -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\APP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\BSP" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\BSP\OS" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av" -I"C:\intelFPGA\17.0\embedded\ip\altera\hps\altera_hps\hwlib\include\soc_cv_av\socal" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\HWLIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-CPU\ARM-Cortex-A" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-CPU" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uC-LIBS" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uCOS-II\Ports" -I"C:\Users\jhuynh\Desktop\Capstone\MotorPwmXY\software\MotorDriver\uCOS-II\Source" --c99 --gnu -O0 -g --md --depend_format=unix_escaped --no_depend_system_headers --depend_dir="uC-LIBS" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

