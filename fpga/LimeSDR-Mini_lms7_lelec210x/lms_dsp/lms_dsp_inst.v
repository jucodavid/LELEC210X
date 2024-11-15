	lms_dsp u0 (
		.clk_clk                                                   (<connected-to-clk_clk>),                                                   //                                                 clk.clk
		.fifo_in_wdata                                             (<connected-to-fifo_in_wdata>),                                             //                                             fifo_in.wdata
		.fifo_in_wrreq                                             (<connected-to-fifo_in_wrreq>),                                             //                                                    .wrreq
		.fifo_out_wrdata                                           (<connected-to-fifo_out_wrdata>),                                           //                                            fifo_out.wrdata
		.fifo_out_wrreq                                            (<connected-to-fifo_out_wrreq>),                                            //                                                    .wrreq
		.ppd_cfg_passthrough_len                                   (<connected-to-ppd_cfg_passthrough_len>),                                   //                                                 ppd.cfg_passthrough_len
		.ppd_cfg_threshold                                         (<connected-to-ppd_cfg_threshold>),                                         //                                                    .cfg_threshold
		.ppd_cfg_clear_rs                                          (<connected-to-ppd_cfg_clear_rs>),                                          //                                                    .cfg_clear_rs
		.ppd_cfg_enable                                            (<connected-to-ppd_cfg_enable>),                                            //                                                    .cfg_enable
		.ppd_debug_count                                           (<connected-to-ppd_debug_count>),                                           //                                                    .debug_count
		.ppd_debug_long_sum                                        (<connected-to-ppd_debug_long_sum>),                                        //                                                    .debug_long_sum
		.ppd_debug_short_sum                                       (<connected-to-ppd_debug_short_sum>),                                       //                                                    .debug_short_sum
		.reset_reset_n                                             (<connected-to-reset_reset_n>),                                             //                                               reset.reset_n
		.fir_compiler_ii_0_clk_clk                                 (<connected-to-fir_compiler_ii_0_clk_clk>),                                 //                               fir_compiler_ii_0_clk.clk
		.fir_compiler_ii_0_rst_reset_n                             (<connected-to-fir_compiler_ii_0_rst_reset_n>),                             //                               fir_compiler_ii_0_rst.reset_n
		.fir_compiler_ii_0_avalon_streaming_sink_data              (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_data>),              //             fir_compiler_ii_0_avalon_streaming_sink.data
		.fir_compiler_ii_0_avalon_streaming_sink_valid             (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_valid>),             //                                                    .valid
		.fir_compiler_ii_0_avalon_streaming_sink_error             (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_error>),             //                                                    .error
		.fir_compiler_ii_0_avalon_streaming_source_data            (<connected-to-fir_compiler_ii_0_avalon_streaming_source_data>),            //           fir_compiler_ii_0_avalon_streaming_source.data
		.fir_compiler_ii_0_avalon_streaming_source_valid           (<connected-to-fir_compiler_ii_0_avalon_streaming_source_valid>),           //                                                    .valid
		.fir_compiler_ii_0_avalon_streaming_source_error           (<connected-to-fir_compiler_ii_0_avalon_streaming_source_error>),           //                                                    .error
		.packet_presence_detection_0_avalon_streaming_sink_data    (<connected-to-packet_presence_detection_0_avalon_streaming_sink_data>),    //   packet_presence_detection_0_avalon_streaming_sink.data
		.packet_presence_detection_0_avalon_streaming_sink_valid   (<connected-to-packet_presence_detection_0_avalon_streaming_sink_valid>),   //                                                    .valid
		.packet_presence_detection_0_avalon_streaming_source_data  (<connected-to-packet_presence_detection_0_avalon_streaming_source_data>),  // packet_presence_detection_0_avalon_streaming_source.data
		.packet_presence_detection_0_avalon_streaming_source_valid (<connected-to-packet_presence_detection_0_avalon_streaming_source_valid>), //                                                    .valid
		.packet_presence_detection_0_clock_sink_clk                (<connected-to-packet_presence_detection_0_clock_sink_clk>),                //              packet_presence_detection_0_clock_sink.clk
		.packet_presence_detection_0_reset_sink_reset              (<connected-to-packet_presence_detection_0_reset_sink_reset>)               //              packet_presence_detection_0_reset_sink.reset
	);

