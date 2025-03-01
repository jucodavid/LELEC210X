/*
 * config.h
 */

#ifndef INC_CONFIG_H_
#define INC_CONFIG_H_

#include <stdio.h>

// Runtime parameters
#define MAIN_APP 0
#define EVAL_RADIO 1

//#define RUN_CONFIG EVAL_RADIO
#define RUN_CONFIG MAIN_APP

// Radio parameters
#define ENABLE_RADIO 1

// General UART enable/disable (disable for low-power operation)
#define ENABLE_UART 0

// Enable performance measurements
#define PERF_COUNT 0

// Enable debug print
#define DEBUGP 0

// In continuous mode, we start and stop continuous acquisition on button press.
// In non-continuous mode, we send a single packet on button press.
#define CONTINUOUS_ACQ 1

// Event detection enable/disable
#define EVENT_DETECTION 1

// Event detection modes
#define HARD_THRESHOLD 0
#define SOFT_THRESHOLD 1
#define HW_HARD_THRESHOLD 2

// Event detection mode selection
#define EVENT_DETECTION_MODE HARD_THRESHOLD
//#define EVENT_DETECTION_MODE SOFT_THRESHOLD

// Event detection parameters
// 	  Hard threshold mode
//        Hard threshold modes
#define HT_MEAN 0
#define HT_MAX 1
#define HT_POWER 2

#define THRESHOLD 2500 // Mean : 2040; MAX : 2500; ENERGY :
//#define HT_METRIC HT_MEAN
#define HT_METRIC HT_MAX
//#define HT_METRIC HT_POWER

// 	  Soft threashold mode


//    Harware Hard threshold mode


// Spectrogram parameters
#define SAMPLES_PER_MELVEC 512
#define MELVEC_LENGTH 20
#define N_MELVECS 20


#if (DEBUGP == 1)
#define DEBUG_PRINT(...) do{ printf(__VA_ARGS__ ); } while( 0 )
#else
#define DEBUG_PRINT(...) do{ } while ( 0 )
#endif



#endif /* INC_CONFIG_H_ */
