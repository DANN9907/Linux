#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

// Define the width and height of the SSD1306 display
#define WIDTH 128
#define HEIGHT 64

// Nearest-neighbor resizing function
void resize_image_nearest_neighbor(uint8_t* input, int input_width, int input_height, uint8_t* output, int output_width, int output_height) {
    for (int y = 0; y < output_height; y++) {
        for (int x = 0; x < output_width; x++) {
            // Calculate the position in the input image
            int nearest_x = (x * input_width) / output_width;
            int nearest_y = (y * input_height) / output_height;

            // Set the output pixel to the nearest input pixel value
            output[y * output_width + x] = input[nearest_y * input_width + nearest_x];
        }
    }
}

// Function to convert any image format to a 1-bit bitmap for the SSD1306 display
void convert_image_to_ssd1306_format(const char* input_filename, const char* output_filename) {
    int width, height, channels;

    // Load the image using stb_image
    uint8_t* image_data = stbi_load(input_filename, &width, &height, &channels, 1); // Load as grayscale
    if (image_data == NULL) {
        printf("Error: Could not load image %s\n", input_filename);
        return;
    }

    // Allocate memory for the resized image
    uint8_t* resized_image = (uint8_t*)malloc(WIDTH * HEIGHT);
    if (resized_image == NULL) {
        printf("Error: Could not allocate memory for the resized image.\n");
        stbi_image_free(image_data);
        return;
    }

    // Resize the image to 128x64 pixels using nearest-neighbor algorithm
    resize_image_nearest_neighbor(image_data, width, height, resized_image, WIDTH, HEIGHT);

    // Free the original image data
    stbi_image_free(image_data);

    // Buffer to store the converted image for SSD1306
    uint8_t oled_buffer[WIDTH * HEIGHT / 8] = {0};

    // Convert the resized grayscale image to 1-bit monochrome
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            int pixel_index = y * WIDTH + x;
            int byte_index = x + (y / 8) * WIDTH;
            int bit_position = y % 8;

            // Threshold the pixel to create a 1-bit monochrome image
            if (resized_image[pixel_index] > 128) { // Simple threshold at mid-range (128)
                oled_buffer[byte_index] |= (1 << bit_position); // Set the bit if pixel is bright
            }
        }
    }

    free(resized_image);

    // Write the converted data to output file
    FILE *output_file = fopen(output_filename, "wb");
    if (output_file == NULL) {
        printf("Error: Could not open output file.\n");
        return;
    }

    fwrite(oled_buffer, sizeof(oled_buffer), 1, output_file);
    fclose(output_file);

    printf("Conversion completed. Data written to %s.\n", output_filename);
}

int main() {
    const char* input_file = "input.png";  // Name of your input file
    const char* output_file = "output.bin"; // Name of the output file

    convert_image_to_ssd1306_format(input_file, output_file);

    return 0;
}