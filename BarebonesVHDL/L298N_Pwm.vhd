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
		reset_n         : in  std_logic                     := '0';             --       reset.reset_n
		clk             : in  std_logic                     := '0';             --       clock.clk
		a               : out std_logic;                                        -- conduit_end.a
		b               : out std_logic;                                        --            .b
		a_comp          : out std_logic;                                        --            .a_comp
		b_comp          : out std_logic;                                        --            .b_comp
		en_a            : out std_logic;                                        --            .en_a
		en_b            : out std_logic;                                        --            .en_b
		step_write_n    : in  std_logic                     := '0';             --        step.write_n
		step_writedata  : in  std_logic_vector(15 downto 0) := (others => '0'); --            .writedata
		step_read_n     : in  std_logic                     := '0';             --            .read_n
		step_readdata   : out std_logic_vector(15 downto 0);                    --            .readdata
		cycle_write_n   : in  std_logic                     := '0';             --       cycle.write_n
		cycle_writedata : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		cycle_readdata  : out std_logic_vector(31 downto 0);                    --            .readdata
		cycle_read_n    : in  std_logic                     := '0';             --            .read_n
		duty_write_n    : in  std_logic                     := '0';             --        duty.write_n
		duty_writedata  : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		duty_read_n     : in  std_logic                     := '0';             --            .read_n
		duty_readdata   : out std_logic_vector(31 downto 0);                    --            .readdata
		dir_write_n     : in  std_logic                     := '0';             --         dir.write_n
		dir_writedata   : in  std_logic_vector(7 downto 0)  := (others => '0'); --            .writedata
		dir_read_n      : in  std_logic                     := '0';             --            .read_n
		dir_readdata    : out std_logic_vector(7 downto 0)                      --            .readdata
	);
end entity L298N_Pwm;

architecture rtl of L298N_Pwm is
	procedure get_step (
	signal currentStep : in std_logic_vector(1 downto 0);
	
	-- full step Cw direction, A(Brown) A#(Red) B(Green) B#(White) 
	constant fs_one 	 : std_logic_vector (3 downto 0)   := b"1010";
	constant fs_two 	 : std_logic_vector (3 downto 0)   := b"1001";
	constant fs_three  : std_logic_vector (3 downto 0)   := b"0101";
	constant fs_four 	 : std_logic_vector (3 downto 0)   := b"0110";	
		
	signal four_coils : out std_logic_vector (3 downto 0) 
	)is
	begin	
		case currentStep is -- translate two bits to step sequence
			when b"00" => four_coils <= fs_one;
			when b"01" => four_coils <= fs_two;
			when b"10" => four_coils <= fs_three;
			when b"11" => four_coils <= fs_four;
		end case;
	end get_step;
	
	-- Signals used in the pwm process
	signal currStep 		: std_logic_vector(1 downto 0) := "00";
	signal numSteps 		: std_logic_vector(15 downto 0) := (others => '0');
	signal output_coils  : std_logic_vector(3 downto 0) ;
	
begin
	write_to_hBridge:
	process(clk, reset_n,step_write_n, cycle_write_n) is		
-- 1600Hz or 1600PPS for 0.7kg load (75.68mHm) at FULL STEP 
		variable period   : integer; -- acts like constant for num period to reset
		variable duty		: integer; -- acts like constant for num pulses to reset
		variable dir		: integer;

		variable numPeriodsToDo: integer; 
		variable numPulsesToDo : integer;
			
		begin
			if(reset_n = '0') then
				step_readdata  <= (others => '0');
				cycle_readdata <= (others => '0');
				duty_readdata  <= (others => '0');
				dir_readdata   <= (others => '0');
				en_a <= '0';
				en_b <= '0';			
			elsif rising_edge(clk) then
				if(step_write_n = '0') then -- check if step has been written to
					numSteps <= step_writedata;
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
				
				if(unsigned(numSteps) /= 0) then
					-- PWM signal pulled high
					if(numPeriodsToDo > 0) and (numPulsesToDo > 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						numPulsesToDo  := numPulsesToDo - 1;
						
						get_step(currStep, four_coils => output_coils ); 
						a 		 <= output_coils(3);
						a_comp <= output_coils(2);
						b 		 <= output_coils(1);
						b_comp <= output_coils(0);
						en_a   <= '1';
						en_b   <= '1';
					-- PWM signal pulled low
					elsif(numPeriodsToDo > 0) and (numPulsesToDo = 0) then
						numPeriodsToDo := numPeriodsToDo - 1;
						
						get_step(currStep, four_coils => output_coils );
						a 		 <= output_coils(3);
						a_comp <= output_coils(2);
						b 		 <= output_coils(1);
						b_comp <= output_coils(0);
						en_a   <= '0';
						en_b   <= '0';
					--end of cycle
					elsif(numPeriodsToDo = 0) and (numPulsesToDo = 0) then
						numSteps <= std_logic_vector(unsigned(numSteps) - 1);
						
						if(dir = 0) then
							currStep <= std_logic_vector(unsigned(currStep) + 1);
						else
							currStep <= std_logic_vector(unsigned(currStep) - 1);
						end if;
							
						numPeriodsToDo := period;
						numPulsesToDo  := duty;
					else 
						en_a <= '0';
						en_b <= '0';
					end if;
				end if;
			end if;
		end process;
end architecture rtl; -- of L298N_Pwm
