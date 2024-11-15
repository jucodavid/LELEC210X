	component lms_dsp is
		port (
			clk_clk                                                   : in  std_logic                     := 'X';             -- clk
			fifo_in_wdata                                             : in  std_logic_vector(47 downto 0) := (others => 'X'); -- wdata
			fifo_in_wrreq                                             : in  std_logic                     := 'X';             -- wrreq
			fifo_out_wrdata                                           : out std_logic_vector(47 downto 0);                    -- wrdata
			fifo_out_wrreq                                            : out std_logic;                                        -- wrreq
			ppd_cfg_passthrough_len                                   : in  std_logic_vector(15 downto 0) := (others => 'X'); -- cfg_passthrough_len
			ppd_cfg_threshold                                         : in  std_logic_vector(7 downto 0)  := (others => 'X'); -- cfg_threshold
			ppd_cfg_clear_rs                                          : in  std_logic                     := 'X';             -- cfg_clear_rs
			ppd_cfg_enable                                            : in  std_logic                     := 'X';             -- cfg_enable
			ppd_debug_count                                           : out std_logic_vector(31 downto 0);                    -- debug_count
			ppd_debug_long_sum                                        : out std_logic_vector(31 downto 0);                    -- debug_long_sum
			ppd_debug_short_sum                                       : out std_logic_vector(31 downto 0);                    -- debug_short_sum
			reset_reset_n                                             : in  std_logic                     := 'X';             -- reset_n
			fir_compiler_ii_0_clk_clk                                 : in  std_logic                     := 'X';             -- clk
			fir_compiler_ii_0_rst_reset_n                             : in  std_logic                     := 'X';             -- reset_n
			fir_compiler_ii_0_avalon_streaming_sink_data              : in  std_logic_vector(23 downto 0) := (others => 'X'); -- data
			fir_compiler_ii_0_avalon_streaming_sink_valid             : in  std_logic                     := 'X';             -- valid
			fir_compiler_ii_0_avalon_streaming_sink_error             : in  std_logic_vector(1 downto 0)  := (others => 'X'); -- error
			fir_compiler_ii_0_avalon_streaming_source_data            : out std_logic_vector(23 downto 0);                    -- data
			fir_compiler_ii_0_avalon_streaming_source_valid           : out std_logic;                                        -- valid
			fir_compiler_ii_0_avalon_streaming_source_error           : out std_logic_vector(1 downto 0);                     -- error
			packet_presence_detection_0_avalon_streaming_sink_data    : in  std_logic_vector(23 downto 0) := (others => 'X'); -- data
			packet_presence_detection_0_avalon_streaming_sink_valid   : in  std_logic                     := 'X';             -- valid
			packet_presence_detection_0_avalon_streaming_source_data  : out std_logic_vector(23 downto 0);                    -- data
			packet_presence_detection_0_avalon_streaming_source_valid : out std_logic;                                        -- valid
			packet_presence_detection_0_clock_sink_clk                : in  std_logic                     := 'X';             -- clk
			packet_presence_detection_0_reset_sink_reset              : in  std_logic                     := 'X'              -- reset
		);
	end component lms_dsp;

	u0 : component lms_dsp
		port map (
			clk_clk                                                   => CONNECTED_TO_clk_clk,                                                   --                                                 clk.clk
			fifo_in_wdata                                             => CONNECTED_TO_fifo_in_wdata,                                             --                                             fifo_in.wdata
			fifo_in_wrreq                                             => CONNECTED_TO_fifo_in_wrreq,                                             --                                                    .wrreq
			fifo_out_wrdata                                           => CONNECTED_TO_fifo_out_wrdata,                                           --                                            fifo_out.wrdata
			fifo_out_wrreq                                            => CONNECTED_TO_fifo_out_wrreq,                                            --                                                    .wrreq
			ppd_cfg_passthrough_len                                   => CONNECTED_TO_ppd_cfg_passthrough_len,                                   --                                                 ppd.cfg_passthrough_len
			ppd_cfg_threshold                                         => CONNECTED_TO_ppd_cfg_threshold,                                         --                                                    .cfg_threshold
			ppd_cfg_clear_rs                                          => CONNECTED_TO_ppd_cfg_clear_rs,                                          --                                                    .cfg_clear_rs
			ppd_cfg_enable                                            => CONNECTED_TO_ppd_cfg_enable,                                            --                                                    .cfg_enable
			ppd_debug_count                                           => CONNECTED_TO_ppd_debug_count,                                           --                                                    .debug_count
			ppd_debug_long_sum                                        => CONNECTED_TO_ppd_debug_long_sum,                                        --                                                    .debug_long_sum
			ppd_debug_short_sum                                       => CONNECTED_TO_ppd_debug_short_sum,                                       --                                                    .debug_short_sum
			reset_reset_n                                             => CONNECTED_TO_reset_reset_n,                                             --                                               reset.reset_n
			fir_compiler_ii_0_clk_clk                                 => CONNECTED_TO_fir_compiler_ii_0_clk_clk,                                 --                               fir_compiler_ii_0_clk.clk
			fir_compiler_ii_0_rst_reset_n                             => CONNECTED_TO_fir_compiler_ii_0_rst_reset_n,                             --                               fir_compiler_ii_0_rst.reset_n
			fir_compiler_ii_0_avalon_streaming_sink_data              => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_sink_data,              --             fir_compiler_ii_0_avalon_streaming_sink.data
			fir_compiler_ii_0_avalon_streaming_sink_valid             => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_sink_valid,             --                                                    .valid
			fir_compiler_ii_0_avalon_streaming_sink_error             => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_sink_error,             --                                                    .error
			fir_compiler_ii_0_avalon_streaming_source_data            => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_source_data,            --           fir_compiler_ii_0_avalon_streaming_source.data
			fir_compiler_ii_0_avalon_streaming_source_valid           => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_source_valid,           --                                                    .valid
			fir_compiler_ii_0_avalon_streaming_source_error           => CONNECTED_TO_fir_compiler_ii_0_avalon_streaming_source_error,           --                                                    .error
			packet_presence_detection_0_avalon_streaming_sink_data    => CONNECTED_TO_packet_presence_detection_0_avalon_streaming_sink_data,    --   packet_presence_detection_0_avalon_streaming_sink.data
			packet_presence_detection_0_avalon_streaming_sink_valid   => CONNECTED_TO_packet_presence_detection_0_avalon_streaming_sink_valid,   --                                                    .valid
			packet_presence_detection_0_avalon_streaming_source_data  => CONNECTED_TO_packet_presence_detection_0_avalon_streaming_source_data,  -- packet_presence_detection_0_avalon_streaming_source.data
			packet_presence_detection_0_avalon_streaming_source_valid => CONNECTED_TO_packet_presence_detection_0_avalon_streaming_source_valid, --                                                    .valid
			packet_presence_detection_0_clock_sink_clk                => CONNECTED_TO_packet_presence_detection_0_clock_sink_clk,                --              packet_presence_detection_0_clock_sink.clk
			packet_presence_detection_0_reset_sink_reset              => CONNECTED_TO_packet_presence_detection_0_reset_sink_reset               --              packet_presence_detection_0_reset_sink.reset
		);

