-- pwm.vhd

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

entity pwm is
	port (
		step            : out std_logic;                                        --            conduit.step
		clk             : in  std_logic                     := '0';             --                clk.clk
		reset           : in  std_logic                     := '0';             --              reset.reset
		cycle_n         : in  std_logic                     := '0';             -- avalon_slave_cycle.write_n
		cycle_writedata : in  std_logic_vector(31 downto 0) := (others => '0'); --                   .writedata
		duty_n          : in  std_logic                     := '0';             --  avalon_slave_duty.write_n
		duty_writedata  : in  std_logic_vector(31 downto 0) := (others => '0'); --                   .writedata
		step_n          : in  std_logic                     := '0';             --  avalon_slave_step.write_n
		step_writedata  : in  std_logic_vector(31 downto 0) := (others => '0')  --                   .writedata
	);
end entity pwm;

architecture rtl of pwm is
signal stepsToDo : std_logic_vector(31 downto 0);

begin
	process(clk, reset, step_n, cycle_n, duty_n) is
		variable period : integer;
		variable highDuty : integer;

		variable numPeriodsToDo: integer; 
		variable numPulsesToDo: integer; -- 90% duty cycle
		begin
		-- TODO: Auto-generated HDL template
		if(reset = '1') then
			step <= '0';
		elsif rising_edge(clk) then
			if(step_n = '0') then
				stepsToDo <= step_writedata;
			end if;
			if(cycle_n = '0') then
				period := to_integer(unsigned(cycle_writedata));
				numPeriodsToDo := period;
			end if;
			if(step_n = '0') then
				highDuty := to_integer(unsigned(duty_writedata));
				numPulsesToDo := highDuty;
			end if;
			
			if(stepsToDo /= "00000000000000000000000000000000") then
			-- pull high
				if(numPeriodsToDo > 0) and (numPulsesToDo > 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						numPulsesToDo  := numPulsesToDo - 1;
						step <= '1';
						
					-- PWM signal pulled low
					elsif(numPeriodsToDo > 0) and (numPulsesToDo = 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						step <= '0';
						
					--end of cycle
					elsif(numPeriodsToDo = 0) and (numPulsesToDo = 0) then
						stepsToDo <= std_logic_vector(unsigned(stepsToDo) - 1);
							
						numPeriodsToDo := period;
						numPulsesToDo  := highDuty;
					end if;
			end if;
		end if;
	end process;
end architecture rtl; -- of pwm
