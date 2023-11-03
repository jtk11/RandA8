import os
import random
import shutil
import psutil
from pydub import AudioSegment
from math import floor
import wave
import numpy as np
import math

F_CLK = 20e6
SAMPLES_PER_PERIOD = 128
MIN_LENGTH_MS = 2000
# Initialize constant variables for presets
sample_start_cv = "1A"
sample_cv_amount = "1.00"
alias = "00"
play_mode = "1"
mix_level = "0.0"
channel_mode = "1"
zones_cv = "1B"

def generate_fourier_wave(num_terms, num_samples, amplitude=1.0):
    t = np.linspace(0, 1, num_samples)
    waveform = np.zeros(num_samples)
    for i in range(1, num_terms + 1):
        frequency = np.random.uniform(1, 10)
        phase = np.random.uniform(0, np.pi * 2)
        coef = np.random.uniform(0.1, 1.0)
        waveform += coef * np.sin(2 * np.pi * frequency * t + phase)
    return amplitude * waveform / np.max(np.abs(waveform))

def calculate_pitch_resolution(F_CLK, sample_rate):
    n = math.floor(F_CLK / sample_rate)
    pitch_resolution = 1200 * math.log((n + 1) / n) / math.log(2)
    return pitch_resolution

def convert_to_mono_and_wav(src, dest):
    segment = AudioSegment.from_file(src)
    mono_segment = segment.set_channels(1)
    mono_segment.export(dest, format="wav")

def pitch_shift_drop_sample(audio_file, F_CLK=20e6, MIN_LENGTH_MS=1000):
    # Randomly choose semitones for pitch shifting
    semitones = random.choice([-16, -26, -38])
    
    # Load the audio segment
    segment = AudioSegment.from_wav(audio_file)

    # Pad audio to meet minimum length requirement
    while len(segment) < MIN_LENGTH_MS:
        segment += segment

    # Oversampling: Double the frame rate
    original_rate = segment.frame_rate
    oversampled = segment.set_frame_rate(original_rate * 2)
    
    # Calculate pitch resolution
    resolution = calculate_pitch_resolution(F_CLK, original_rate)
    
    # Calculate the dynamic clock frequency based on pitch resolution
    dynamic_F_CLK = F_CLK * (2 ** (resolution / 1200))

    # Calculate the desired shifted rate based on semitones
    desired_shifted_rate = oversampled.frame_rate * (2 ** (semitones / 12.0))
    
    # Calculate the divide-by-n value
    n = math.floor(dynamic_F_CLK / desired_shifted_rate)
    
    # Calculate the effective rate for pitch shift
    effective_rate = dynamic_F_CLK / n

    # Perform the pitch shift
    pitched = oversampled._spawn(oversampled.raw_data, overrides={
        "frame_rate": int(effective_rate)
    })
    
    # Restore to original sample rate
    restored = pitched.set_frame_rate(original_rate)
    
    # Export
    restored.export(audio_file, format="wav")


def clean_filename(filename):
    forbidden_chars = '!@#$%^&*()={[}]|\><?;":,_'
    for char in forbidden_chars:
        filename = filename.replace(char, '')
    # Remove any double dots before '.wav'
    filename = filename.replace('..wav', '.wav')
    return filename


# Updated generate_presets function
def generate_presets(dir_path):
    import random
    import yaml
    num_channels = 1  # Mono
    scale_factor = int(5 * (2 ** 31 - 1) / 5.0)  # Scale for CV files
    sample_rate = 96000  # Sample rate for CV files
    num_samples = 96793  # Number of samples for CV files
    output_folder = os.path.join(dir_path, 'random_cv_wave_files_fourier')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize constant variables for presets
    sample_start_cv = "0A"
    sample_cv_amount = "1.00"
    bit_rate = "32"
    alias = "00"
    play_mode = "0"
    loop_mode = "2"
    mix_level = "0.0"
    channel_mode = "1"
    zones_cv = "1B"

    # Read values from existing YAML file
    with open("/Users/macbookpro/Documents/Tools/Assimil8or Tools/prst001.yml", "r") as f:
        existing_data = yaml.safe_load(f)
        phase_cv = existing_data.get("PhaseCV", "0B 1.0000")
        bits_mod = existing_data.get("BitsMod", "0C 1.0000")
        lin_fm = existing_data.get("LinFM", "0A 1.0000")
        release_mod = existing_data.get("ReleaseMod", "0A 1.0000")

    # List to store files
    res = []

    # Iterate directory
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            if path.endswith('.wav'):
                res.append(path)

    random.shuffle(res)
    preset_num = 1

    # Limit presets to 100
    while preset_num <= 100:
        i = 1
        preset_filename = "prst" + "{:03d}".format(preset_num) + ".yml"
        preset_name = "pyPre " + "{:03d}".format(preset_num)

        # Generate a random CV wave file for channel 5
        random_waveform = generate_fourier_wave(5, num_samples)
        random_waveform = np.int32(random_waveform * scale_factor)
        cv_output_path = os.path.join(dir_path, f'fourier_cv_{preset_num}.wav')
        with wave.open(cv_output_path, 'wb') as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(4)  # 4 bytes for int32
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(random_waveform.tobytes())

        with open(os.path.join(dir_path, preset_filename), "w") as cur_file:
            cur_file.write("Preset " + "{:03d}".format(preset_num) + " :"+"\n")
            cur_file.write("  Name : " + preset_name + "\n")

            while i <= 4:  # 4 channels
                random_sample = random.choice(res)
                cur_file.write("  Channel " + str(i) + " :" +"\n")
                cur_file.write("    Bits : " + bit_rate + "\n")
                cur_file.write("    Aliasing : " + alias + "\n")
                cur_file.write("    PlayMode : " + play_mode + "\n")
                cur_file.write("    MixLevel : " + mix_level + "\n")
                cur_file.write("    SampleStartMod : " + sample_start_cv + " " + sample_cv_amount + "\n")
                cur_file.write("    LoopMode : " + loop_mode + "\n")
                cur_file.write("    ZonesCV : " + zones_cv + "\n")
                cur_file.write("    PhaseCV : " + phase_cv + "\n")
                cur_file.write("    BitsMod : " + bits_mod + "\n")
                cur_file.write("    LinFM : " + lin_fm + "\n")
                cur_file.write("    ReleaseMod : " + release_mod + "\n")

                j = 1
                while j <= 8:  # 8 zones
                    random_sample = random.choice(res)
                    cur_file.write("    Zone " + str(j) + " :"+"\n")
                    cur_file.write("      Sample : " + random_sample + "\n")
                    if j < 8:
                        cur_file.write("      MinVoltage : " + str(float(5 - (j * 1.25))) + "\n")
                    j += 1
                i += 1
            cur_file.write("  Channel 5 :"+"\n")
            cur_file.write("    Bits : " + bit_rate +"\n")
            cur_file.write("    Aliasing : " + alias  +"\n")
            cur_file.write("    PlayMode : 1" +"\n")  # Play mode set to 1
            cur_file.write("    MixLevel : " + mix_level  +"\n")
            cur_file.write("    SampleStartMod : " + sample_start_cv + " " + sample_cv_amount +"\n")
            cur_file.write("    LoopMode : 1" +"\n")  # Loop mode set to 2
            cur_file.write("    ZonesCV : " + zones_cv +"\n")
            cur_file.write("    MixLevel : " + "-90.0" + "\n")
            cur_file.write("    PhaseCV : " + phase_cv +"\n")
            cur_file.write("    BitsMod : " + bits_mod +"\n")
            cur_file.write("    LinFM : " + lin_fm  +"\n")
            cur_file.write("    ReleaseMod : " + release_mod +"\n")
            cur_file.write("    Zone 1 :" +"\n")
            cur_file.write("      Sample : " + os.path.basename(cv_output_path) + "\n")

        preset_num += 1
def randomly_copy_wav_files(src_folder, max_size=340 * 1024 * 1024):
    should_pitch_shift = input("Do you want to pitch shift the samples? (yes/no): ").strip().lower() == "yes"

    first_word = os.path.basename(src_folder).split()[0]
    first_word_cleaned = clean_filename(first_word).replace('_', '')  # Remove underscores

    dest_folder_base = os.path.join(os.path.dirname(src_folder), f"{first_word_cleaned}Taste")
    counter = 1
    dest_folder = f"{dest_folder_base}{counter}"  # Removed the underscore

    while os.path.exists(dest_folder):
        counter += 1
        dest_folder = f"{dest_folder_base}{counter}"  # Removed the underscore


    os.makedirs(dest_folder)

    wav_and_aif_files = [f for f in os.listdir(src_folder) if f.endswith(('.wav', '.aif'))]
    random.shuffle(wav_and_aif_files)


    current_size = 0
    
    for file in wav_and_aif_files:
        src_path = os.path.join(src_folder, file)
        file_size = os.path.getsize(src_path)

        if current_size + file_size > max_size:
            break  # Stop copying if adding the next file would exceed the max size


        # Step 1: Convert .aif to .wav in the filename
        file = file.replace(".aif", ".wav")
        
        # Step 2: Remove any existing file extension from the file name
        base_file_name = os.path.splitext(file)[0]

        # Step 3: Clean the filename from forbidden characters
        cleaned_file_name = clean_filename(base_file_name)

        # Step 4: Limit to 43 characters to leave room for ".wav"
        truncated_file_name = cleaned_file_name[:43]
        
        # Step 5: Remove trailing dots to prevent "..wav"
        truncated_file_name = truncated_file_name.rstrip('.')
        
        # Step 6: Add the .wav extension
        final_file_name = truncated_file_name + '.wav'

        dest_path = os.path.join(dest_folder, final_file_name)

        shutil.copy(src_path, dest_path)
        try:
            convert_to_mono_and_wav(dest_path, dest_path)
        except Exception as e:
            print(f"Skipping {dest_path} due to error: {e}")

        if should_pitch_shift:
            pitch_shift_drop_sample(dest_path)

        current_size += os.path.getsize(dest_path)

        ram_usage = psutil.Process(os.getpid()).memory_info().rss // 1024 ** 2
        print(f"Copied {final_file_name} RAM usage: {ram_usage} MB")

    print(f"Copied files to {dest_folder}. Total size: {current_size / (1024 * 1024):.2f} MB")

    generate_presets_choice = input("Would you like to generate 100 presets? (yes/no): ").strip().lower()
    if generate_presets_choice == "yes":
        generate_presets(dest_folder)

if __name__ == "__main__":
    source_folder = "/Users/macbookpro/Documents/Samples/Poke 2 copy_all_audio"
    randomly_copy_wav_files(source_folder)
