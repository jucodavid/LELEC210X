/*
 * packet.c
 */

#include "aes_ref.h"
#include "config.h"
#include "packet.h"
#include "main.h"
#include "utils.h"

const uint8_t AES_Key[16]  = {
                            0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00};

void tag_cbc_mac(uint8_t *tag, const uint8_t *msg, size_t msg_len) {
	// Allocate a buffer of the key size to store the input and result of AES
	// uint32_t[4] is 4*(32/8)= 16 bytes long
	uint32_t statew[4] = {0};
	// state is a pointer to the start of the buffer
	uint8_t *state = (uint8_t*) statew;
    size_t i;


    // TO DO : Complete the CBC-MAC_AES
	// Parse msg into blocks of 16 bytes
	size_t num_blocks = (msg_len + 15) / 16;
	uint8_t block[16];

	// Initialize state to 0
	memset(state, 0, 16);

	for (i = 0; i < num_blocks; i++) {
		// Copy the current block into the block buffer
		size_t block_len = (i == num_blocks - 1) ? (msg_len % 16) : 16;
		memcpy(block, msg + i * 16, block_len);

		// If the last block is not 16 bytes, pad with zeros
		if (block_len < 16) {
			memset(block + block_len, 0, 16 - block_len);
		}

		// XOR the block with the current state
		for (size_t j = 0; j < 16; j++) {
			state[j] ^= block[j];
		}

		// Encrypt the state with AES
		AES128_encrypt(state, AES_Key);
	}

    // Copy the result of CBC-MAC-AES to the tag.
    for (int j=0; j<16; j++) {
        tag[j] = state[j];
    }
}

// Assumes payload is already in place in the packet
int make_packet(uint8_t *packet, size_t payload_len, uint8_t sender_id, uint32_t serial) {
    size_t packet_len = payload_len + PACKET_HEADER_LENGTH + PACKET_TAG_LENGTH;
    // Initially, the whole packet header is set to 0s
    memset(packet, 0, PACKET_HEADER_LENGTH);
    // So is the tag
	memset(packet + payload_len + PACKET_HEADER_LENGTH, 0, PACKET_TAG_LENGTH);

	// TO DO :  replace the two previous command by properly
	//			setting the packet header with the following structure :
	/***************************************************************************
	 *    Field       	Length (bytes)      Encoding        Description
	 ***************************************************************************
	 *  r 					1 								Reserved, set to 0.
	 * 	emitter_id 			1 					BE 			Unique id of the sensor node.
	 *	payload_length 		2 					BE 			Length of app_data (in bytes).
	 *	packet_serial 		4 					BE 			Unique and incrementing id of the packet.
	 *	app_data 			any 							The feature vectors.
	 *	tag 				16 								Message authentication code (MAC).
	 *
	 *	Note : BE refers to Big endian
	 *		 	Use the structure 	packet[x] = y; 	to set a byte of the packet buffer
	 *		 	To perform bit masking of the specific bytes you want to set, you can use
	 *		 		- bitshift operator (>>),
	 *		 		- and operator (&) with hex value, e.g.to perform 0xFF
	 *		 	This will be helpful when setting fields that are on multiple bytes.
	*/

	// For the tag field, you have to calculate the tag. The function call below is correct but
	// tag_cbc_mac function, calculating the tag, is not implemented.
	packet[0] = 0x00;
	packet[1] = sender_id;
	packet[2] = (payload_len >> 8) & 0xFF;
	packet[3] = payload_len & 0xFF;
	packet[4] = (serial >> 24) & 0xFF;
	packet[5] = (serial >> 16) & 0xFF;
	packet[6] = (serial >> 8)  & 0XFF;
	packet[7] = serial & 0xFF;

    tag_cbc_mac(packet + payload_len + PACKET_HEADER_LENGTH, packet, payload_len + PACKET_HEADER_LENGTH);

    return packet_len;
}
