-- new_component.vhd

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

entity new_component is
	port (
		en_a      : out std_logic;                                        --  conduit_end.en_a
		en_b      : out std_logic;                                        --             .en_b
		a         : out std_logic;                                        --             .a
		b         : out std_logic;                                        --             .b
		a_comp    : out std_logic;                                        --             .a_comp
		b_comp    : out std_logic;                                        --             .b_comp
		write_n   : in  std_logic                     := '0';             -- avalon_slave.write_n
		writedata : in  std_logic_vector(31 downto 0) := (others => '0'); --             .writedata
		read_n    : in  std_logic                     := '0';             --             .read_n
		readdata  : out std_logic_vector(31 downto 0);                    --             .readdata
		reset_n   : in  std_logic                     := '0';             --        reset.reset_n
		clk       : in  std_logic                     := '0'              --        clock.clk
	);
end entity new_component;

architecture rtl of new_component is
	-- CW Rotation
	variable step1: integer := 58;
	variable step2: integer := 57;
	variable step3: integer := 53;
	variable step4: integer := 54;
	
	variable numPeriodsToDo: integer := 1000000;
	variable numPulsesToDo: integer:= 75000;
	
	signal currPwmState: std_logic := '0';
			
begin
	write_to_hBridge:
		process(clk, reset_n,write_n) is

		begin
			if(reset_n = '0') then
				readdata <= "00000000000000000000000000000000";
				en_a <= '0';
				en_b <= '0';
			
			elseif rising_edge(clk) then
				-- current pwm signal is low (off)
				if(currPwmState = '0' then
					if(numPulsesToDo = 0) then
						numPulsesToDo := 75000;
						currPwmState <= '1';
					elseif(numPulsesToDo > 0) then
					
					end if;
					
				-- current pwm signal is high (on)
				elseif(pwmState = '1') then
				end if;
--			elsif(write_n = '0') then
--				readdata <= writedata(31 downto 0);
--				en_a <= writedata(5);
--				en_b <= writedata(4);
--				
--				a <= writedata(3);
--				a_comp <= writedata(2);
--				
--				b <= writedata(1);
--				b_comp <= writedata(0);
			end if;
				
		end process;
	-- TODO: Auto-generated HDL template

end architecture rtl; -- of new_component
