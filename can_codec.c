#include <stdint.h>

// Encode RPM (real-world value) into 2 raw bytes, little-endian
// Formula: raw = value / 0.25  ->  value = raw * 0.25
void encode_rpm(double rpm, uint8_t *byte0, uint8_t *byte1) {
    uint16_t raw = (uint16_t)(rpm / 0.25);
    *byte0 = raw & 0xFF;         // low byte
    *byte1 = (raw >> 8) & 0xFF;  // high byte
}

double decode_rpm(uint8_t byte0, uint8_t byte1) {
    uint16_t raw = (uint16_t)byte0 | ((uint16_t)byte1 << 8);
    return raw * 0.25;
}

// Encode coolant temp into 1 raw byte
// Formula: raw = value -> (-40) = value + 40
uint8_t encode_coolant(double temp_c) {
    return (uint8_t)(temp_c + 40);
}

double decode_coolant(uint8_t raw) {
    return (double)raw - 40;
}
