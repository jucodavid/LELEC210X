/*
 * spectrogram.c
 *
 *  Created on: Oct 7, 2021
 *      Author: Teaching Assistants of LELEC210x
 */

#include "spectrogram.h"
#include "spectrogram_tables.h"
#include "config.h"
#include "arm_math.h"
#include "arm_absmax_q15.h"

extern void start_cycle_count();
extern void stop_cycle_count(char *s);

q15_t buf    [  SAMPLES_PER_MELVEC  ]; // Windowed samples
q15_t buf_fft[2*SAMPLES_PER_MELVEC  ]; // Double size (real|imag) buffer for arm_rfft_q15
q15_t buf_tmp[  SAMPLES_PER_MELVEC/2]; // Intermediate buffer for arm_mat_mult_fast_q15

// Convert 12-bit DC ADC samples to Q1.15 fixed point signal and remove DC component
void Spectrogram_Format(q15_t *buf)
{
	// STEP 0.1 : Increase fixed-point scale
	//            --> Pointwise shift
	//            Complexity: O(SAMPLES_PER_MELVEC)
	//            Number of cycles: 3661

	// The output of the ADC is stored in an unsigned 12-bit format, so buf[i] is in [0 , 2**12 - 1]
	// In order to better use the scale of the signed 16-bit format (1 bit of sign and 15 integer bits), we can multiply by 2**(15-12) = 2**3
	// That way, the value of buf[i] is in [0 , 2**15 - 1]

	// /!\ When multiplying/dividing by a power 2, always prefer shifting left/right instead, ARM instructions to do so are more efficient.
	// Here we should shift left by 3.

//	start_cycle_count();
	arm_shift_q15(buf, 3, buf, SAMPLES_PER_MELVEC);
//	stop_cycle_count("Step_0.1");

	// STEP 0.2 : Remove DC Component
	//            --> Pointwise substract
	//            Complexity: O(SAMPLES_PER_MELVEC)
	//            Number of cycles: 15911

	// Since we use a signed representation, we should now center the value around zero, we can do this by substracting 2**14.
	// Now the value of buf[i] is in [-2**14 , 2**14 - 1]

	// [?] Why don't we use the full scale of the 16-bit?
	// Are we done computing things with this array ?
	// What would happen if we used the full scale and do, for example, a multiplication between two values?

//	start_cycle_count();
	const uint16_t DC_VALUE = 1u << 14;
	for(uint16_t i=0; i < SAMPLES_PER_MELVEC; i++)
	{
		// Remove DC component
		buf[i] -= DC_VALUE;
	}
//	stop_cycle_count("Step_0.2");
}

void optimizedMatrixMultiplication(int a, int b, int c,
                                   int matrix[a][b], int dense[b][c], int result[a][c]) {
    int start_index[a], length[a];

    // Trouver les indices de début et la longueur de la plage non-nulle pour chaque ligne
    for (int i = 0; i < a; i++) {
        start_index[i] = -1;  // Indicateur pour le début de la plage
        length[i] = 0;

        for (int j = 0; j < b; j++) {
            if (matrix[i][j] != 0) {
                if (start_index[i] == -1) start_index[i] = j; // Premier élément non nul
                length[i]++;
            } else if (start_index[i] != -1) {
                // Une fois qu'on a commencé la plage, on s'arrête dès qu'on retrouve un zéro
                break;
            }
        }
    }

    // Multiplication optimisée en ignorant les zéros
    for (int i = 0; i < a; i++) {
        if (length[i] == 0) continue; // Ligne entièrement nulle, inutile de la traiter

        int start = start_index[i];
        int end = start + length[i];

        for (int j = 0; j < c; j++) {
            for (int k = start; k < end; k++) {
                result[i][j] += matrix[i][k] * dense[k][j];
            }
        }
    }
}


#include "arm_math.h" // CMSIS-DSP

void optimizedMatrixMultiplication(int a, int b, int c,
	arm_matrix_instance_q15 matrix[a][b], arm_matrix_instance_q15 dense[b][c], arm_matrix_instance_q15 result[a][c]) {
    int start_index[a], length[a];
    start_index[-1] = 0;
    length[-1] = 0;

    // Trouver les indices de début et la longueur de la plage non-nulle pour chaque ligne
    for (int i = 0; i < a; i++) {
        start_index[i] = -1;  // Indicateur pour le début de la plage
        length[i] = length[i-1];

        for (int j = start_index[i-1]; j < b; j++) {
            if (matrix[i][j] != 0) {
                if (start_index[i] == -1) start_index[i] = j; // Premier élément non nul
            break;
        }
    }   while (matrix[i][start_index[i]+length[i]] != 0){
            length[i]++;
        }
    }
    for (int j = 0; j < 4; j++) {
            printf("%d ", start_index[j]);
        }
    printf("\n");
    for (int j = 0; j < 4; j++) {
        printf("%d ", length[j]);
    }
    printf("\n");

    for (int i = 0; i < a; ++i) {
      for (int j = 0; j < c; ++j) {
         result[i][j] = 0;
      }
   }

    // Multiplication optimisée en ignorant les zéros
    for (int i = 0; i < a; i++) {
        if (length[i] == 0) continue; // Ligne entièrement nulle, inutile de la traiter

        int start = start_index[i];
        int end = start + length[i];

        for (int j = 0; j < c; j++) {
            for (int k = start; k < end; k++) {
                result[i][j] += matrix[i][k] * dense[k][j];
            }
        }
    }
}

arm_status optimized_mat_mult_q15(
    const arm_matrix_instance_q15 * pSrcA,
    const arm_matrix_instance_q15 * pSrcB,
    arm_matrix_instance_q15 * pDst)
{
    // Dimensions
    uint16_t numRowsA = pSrcA->numRows;
    uint16_t numColsA = pSrcA->numCols;
    uint16_t numColsB = pSrcB->numCols;

    // Pointeurs des données
    q15_t *pA = pSrcA->pData;
    q15_t *pB = pSrcB->pData;
    q15_t *pC = pDst->pData;

    // Multiplication optimisée
    for (uint16_t i = 0; i < numRowsA; i++) {
        uint16_t start = 0, length = 0;
        q15_t *rowA = &pA[i * numColsA];

        // Trouver la plage non nulle dans la ligne i
        while (start < numColsA && rowA[start] == 0) start++;  // Début
        length = numColsA - start;
        while (length > 0 && rowA[start + length - 1] == 0) length--;  // Fin

        if (length == 0) continue; // Si toute la ligne est nulle, passer

        // Effectuer le produit ligne × matrice colonne
        for (uint16_t j = 0; j < numColsB; j++) {
            q31_t sum = 0;  // Somme sur 32 bits pour éviter l’overflow
            for (uint16_t k = 0; k < length; k++) {
                sum += (q31_t) rowA[start + k] * pB[(start + k) * numColsB + j];
            }
            pC[i * numColsB + j] = (q15_t) __SSAT((sum >> 15), 16); // Saturation Q15
        }
    }

    return ARM_MATH_SUCCESS;
}

// Compute spectrogram of samples and transform into MEL vectors.
void Spectrogram_Compute(q15_t *samples, q15_t *melvec)
{
	// STEP 1  : Windowing of input samples
	//           --> Pointwise product
	//           Complexity: O(SAMPLES_PER_MELVEC)
	//           Number of cycles: 3923
	//	start_cycle_count();
	arm_mult_q15(samples, hamming_window, buf, SAMPLES_PER_MELVEC);
//	stop_cycle_count("Step_1");

	// STEP 2  : Discrete Fourier Transform
	//           --> In-place Fast Fourier Transform (FFT) on a real signal
	//           --> For our spectrogram, we only keep only positive frequencies (symmetry) in the next operations.
	//           Complexity: O(SAMPLES_PER_MELVEC log_2 SAMPLES_PER_MELVEC)
	//           Number of cycles: 23164

	// Since the FFT is a recursive algorithm, the values are rescaled in the function to ensure that overflow cannot happen.
	//	start_cycle_count();
	arm_rfft_instance_q15 rfft_inst;

	arm_rfft_init_q15(&rfft_inst, SAMPLES_PER_MELVEC, 0, 1);

	arm_rfft_q15(&rfft_inst, buf, buf_fft);
//	stop_cycle_count("Step_2");

	// STEP 3  : Compute the complex magnitude of the FFT
	//           Because the FFT can output a great proportion of very small values,
	//           we should rescale all values by their maximum to avoid loss of precision when computing the complex magnitude
	//           In this implementation, we use integer division and multiplication to rescale values, which are very costly.
	//           [?] Is there a more efficient way to this using only shifting ?

	// STEP 3.1: Find the extremum value (maximum of absolute values)
	//           Complexity: O(SAMPLES_PER_MELVEC)
	//           Number of cycles: 17494

	//	start_cycle_count();
	q15_t vmax;
	uint32_t pIndex=0;

	arm_absmax_q15(buf_fft, SAMPLES_PER_MELVEC, &vmax, &pIndex);
//	stop_cycle_count("Step_3.1");

	// STEP 3.2: Normalize the vector
	//           Complexity: O(SAMPLES_PER_MELVEC)
	//           Number of cycles: 15416

	//	start_cycle_count();
	for (int i=0; i < SAMPLES_PER_MELVEC; i++)
	{
		buf[i] = (q15_t) (((q31_t) buf_fft[i] << 15) / ((q31_t) vmax));
	}
//	stop_cycle_count("Step_3.2");

	// STEP 3.3: Compute the complex magnitude
	//           --> The output buffer is now two times smaller because (real|imag) --> (mag)
	//           Complexity: O(SAMPLES_PER_MELVEC)
	//           Number of cycles: 4798

	//	start_cycle_count();
	arm_cmplx_mag_q15(buf, buf, SAMPLES_PER_MELVEC / 2);
//	stop_cycle_count("Step_3.3");

	// STEP 3.4: Denormalize the vector
	//           Complexity: O(SAMPLES_PER_MELVEC)
	//           Number of cycles: 6439

	//	start_cycle_count();
	for (int i=0; i < SAMPLES_PER_MELVEC / 2; i++)
	{
		buf[i] = (q15_t) ((((q31_t) buf[i]) * ((q31_t) vmax) ) >> 15 );
	}
//	stop_cycle_count("Step_3.4");

	// STEP 4:   Apply MEL transform
	//           --> Fast Matrix Multiplication
	//           Complexity: O(SAMPLES_PER_MELVEC * MELVEC_LENGTH)
	//           Number of cycles: 20891

	// /!\ The difference between the function arm_mat_mult_q15() and the fast variant is that the fast variant use a 32-bit rather than a 64-bit accumulator.
	// The result of each 1.15 x 1.15 multiplication is truncated to 2.30 format. These intermediate results are accumulated in a 32-bit register in 2.30 format.
	// Finally, the accumulator is saturated and converted to a 1.15 result. The fast version has the same overflow behavior as the standard version but provides
	// less precision since it discards the low 16 bits of each multiplication result.

	// /!\ In order to avoid overflows completely the input signals should be scaled down. Scale down one of the input matrices by log2(numColsA) bits to avoid overflows,
	// as a total of numColsA additions are computed internally for each output element. Because our hz2mel_mat matrix contains lots of zeros in its rows, this is not necessary.


	arm_matrix_instance_q15 hz2mel_inst, fftmag_inst, melvec_inst;

	arm_mat_init_q15(&hz2mel_inst, MELVEC_LENGTH,          SAMPLES_PER_MELVEC / 2, hz2mel_mat);
	arm_mat_init_q15(&fftmag_inst, SAMPLES_PER_MELVEC / 2, 1,                      buf);
	arm_mat_init_q15(&melvec_inst, MELVEC_LENGTH,          1,                      melvec);
	start_cycle_count();
	arm_mat_mult_fast_q15(&hz2mel_inst, &fftmag_inst, &melvec_inst, buf_tmp);
	stop_cycle_count("Step_4");
	start_cycle_count();
	optimizedMatrixMultiplication(MELVEC_LENGTH, SAMPLES_PER_MELVEC / 2, 1, hz2mel_mat, buf, melvec)
	stop_cycle_count("Step_5");
}

