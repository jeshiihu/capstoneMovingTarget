-- Push_Buttons.vhd

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

entity Push_Buttons is
	port (
		clk            : in  std_logic                    := '0';             --            clock.clk
		rst_n          : in  std_logic                    := '0';             --            reset.reset_n
		push_btn_press : in  std_logic_vector(2 downto 0) := (others => '0'); -- conduit_push_btn.export
		btn_read_n     : in  std_logic                    := '0';             --     avalon_slave.read_n
		btn_readdata   : out std_logic_vector(7 downto 0)                     --                 .readdata
	);
end entity Push_Buttons;

architecture rtl of Push_Buttons is
begin

	-- TODO: Auto-generated HDL template

	btn_readdata <= "00000000";

end architecture rtl; -- of Push_Buttons
