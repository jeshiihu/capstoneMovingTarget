-- Easy_Driver.vhd

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

entity Easy_Driver is
	port (
		clk                : in  std_logic                     := '0';             --               clock.clk
		reset_n            : in  std_logic                     := '0';             --               reset.reset_n
		conduit_end_dir    : out std_logic;                                        --         conduit_end.dir
		conduit_end_step   : out std_logic;                                        --                    .step
		conduit_end_enable : out std_logic;                                        --                    .enable
		step_read_n        : in  std_logic                     := '0';             --   avalon_slave_step.read_n
		step_readdata      : out std_logic_vector(15 downto 0);                    --                    .readdata
		step_write_n       : in  std_logic                     := '0';             --                    .write_n
		step_writedata     : in  std_logic_vector(15 downto 0) := (others => '0'); --                    .writedata
		dir_read_n         : in  std_logic                     := '0';             --    avalon_slave_dir.read_n
		dir_readdata       : out std_logic_vector(7 downto 0);                     --                    .readdata
		dir_write_n        : in  std_logic                     := '0';             --                    .write_n
		dir_writedata      : in  std_logic_vector(7 downto 0)  := (others => '0'); --                    .writedata
		period_read_n      : in  std_logic                     := '0';             -- avalon_slave_period.read_n
		period_readdata    : out std_logic_vector(31 downto 0);                    --                    .readdata
		period_write_n     : in  std_logic                     := '0';             --                    .write_n
		period_writedata   : in  std_logic_vector(31 downto 0) := (others => '0'); --                    .writedata
		duty_read_n        : in  std_logic                     := '0';             --   avalon_slave_duty.read_n
		duty_readdata      : out std_logic_vector(31 downto 0);                    --                    .readdata
		duty_write_n       : in  std_logic                     := '0';             --                    .write_n
		duty_writedata     : in  std_logic_vector(31 downto 0) := (others => '0')  --                    .writedata
	);
end entity Easy_Driver;

architecture rtl of Easy_Driver is
-- Signals used in the pwm process
signal numSteps 		: std_logic_vector(15 downto 0) := (others => '0'); -- step counter

-- Process that produces the step sequence from a PWM
-- by set frequency and duty cycle	
begin
	write_to_easy_driver:
	process(clk, reset_n) is
		variable period   : integer; -- acts as constant for num period to reset
		variable duty		: integer; -- acts as constant for num pulses to reset

		variable numPeriodsToDo: integer; 
		variable numPulsesToDo : integer;
			
		begin
			-- reset case
			if(reset_n = '0') then
				step_readdata   <= (others => '0');
				period_readdata <= (others => '0');
				duty_readdata   <= (others => '0');
				dir_readdata    <= (others => '0');
				conduit_end_dir    <= '0';
				conduit_end_step   <= '0';
				conduit_end_enable <= '0';
					
			-- FPGA rising edge (50MHz) will produce PWM		
			elsif rising_edge(clk) then
				if(step_write_n = '0') then -- check if step has been written to
					numSteps      <= step_writedata;
					step_readdata <= step_writedata;
				end if;
			
				if(period_write_n = '0') then -- check if cycle has been written to
					period 			:= to_integer(unsigned(period_writedata));
					numPeriodsToDo := period;
					period_readdata <= period_writedata;	
				end if;
				
				if(duty_write_n = '0') then -- check if duty has been written to
					duty 				:= to_integer(unsigned(duty_writedata));
					numPulsesToDo  := duty;
					duty_readdata  <= duty_writedata;	
				end if;
				
				if(dir_write_n = '0') then -- check if dir has been written to
					conduit_end_dir <= dir_writedata(0);
					dir_readdata    <= dir_writedata;	
				end if;
				
				-- VHDL Code: to produce a PWM signal
				if(unsigned(numSteps) /= 0) then
					conduit_end_enable <= '1';
						
					-- PWM signal "pulled high", set the step sequence
					if(numPeriodsToDo > 0) and (numPulsesToDo > 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						numPulsesToDo  := numPulsesToDo - 1;
						conduit_end_step <= '1';
						
					-- PWM signal "pulled low", set next step sequence
					elsif(numPeriodsToDo > 0) and (numPulsesToDo = 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						conduit_end_step <= '0';
						
					--end of cycle
					elsif(numPeriodsToDo = 0) and (numPulsesToDo = 0) then
						numSteps <= std_logic_vector(unsigned(numSteps) - 1);
						numPeriodsToDo := period;
						numPulsesToDo  := duty;
					end if;
				else 
					conduit_end_step   <= '0';
					conduit_end_enable <= '0';
				end if;
			end if;
		end process;
end architecture rtl; -- of Easy_Driver
