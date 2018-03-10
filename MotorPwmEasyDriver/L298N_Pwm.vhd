-- L298N_Pwm.vhd

-- This file was auto-generated as a prototype implementation of a module
-- created in component editor.  It ties off all outputs to ground and
-- ignores all inputs.  It needs to be edited to make it do something
-- useful.
-- 
-- This file will not be automatically regenerated.  You should check it in
-- to your version control system if you want to keep it.

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity L298N_Pwm is
	port (
		reset_n            : in  std_logic                     := '0';             --       reset.reset_n
		clk                : in  std_logic                     := '0';             --       clock.clk
		a                  : out std_logic;                                        -- conduit_end.a
		b                  : out std_logic;                                        --            .b
		a_comp             : out std_logic;                                        --            .a_comp
		b_comp             : out std_logic;                                        --            .b_comp
		en_a               : out std_logic;                                        --            .en_a
		en_b               : out std_logic;                                        --            .en_b
		
		step_write_n       : in  std_logic                     := '0';             --        step.write_n
		step_writedata     : in  std_logic_vector(15 downto 0) := (others => '0'); --            .writedata
		step_read_n        : in  std_logic                     := '0';             --            .read_n
		step_readdata      : out std_logic_vector(15 downto 0);                    --            .readdata
		
		cycle_write_n      : in  std_logic                     := '0';             --       cycle.write_n
		cycle_writedata    : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		cycle_readdata     : out std_logic_vector(31 downto 0);                    --            .readdata
		cycle_read_n       : in  std_logic                     := '0';             --            .read_n
		
		duty_write_n       : in  std_logic                     := '0';             --        duty.write_n
		duty_writedata     : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		duty_read_n        : in  std_logic                     := '0';             --            .read_n
		duty_readdata      : out std_logic_vector(31 downto 0);                    --            .readdata
		
		dir_write_n        : in  std_logic                     := '0';             --         dir.write_n
		dir_writedata      : in  std_logic_vector(7 downto 0)  := (others => '0'); --            .writedata
		dir_read_n         : in  std_logic                     := '0';             --            .read_n
		dir_readdata       : out std_logic_vector(7 downto 0);                     --            .readdata
		
		stepMode_read_n    : in  std_logic                     := '0';             --    stepMode.read_n
		stepMode_readdata  : out std_logic_vector(7 downto 0);                     --            .readdata
		stepMode_write_n   : in  std_logic                     := '0';             --            .write_n
		stepMode_writedata : in  std_logic_vector(7 downto 0)  := (others => '0')  --            .writedata
	);
end entity L298N_Pwm;

architecture rtl of L298N_Pwm is
	-- Signals used in the pwm process
	signal currStep 		: std_logic_vector(2 downto 0) := "000"; -- to retreive step seq
	signal numSteps 		: std_logic_vector(15 downto 0) := (others => '0'); -- step counter


-- Process that produces the step sequence from a PWM
-- by set frequency and duty cycle	
begin
	write_to_hBridge:
	process(clk, reset_n,step_write_n, cycle_write_n) is
		variable period   : integer; -- acts as constant for num period to reset
		variable duty		: integer; -- acts as constant for num pulses to reset
		variable dir		: integer;
		variable stepMode	: integer;

		variable numPeriodsToDo: integer; 
		variable numPulsesToDo : integer;
		variable output_coils  : std_logic_vector(5 downto 0) ;
			
		begin
			-- reset case
			if(reset_n = '0') then
				step_readdata  <= (others => '0');
				cycle_readdata <= (others => '0');
				duty_readdata  <= (others => '0');
				dir_readdata   <= (others => '0');
				en_a <= '0';
				en_b <= '0';
					
			-- FPGA rising edge (50MHz) will produce PWM		
			elsif rising_edge(clk) then
				if(step_write_n = '0') then -- check if step has been written to
					numSteps      <= step_writedata;
					step_readdata <= step_writedata;
				end if;
			
				if(cycle_write_n = '0') then -- check if cycle has been written to
					period 			:= to_integer(unsigned(cycle_writedata));
					numPeriodsToDo := period;
					cycle_readdata <= cycle_writedata;	
				end if;
				
				if(duty_write_n = '0') then -- check if duty has been written to
					duty 				:= to_integer(unsigned(duty_writedata));
					numPulsesToDo  := duty;
					duty_readdata  <= duty_writedata;	
				end if;
				
				if(dir_write_n = '0') then -- check if dir has been written to
					dir 				:= to_integer(unsigned(dir_writedata));
					dir_readdata   <= dir_writedata;	
				end if;
				
				if(stepMode_write_n = '0') then -- check if stepMode has been written to
					stepmode 		   := to_integer(unsigned(stepMode_writedata));
					stepMode_readdata <= stepMode_writedata;	
				end if;
				
				-- VHDL Code: to produce a PWM signal
				if(unsigned(numSteps) /= 0) then

						
					-- PWM signal "pulled high", set the step sequence
					if(numPeriodsToDo > 0) and (numPulsesToDo > 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						numPulsesToDo  := numPulsesToDo - 1;
						en_a   <= '1';
						
					-- PWM signal "pulled low", set next step sequence
					elsif(numPeriodsToDo > 0) and (numPulsesToDo = 0) then
						numPeriodsToDo := numPeriodsToDo - 1;						
						en_a   <= '0';
						
					--end of cycle
					elsif(numPeriodsToDo = 0) and (numPulsesToDo = 0) then
						numSteps <= std_logic_vector(unsigned(numSteps) - 1);
						a <= dir_writedata(0);		
						numPeriodsToDo := period;
						numPulsesToDo  := duty;
					end if;
				else 
					en_a <= '0';
					en_b <= '0';
				end if;
			end if;
		end process;
end architecture rtl; -- of L298N_Pwm
