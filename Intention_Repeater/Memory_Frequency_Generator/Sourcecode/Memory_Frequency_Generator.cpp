/*
Memory Frequency Generator by Anthro Teacher (AnthroHeart)
Version 1.4
Created: 4/26/2024
*/

#include <iostream>
#include <cmath>
#include <vector>
#include <thread>
#include <atomic>
#include <complex>
#include <fstream>
#include <cstdint>
#include <algorithm>
#include <cctype>
#include <regex>

const double PI = 3.14159265358979323846;
const std::string VERSION = "v1.4";

void writeWAVFileChunk(const std::string &filename, const std::vector<double> &waveformChunk, double sampleRate, int numChannels, int bitsPerSample)
{
    std::ofstream file(filename, std::ios::binary);
    if (!file)
    {
        std::cerr << "Error: Unable to open file for writing." << std::endl;
        return;
    }

    // Write WAV header
    file.write("RIFF", 4);
    uint32_t fileSize = 44 + waveformChunk.size() * (bitsPerSample / 8);
    file.write(reinterpret_cast<const char *>(&fileSize), 4);
    file.write("WAVE", 4);
    file.write("fmt ", 4);
    uint32_t fmtChunkSize = 16;
    file.write(reinterpret_cast<const char *>(&fmtChunkSize), 4);
    uint16_t audioFormat = 3; // IEEE Float
    file.write(reinterpret_cast<const char *>(&audioFormat), 2);
    uint16_t numChannelsUint16 = static_cast<uint16_t>(numChannels);
    file.write(reinterpret_cast<const char *>(&numChannelsUint16), 2);
    uint32_t sampleRateUint32 = static_cast<uint32_t>(sampleRate);
    file.write(reinterpret_cast<const char *>(&sampleRateUint32), 4);
    uint32_t byteRate = sampleRateUint32 * numChannelsUint16 * (bitsPerSample / 8);
    file.write(reinterpret_cast<const char *>(&byteRate), 4);
    uint16_t blockAlign = numChannelsUint16 * (bitsPerSample / 8);
    file.write(reinterpret_cast<const char *>(&blockAlign), 2);
    uint16_t bitsPerSampleUint16 = static_cast<uint16_t>(bitsPerSample);
    file.write(reinterpret_cast<const char *>(&bitsPerSampleUint16), 2);
    file.write("data", 4);
    uint32_t dataChunkSize = waveformChunk.size() * (bitsPerSample / 8);
    file.write(reinterpret_cast<const char *>(&dataChunkSize), 4);

    // Write waveform data
    for (double sample : waveformChunk)
    {
        float sampleFloat = static_cast<float>(sample);
        file.write(reinterpret_cast<const char *>(&sampleFloat), sizeof(float));
    }
}

void generateSquareWave(std::vector<double> &waveform, double frequency, double sampleRate, int numSamples)
{
    std::vector<double> squareWave(numSamples);
    double timeStep = 1.0 / sampleRate;
    double period = 1.0 / frequency;
    double dutyCycle = 0.5; // 50% duty cycle (square wave)

    for (int i = 0; i < numSamples; i++)
    {
        double time = i * timeStep;
        double value = std::fmod(time, period) < dutyCycle * period ? 1.0 : -1.0;
        waveform[i] = value * 0.9; // scale to [-0.9, 0.9]
    }
}

void generateTriangleWave(std::vector<double> &waveform, double frequency, double sampleRate, int numSamples)
{
    double timeStep = 1.0 / sampleRate;
    double period = 1.0 / frequency;
    double dbToLinear = std::pow(10.0, -8.627 / 20.0); // convert dB to linear scale

    // calculate the mean value of the triangle wave
    double sum = 0.0;
    for (int i = 0; i < numSamples; i++)
    {
        double time = i * timeStep;
        double value = std::fmod(time, period);
        value = 2.0 * (value / period) - 1.0; // scale to [-1, 1]
        value = 4.0 * std::abs(value) - 1.0;  // triangle wave
        sum += dbToLinear * 0.9 * value;
    }
    double meanValue = sum / numSamples;

    // generate the triangle wave with the mean value subtracted
    for (int i = 0; i < numSamples; i++)
    {
        double time = i * timeStep;
        double value = std::fmod(time, period);
        value = 2.0 * (value / period) - 1.0; // scale to [-1, 1]
        value = 4.0 * std::abs(value) - 1.0;  // triangle wave
        waveform[i] = dbToLinear * 0.9 * value - meanValue;
    }
}

// Generate a sine wave
void generateSineWave(std::vector<double> &waveform, double frequency, double sampleRate, int numSamples)
{
    double angularFrequency = 2 * PI * frequency;

    for (int i = 0; i < numSamples; ++i)
    {
        double t = i / sampleRate;
        double value = std::sin(angularFrequency * t) * 0.9;
        waveform[i] = value;
    }
}

int computeSampleRate(double frequency)
{
    int multiplier = 1;
    int sampleRate = frequency;

    while (sampleRate <= 767500 && sampleRate == static_cast<int>(frequency * multiplier))
    {
        multiplier *= 2;
        sampleRate = frequency * multiplier;
    }

    if (sampleRate > 767500)
    {
        sampleRate /= 2;
    }

    return sampleRate;
}

void generateWaveform(std::vector<double> &waveform, double frequency, double sampleRate, int bufferSize, std::atomic<bool> &quit, std::string waveformType)
{
    int index = 0;

    // Convert waveform type to uppercase
    std::transform(waveformType.begin(), waveformType.end(), waveformType.begin(), ::toupper);

    while (!quit)
    {
        if (waveformType == "SQUARE")
        {
            generateSquareWave(waveform, frequency, sampleRate, bufferSize);
        }
        else if (waveformType == "TRIANGLE")
        {
            generateTriangleWave(waveform, frequency, sampleRate, bufferSize);
        }
        else
        {
            generateSineWave(waveform, frequency, sampleRate, bufferSize);
        }

        index = (index + bufferSize) % waveform.size();
    }
}

int main()
{
    std::cout << "Memory Frequency Generator " << VERSION << std::endl;
    std::cout << "by Anthro Teacher (AnthroHeart)" << std::endl
              << std::endl;
    std::string waveformType;
    std::string strFrequency;
    double frequency;
    int bufferSize = 1024 * 1024; // Buffer size for generating waveform
    int numGenerators = 1;        // Default number of generators

    std::cout << "Waveform (Sine, Square, Triangle) [Default: Sine]: ";
    std::getline(std::cin, waveformType);

    if (waveformType == "") {
        waveformType = "Sine";
    }

    while (strFrequency == "") {
        std::cout << "Frequency (Hz): ";
        std::cin >> strFrequency;
        std::cout << std::flush;
    }

    // Remove all but period and numbers from frequency
    std::regex rgx("[^0-9.]");
    std::string frequencyString = std::regex_replace(strFrequency, rgx, "");
    frequency = std::stod(frequencyString);

    std::cout << "Number of Generators (1-255) [Default 1]: ";
    std::cin >> numGenerators;
    //if numGenerators is not a number, set to 1
    if (!std::cin) {
        numGenerators = 1;
    } else {
        numGenerators = std::min(std::max(numGenerators, 1), 255);
    }

    double sampleRate = computeSampleRate(frequency);

    std::vector<std::vector<double>> waveforms(numGenerators, std::vector<double>(bufferSize));
    std::vector<std::thread> threads;
    std::atomic<bool> quit(false);

    std::cout << "Loading Waveforms.." << std::endl;

    for (int i = 0; i < numGenerators; ++i)
    {
        threads.emplace_back(generateWaveform, std::ref(waveforms[i]), frequency, sampleRate, bufferSize, std::ref(quit), waveformType);
    }

    std::cout << "Waveforms are being repeated in memory. Press 'q' and Enter to quit." << std::endl;

    char input;
    while (std::cin >> input)
    {
        if (input == 'q' || input == 'Q')
        {
            quit = true;
            break;
        }
    }

    for (auto &thread : threads)
    {
        thread.join();
    }

    std::cout << "Waveform generation stopped." << std::endl;

    // Write the waveform from the first generator to the WAV file
    std::string fileName = strFrequency + "Hz_" + waveformType + ".wav";
    writeWAVFileChunk(fileName, waveforms[0], sampleRate, 1, 32);
    std::cout << "Waveform written to " << fileName << std::endl;

    return 0;
}