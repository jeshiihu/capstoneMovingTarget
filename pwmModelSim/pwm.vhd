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
	-- get_step function will iterate through the step sequence
	-- This is for full step A, A#, B, B# 
	procedure getFullStep (
		signal currentStep : in std_logic_vector(2 downto 0);

		constant fs_one 	 : std_logic_vector (5 downto 0)   := "111010";
		constant fs_two 	 : std_logic_vector (5 downto 0)   := "111001";
		constant fs_three  : std_logic_vector (5 downto 0)   := "110101";
		constant fs_four 	 : std_logic_vector (5 downto 0)   := "110110";	
			
		variable four_coils : out std_logic_vector (5 downto 0) 
	)is
	begin	
		case currentStep is -- translate two bits to step sequence
			when "000" => four_coils := fs_one;
			when "001" => four_coils := fs_two;
			when "010" => four_coils := fs_three;
			when "011" => four_coils := fs_four;
			when others  => four_coils := "000000";
		end case;
	end getFullStep;
	
		-- get_step function will iterate through the step sequence
	-- This is for half step A, A#, B, B# 
	procedure getHalfStep (
		signal currentStep : in std_logic_vector(2 downto 0);

		constant hs_one 	 : std_logic_vector (5 downto 0)   := "111010";
		constant hs_two 	 : std_logic_vector (5 downto 0)   := "101011";
		constant hs_three  : std_logic_vector (5 downto 0)   := "111001";
		constant hs_four 	 : std_logic_vector (5 downto 0)   := "011101";
		constant hs_five 	 : std_logic_vector (5 downto 0)   := "110101";
		constant hs_six 	 : std_logic_vector (5 downto 0)   := "100111";
		constant hs_seven  : std_logic_vector (5 downto 0)   := "110110";
		constant hs_eight  : std_logic_vector (5 downto 0)   := "011110";		
			
		variable four_coils : out std_logic_vector (5 downto 0) 
	)is
	begin	
		case currentStep is -- translate two bits to step sequence
			when b"000" => four_coils := hs_one;
			when b"001" => four_coils := hs_two;
			when b"010" => four_coils := hs_three;
			when b"011" => four_coils := hs_four;
			when b"100" => four_coils := hs_five;
			when b"101" => four_coils := hs_six;
			when b"110" => four_coils := hs_seven;
			when b"111" => four_coils := hs_eight;
			when others  => four_coils := "000000";
		end case;
	end getHalfStep;
	
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
						
						if(stepMode = 0) then
							getFullStep(currStep, four_coils => output_coils );
						else
							getHalfStep(currStep, four_coils => output_coils );
						end if;
					
						en_a   <= output_coils(5);
						en_b   <= output_coils(4);
						a 		 <= output_coils(3);
						a_comp <= output_coils(2);
						b 		 <= output_coils(1);
						b_comp <= output_coils(0);
					-- PWM signal "pulled low", set next step sequence
					elsif(numPeriodsToDo > 0) and (numPulsesToDo = 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						
						if(stepMode = 0) then
							getFullStep(currStep, four_coils => output_coils );
						else
							getHalfStep(currStep, four_coils => output_coils );
						end if;
						
						en_a   <= output_coils(5);
						en_b   <= output_coils(4);
						a 		 <= output_coils(3);
						a_comp <= output_coils(2);
						b 		 <= output_coils(1);
						b_comp <= output_coils(0);
					--end of cycle
					elsif(numPeriodsToDo = 0) and (numPulsesToDo = 0) then
						numSteps <= std_logic_vector(unsigned(numSteps) - 1);
						
						if(dir = 0) then
							if(stepMode = 0) and (currStep = "011") then
								currStep <= "000";
							else
								currStep <= std_logic_vector(unsigned(currStep) + 1);
							end if;
						else
							if(stepMode = 0) and (currStep = "000") then
								currStep <= "011";
							else
								currStep <= std_logic_vector(unsigned(currStep) - 1);
							end if;
						end if;
							
						numPeriodsToDo := period;
						numPulsesToDo  := duty;
					end if;
				end if;
			end if;
		end process;
end architecture rtl; -- of L298N_Pwm
